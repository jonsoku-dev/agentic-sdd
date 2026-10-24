#!/usr/bin/env python3
"""Judge runs against definition.md (C1-C10). usage: perfect.py <sl-root> <outdir> [baseline.json]

Prints one line per run with failed criteria, then per-cell cost, then PASS or FAIL.
Writes <sl-root>/<outdir>.perfect.json (feed it as baseline.json to a later matrix for C10).
"""
import json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "2026-10-24-single-loop-ab"))
import measure  # noqa: E402

UNSCORED = {"extra_flags_after_text"}


def cell(tag):
    # tag = host-base-version-brief-rep; rep is <model letters><n>, e.g. so1 (sonnet), op2 (opus)
    host, base, _v, brief, rep = tag.split("-")
    return f"{host}/{rep.rstrip('0123456789')}-{base}-{brief}"


def spawned_reviewer(host, jl: Path):
    raw = jl.read_text(errors="replace")
    if host == "claude":
        t = measure.transcript(jl)
        return t["spawn_counts"]["review"] > 0, t
    if host == "codex":
        return '"type": "collab_tool_call"' in raw or '"type":"collab_tool_call"' in raw, None
    return "spawn_subagent" in raw, None


def judge(sl: Path, outdir: str):
    rows = []
    for jl in sorted((sl / outdir).glob("*.jsonl")):
        tag = jl.stem
        host, brief = tag.split("-")[0], tag.split("-")[3]
        repo = sl / "runs" / tag
        fails = []
        acc = {k: v for k, v in measure.acceptance(repo, brief).items() if k not in UNSCORED}
        if not acc or not all(acc.values()):
            fails.append("C1")
        facts = measure.repo_facts(repo)
        if facts["tests"]["rc"] != 0:
            fails.append("C2")
        gate = subprocess.run([sys.executable, str(REPO / "scripts/progress_gate.py"), str(repo / "progress.md")],
                              capture_output=True, text=True).stdout.strip().splitlines()
        gate_ok = bool(gate) and gate[-1] == "ok"
        if not gate_ok:
            fails.append("C3")
        reviewed, t = spawned_reviewer(host, jl)
        if not reviewed:
            fails.append("C4")
        if facts["final_goal_met"] and not gate_ok:
            fails.append("C5")
        tasks = [sum(1 for l in (d / "tasks.md").read_text().splitlines() if re.match(r"^- \[", l))
                 for d in sorted(repo.glob("specs/*/")) if (d / "tasks.md").is_file()]
        if len(tasks) > 1 and sum(tasks) <= 12 or len(tasks) == 0:
            fails.append("C6")
        if any(len(re.findall(r"^##+ .*Convergence", (d / "tasks.md").read_text(), re.M | re.I)) > 1
               for d in repo.glob("specs/*/") if (d / "tasks.md").is_file()):
            fails.append("C7")
        if t and (t["wakeups"] or t["spawn_counts"].get("placeholder")):
            fails.append("C8")
        if facts["worktrees"] > 1:
            fails.append("C9")
        cost = re.findall(r'"total_cost_usd":\s*([0-9.]+)', jl.read_text(errors="replace"))
        rows.append({"tag": tag, "cell": cell(tag), "fails": fails, "cost": float(cost[-1]) if cost else None,
                     "tasks": tasks})
    return rows


def main():
    sl, outdir = Path(sys.argv[1]), sys.argv[2]
    rows = judge(sl, outdir)
    base = {}
    if len(sys.argv) > 3:
        for r in json.loads(Path(sys.argv[3]).read_text()):
            if r["cost"] is not None:
                base.setdefault(r["cell"], []).append(r["cost"])
    cells = {}
    for r in rows:
        cells.setdefault(r["cell"], []).append(r)
    for c, rs in sorted(cells.items()):
        costs = [r["cost"] for r in rs if r["cost"] is not None]
        if costs and c in base:
            limit = 1.15 * sum(base[c]) / len(base[c])
            if sum(costs) / len(costs) > limit:
                for r in rs:
                    r["fails"].append("C10")
    for r in rows:
        print(f"{r['tag']:30} tasks {r['tasks']} cost {r['cost']} {'ok' if not r['fails'] else 'FAIL ' + ','.join(r['fails'])}")
    for c, rs in sorted(cells.items()):
        costs = [r["cost"] for r in rs if r["cost"] is not None]
        print(f"cell {c}: runs {len(rs)} mean cost {sum(costs)/len(costs):.2f}" if costs else f"cell {c}: runs {len(rs)} (no cost)")
    (sl / f"{outdir}.perfect.json").write_text(json.dumps(rows, indent=1))
    bad = [r for r in rows if r["fails"]]
    print("PASS" if not bad else f"FAIL: {len(bad)} of {len(rows)} runs")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
