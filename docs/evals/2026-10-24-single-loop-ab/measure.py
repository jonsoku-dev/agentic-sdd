#!/usr/bin/env python3
"""Score single-loop A/B runs from transcripts and shipped files, never from the agent's own summary.

usage: measure.py <sl-root>   (reads <sl-root>/runs/<tag>/ and <sl-root>/out/<tag>.jsonl, prints JSON)
"""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

REVIEW = re.compile(r"review|interrogat|thermos|blast|audit|critic|judge|panel|hygiene|sicko", re.I)
WORK = re.compile(r"implement|\bT\d{3}\b|packet|write code", re.I)


PLACEHOLDER = re.compile(r"\bnoop\b|\bwait\b|reply with|say ok|single word", re.I)


def role(inp):
    typ, desc = inp.get("subagent_type") or "", inp.get("description") or ""
    if len(inp.get("prompt") or "") < 80 or PLACEHOLDER.search(desc):
        return "placeholder"
    if REVIEW.search(desc):
        return "review"
    if "poteto-agent" in typ or WORK.search(desc):
        return "work"
    return "review" if REVIEW.search(f"{desc} {typ}") else "work"


def codex_transcript(path: Path):
    """Codex `exec --json`: count spawn_agent calls and sum turn usage."""
    t = {"spawns": [], "skills": [], "read_single_loop": False, "result": None, "wakeups": 0, "active_ms": 0,
         "segments": 0, "skill_reads": [], "tokens": {}}
    for line in path.read_text(errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "turn.completed":
            t["segments"] += 1
            for k, v in (ev.get("usage") or {}).items():
                t["tokens"][k] = t["tokens"].get(k, 0) + (v or 0)
        it = ev.get("item") or {}
        if ev.get("type") == "item.started" and "spawn" in json.dumps(it):
            blob = json.dumps(it)
            t["spawns"].append({"nested": False, "type": it.get("type"), "desc": blob[:160],
                                "role": "review" if REVIEW.search(blob) else "work", "background": None, "isolation": None})
    sp = t["spawns"]
    t["spawn_counts"] = {"total": len(sp), "parent": len(sp), "work": sum(s["role"] == "work" for s in sp),
                         "review": sum(s["role"] == "review" for s in sp), "placeholder": 0}
    t["result"] = {"total_cost_usd": None}
    return t


def transcript(path: Path):
    t = {"spawns": [], "skills": [], "read_single_loop": False, "result": None, "wakeups": 0, "active_ms": 0, "segments": 0, "skill_reads": set(), "tokens": {}}
    for line in path.read_text(errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "result":
            # -p emits one result per resumed segment; cost is cumulative, duration is per segment
            t["segments"] += 1
            t["active_ms"] += ev.get("duration_ms") or 0
            t["result"] = {k: ev.get(k) for k in ("total_cost_usd", "duration_ms", "num_turns", "is_error", "subtype")}
            u = ev.get("usage") or {}
            for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
                t["tokens"][k] = t["tokens"].get(k, 0) + (u.get(k) or 0)
        if ev.get("type") != "assistant":
            continue
        nested = ev.get("parent_tool_use_id") is not None
        for c in ev.get("message", {}).get("content", []):
            if c.get("type") != "tool_use":
                continue
            inp = c.get("input", {})
            if c["name"] in ("Agent", "Task"):
                t["spawns"].append({"nested": nested, "type": inp.get("subagent_type"), "desc": inp.get("description"),
                                    "role": role(inp),
                                    "background": inp.get("run_in_background"), "isolation": inp.get("isolation")})
            elif c["name"] == "ScheduleWakeup" and not inp.get("stop"):
                t["wakeups"] += 1
            elif c["name"] == "Skill" and not nested:
                t["skills"].append(inp.get("skill"))
            elif c["name"] == "Read" and "single-loop-default" in str(inp.get("file_path", "")):
                t["read_single_loop"] = True
            if not nested and c["name"] in ("Read", "Bash"):
                blob = str(inp.get("file_path", "")) + " " + str(inp.get("command", ""))
                t["skill_reads"].update(re.findall(r"\breferences/[\w.-]+\.md", blob))
    t["skill_reads"] = sorted(t["skill_reads"])
    sp = t["spawns"]
    t["spawn_counts"] = {"total": len(sp), "parent": sum(not s["nested"] for s in sp),
                         "work": sum(s["role"] == "work" for s in sp), "review": sum(s["role"] == "review" for s in sp),
                         "placeholder": sum(s["role"] == "placeholder" for s in sp)}
    return t


def kv_acceptance(repo: Path, store_dir: str):
    """Black-box checks for the kv TTL brief (base2)."""
    import time
    store = os.path.join(store_dir, "kv.json")
    env = dict(os.environ, KV_FILE=store)

    def kv(*a):
        p = subprocess.run(["node", "src/cli.js", *a], cwd=repo, capture_output=True, text=True, env=env, timeout=30)
        return p.returncode, p.stdout.strip(), p.stderr.strip()

    r = {}
    Path(store).write_text(json.dumps({"entries": {"old": {"value": "v"}}}))
    r["legacy_store_reads"] = kv("get", "old")[:2] == (0, "v")
    # 3 s TTL: each node start costs ~0.6 s, and a 1 s TTL expired before the ttl check ran
    kv("set", "short", "1", "--ttl", "3")
    kv("set", "keep", "2")
    rc, out, _ = kv("get", "short")
    r["ttl_key_readable_before_expiry"] = rc == 0 and out == "1"
    rc, out, _ = kv("ttl", "short")
    r["ttl_prints_seconds"] = rc == 0 and out.isdigit() and int(out) <= 3
    rc, _, err = kv("ttl", "keep")
    r["ttl_without_expiry_fails"] = rc == 1 and bool(err)
    rc, _, err = kv("ttl", "missing")
    r["ttl_missing_fails"] = rc == 1 and bool(err)
    time.sleep(3.6)
    rc, _, err = kv("get", "short")
    live = r["ttl_key_readable_before_expiry"]
    r["expired_get_fails"] = live and rc == 1 and bool(err)
    rc, out, _ = kv("list")
    r["expired_absent_from_list"] = live and rc == 0 and "keep" in out.split() and "short" not in out.split() and "old" in out.split()
    return r


def entry(repo: Path):
    for c in [repo / "todo.py", repo / "todo", *repo.glob("src/**/todo.py"), *repo.glob("**/__main__.py")]:
        if c.is_file() and ".specify" not in c.parts and ".claude" not in c.parts:
            return [sys.executable, str(c)] if c.name != "__main__.py" else [sys.executable, "-m", c.parent.name]
    return None


def acceptance(repo: Path, brief: str):
    if brief.startswith("K"):
        with tempfile.TemporaryDirectory() as d:
            return kv_acceptance(repo, store_dir=d)
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
        if brief.startswith("S"):
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
        sh("add", "--priority", "1", "--due", "2000-01-01", "high")
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
        # added after the first scoring pass (disclosed in result.md): the brief does not fix flag position
        sh("add", "late", "--priority", "2")
        out = sh("list")[1]
        r["extra_flags_after_text"] = "late" in out and "--priority" not in out
        return r


def repo_facts(repo: Path):
    f = {}
    cmd = ["npm", "test", "--silent"] if (repo / "package.json").is_file() else [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    p = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=300)
    tail = (p.stdout + p.stderr).strip().splitlines()
    f["tests"] = {"rc": p.returncode, "summary": " ".join(l for l in tail if l.startswith(("Ran ", "OK", "FAILED", "ℹ pass", "ℹ fail", "# pass", "# fail")))}
    f["specs"] = sorted({s.parent.name for s in [*repo.glob("specs/*/spec.md"), *repo.glob(".specify/specs/*/spec.md")]})
    f["converge_files"] = len([*repo.glob("specs/*/converge.md"), *repo.glob(".specify/specs/*/converge.md")])
    prog = repo / "progress.md"
    text = prog.read_text(errors="replace") if prog.is_file() else ""
    lines = [l for l in text.splitlines() if re.match(r"^(pstack|harness|ROUTING|rea):", l)]
    f["breadcrumbs"] = len(lines)
    f["o_poteto"] = [l for l in lines if "O-poteto" in l]
    f["gate_review_line"] = bool(re.search(r"^pstack: O-interrogate\|", text, re.M))
    f["gate_rea_line"] = bool(re.search(r"^rea: [^|\n]+\|pass\|ev_", text, re.M))
    f["breadcrumbs_bulleted"] = len(re.findall(r"^\s*[-*]\s+(?:pstack|harness|ROUTING|rea):", text, re.M))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
    import progress_gate
    f["final_goal_met"] = progress_gate.claims_met(text)
    allmd = "\n".join(p.read_text(errors="replace") for p in repo.rglob("*.md") if not {".claude", ".specify"} & set(p.parts))
    f["rea_evidence_ids"] = sorted(set(re.findall(r"\bev_[0-9a-f]{6,}", allmd)))
    code = [p for p in repo.rglob("*.py") if not {".claude", ".specify", "tests"} & set(p.parts) and not p.name.startswith("test")]
    f["impl_loc"] = sum(len(p.read_text(errors="replace").splitlines()) for p in code)
    f["commits"] = int(subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip() or 0)
    f["worktrees"] = subprocess.run(["git", "worktree", "list"], cwd=repo, capture_output=True, text=True).stdout.count("\n")
    return f


def main(sl: Path, outdir: str = "out"):
    rows = []
    log = sl / outdir / "runs.log"
    wall = dict(re.findall(r"^(\S+) rc=\d+ (\d+)s$", log.read_text(), re.M)) if log.is_file() else {}
    for jl in sorted((sl / outdir).glob("*.jsonl")):
        tag = jl.stem
        parts = tag.split("-")
        host = parts[0] if parts[0] in ("claude", "codex") else "claude"
        v, brief, rep = parts[-3:]
        repo = sl / "runs" / tag
        parse = codex_transcript if host == "codex" else transcript
        row = {"tag": tag, "host": host, "version": v, "brief": brief, "rep": rep, "wall_s": int(wall.get(tag, 0)), **parse(jl)}
        if repo.is_dir():
            row["acceptance"] = acceptance(repo, brief[0])
            row.update(repo_facts(repo))
        rows.append(row)
    print(json.dumps(rows, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]), *sys.argv[2:3])
