#!/usr/bin/env python3
"""Score single-loop A/B runs from transcripts and shipped files, never from the agent's own summary.

usage: measure.py <sl-root>   (reads <sl-root>/runs/<tag>/ and <sl-root>/out/<tag>.jsonl, prints JSON)
"""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

REVIEW = re.compile(r"review|interrogat|thermos|blast|audit|critic|verify|judge|panel", re.I)


def transcript(path: Path):
    t = {"spawns": [], "skills": [], "read_single_loop": False, "result": None}
    for line in path.read_text(errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "result":
            t["result"] = {k: ev.get(k) for k in ("total_cost_usd", "duration_ms", "num_turns", "is_error", "subtype")}
            u = ev.get("usage") or {}
            t["result"]["tokens"] = {k: u.get(k) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}
        if ev.get("type") != "assistant":
            continue
        nested = ev.get("parent_tool_use_id") is not None
        for c in ev.get("message", {}).get("content", []):
            if c.get("type") != "tool_use":
                continue
            inp = c.get("input", {})
            if c["name"] in ("Agent", "Task"):
                desc = f"{inp.get('description', '')} {inp.get('subagent_type', '')}"
                t["spawns"].append({"nested": nested, "type": inp.get("subagent_type"), "desc": inp.get("description"),
                                    "role": "review" if REVIEW.search(desc) else "work",
                                    "background": inp.get("run_in_background"), "isolation": inp.get("isolation")})
            elif c["name"] == "Skill" and not nested:
                t["skills"].append(inp.get("skill"))
            elif c["name"] == "Read" and "single-loop-default" in str(inp.get("file_path", "")):
                t["read_single_loop"] = True
    sp = t["spawns"]
    t["spawn_counts"] = {"total": len(sp), "parent": sum(not s["nested"] for s in sp),
                         "work": sum(s["role"] == "work" for s in sp), "review": sum(s["role"] == "review" for s in sp)}
    return t


def entry(repo: Path):
    for c in [repo / "todo.py", repo / "todo", *repo.glob("src/**/todo.py"), *repo.glob("**/__main__.py")]:
        if c.is_file() and ".specify" not in c.parts and ".claude" not in c.parts:
            return [sys.executable, str(c)] if c.name != "__main__.py" else [sys.executable, "-m", c.parent.name]
    return None


def acceptance(repo: Path, brief: str):
    cmd = entry(repo)
    if not cmd:
        return {"entry": None}
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "t.json")
        env = dict(os.environ, TODO_FILE=store)

        def sh(*a):
            p = subprocess.run([*cmd, *a], cwd=repo, capture_output=True, text=True, env=env, timeout=30)
            return p.returncode, p.stdout, p.stderr

        r = {}
        if brief == "S":
            sh("add", "alpha")
            rc, _, _ = sh("edit", "1", "beta")
            out = sh("list")[1]
            r["edit_replaces"] = rc == 0 and "beta" in out and "alpha" not in out
            rc, _, err = sh("edit", "99", "x")
            r["edit_unknown_fails"] = rc != 0 and bool(err.strip()) and "unknown command" not in err
            return r
        # L: migration first, from the base version's exact store shape
        Path(store).write_text(json.dumps({"next_id": 2, "items": [{"id": 1, "text": "legacy", "done": False}]}))
        rc, out, _ = sh("list")
        r["migration_reads_old"] = rc == 0 and "legacy" in out
        # insertion order is the reverse of every expected sort order
        sh("add", "--due", "2999-12-31", "future")
        sh("add", "--priority", "3", "low")
        sh("add", "--priority", "1", "high", "--due", "2000-01-01")
        rc, out, _ = sh("list")
        r["migration_keeps_old"] = "legacy" in out
        r["flags_parsed"] = rc == 0 and "high" in out and "--" not in out
        if not r["flags_parsed"]:
            return r
        hi = next((l for l in out.splitlines() if "high" in l), "")
        rest = hi.split(None, 1)[1] if len(hi.split(None, 1)) > 1 else ""
        r["priority_shown"] = bool(re.search(r"(?i)\bp?1\b|priority[: =]*1|\[1\]|!", rest))
        rc, out, _ = sh("list", "--sort", "priority")
        r["sort_priority"] = rc == 0 and "high" in out and "low" in out and out.index("high") < out.index("low")
        rc, out, _ = sh("list", "--sort", "due")
        r["sort_due"] = rc == 0 and "high" in out and "future" in out and out.index("high") < out.index("future")
        rc, out, _ = sh("list", "--overdue")
        r["overdue_only"] = rc == 0 and "high" in out and "future" not in out and "low" not in out
        rc, _, _ = sh("add", "--priority", "9", "bad")
        r["priority_invalid_rejected"] = rc != 0
        return r


def repo_facts(repo: Path):
    f = {}
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=repo,
                       capture_output=True, text=True, timeout=300)
    tail = (p.stdout + p.stderr).strip().splitlines()
    f["tests"] = {"rc": p.returncode, "summary": " ".join(l for l in tail if l.startswith(("Ran ", "OK", "FAILED")))}
    f["specs"] = sorted({s.parent.name for s in [*repo.glob("specs/*/spec.md"), *repo.glob(".specify/specs/*/spec.md")]})
    f["converge_files"] = len([*repo.glob("specs/*/converge.md"), *repo.glob(".specify/specs/*/converge.md")])
    prog = repo / "progress.md"
    text = prog.read_text(errors="replace") if prog.is_file() else ""
    lines = [l for l in text.splitlines() if re.match(r"^(pstack|harness|ROUTING|rea):", l)]
    f["breadcrumbs"] = len(lines)
    f["o_poteto"] = [l for l in lines if "O-poteto" in l]
    f["final_goal_met"] = bool(re.search(r"(?i)final goal[^\n]*\b(met|complete|done)\b", text))
    allmd = "\n".join(p.read_text(errors="replace") for p in repo.rglob("*.md") if not {".claude", ".specify"} & set(p.parts))
    f["rea_evidence_ids"] = sorted(set(re.findall(r"\bev_[0-9a-f]{6,}", allmd)))
    code = [p for p in repo.rglob("*.py") if not {".claude", ".specify", "tests"} & set(p.parts) and not p.name.startswith("test")]
    f["impl_loc"] = sum(len(p.read_text(errors="replace").splitlines()) for p in code)
    f["commits"] = int(subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip() or 0)
    f["worktrees"] = subprocess.run(["git", "worktree", "list"], cwd=repo, capture_output=True, text=True).stdout.count("\n")
    return f


def main(sl: Path):
    rows = []
    for jl in sorted((sl / "out").glob("*.jsonl")):
        tag = jl.stem
        v, brief, rep = tag.split("-")
        repo = sl / "runs" / tag
        row = {"tag": tag, "version": v, "brief": brief, "rep": rep, **transcript(jl)}
        if repo.is_dir():
            row["acceptance"] = acceptance(repo, brief)
            row.update(repo_facts(repo))
        rows.append(row)
    print(json.dumps(rows, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
