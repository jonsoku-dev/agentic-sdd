#!/usr/bin/env python3
"""Judge the Tier-2 feature runs from files and transcripts, not from the agent's summary.

For each host sandbox: new numbered spec present, tasks checked, progress.md breadcrumbs
(pstack:/harness:/ROUTING:), converge count, REA Evidence id, tests pass, black-box `edit`
behaviour, commits; from the transcript: subagent dispatches, review skills run, host cost/turns.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

S = Path(os.environ.get("SDD_HM", "<scratchpad>/hm"))  # per-host clones written by tier2.sh
OUT = Path(__file__).resolve().parent / "tier2"
HOSTS = ("claude", "codex", "cursor", "grok")


def sh(cmd, cwd, env=None, timeout=120):
    p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def black_box_edit(arm: Path):
    env = dict(os.environ, TODO_FILE=str(arm / "_m_todo.json"))
    (arm / "_m_todo.json").unlink(missing_ok=True)
    r = {}
    rc, out, _ = sh('./todo add "old text"', arm, env)
    rc, out, err = sh('./todo edit 1 "new text"', arm, env)
    r["edit_ok"] = rc == 0
    rc, out, _ = sh("./todo list", arm, env)
    r["list_shows_new"] = "new text" in out and "old text" not in out
    rc, out, err = sh('./todo edit 99 "x"', arm, env)
    r["unknown_id_fails"] = rc != 0 and bool(err)
    (arm / "_m_todo.json").unlink(missing_ok=True)
    return r


def transcript_facts(host):
    p = OUT / f"{host}.jsonl"
    if not p.is_file():
        return {"transcript": "missing"}
    text = p.read_text(errors="replace")
    f = {"bytes": len(text)}
    f["agent_dispatches"] = len(re.findall(r'"name":\s*"Agent"|spawn_agent|spawn_subagent|"subagent_type"', text))
    f["poteto_agent_mentions"] = len(re.findall(r"poteto-agent", text))
    f["skill_calls"] = sorted(set(re.findall(r'"skill":\s*"([^"]+)"', text)))[:12]
    f["rea_calls"] = len(re.findall(r"capture_process_scenario|capture-process|rea-agents", text))
    for k in ("total_cost_usd", "num_turns", "duration_ms"):
        m = re.findall(rf'"{k}":\s*([0-9.]+)', text)
        if m:
            f[k] = m[-1]
    f["errors"] = len(re.findall(r'"is_error":\s*true|"type":\s*"error"', text))
    return f


def main():
    for host in HOSTS:
        arm = S / host
        m = {"host": host}
        specs = sorted(p.name for p in (arm / "specs").iterdir()) if (arm / "specs").is_dir() else []
        m["specs"] = specs
        new = [s for s in specs if not s.startswith("001")]
        m["new_spec_files"] = sorted(p.name for p in (arm / "specs" / new[0]).iterdir()) if new else []
        tasks = (arm / "specs" / new[0] / "tasks.md").read_text() if new and (arm / "specs" / new[0] / "tasks.md").is_file() else ""
        m["tasks_total"] = len(re.findall(r"^- \[[ xX]\] T\d+", tasks, re.M))
        m["tasks_done"] = len(re.findall(r"^- \[[xX]\] T\d+", tasks, re.M))
        m["converge_files"] = len(list(arm.glob("specs/*/converge*.md")))
        prog = (arm / "progress.md").read_text() if (arm / "progress.md").is_file() else ""
        base = Path("<scratchpad>/sdd-ab/B/progress.md").read_text()
        added = [l for l in prog.splitlines() if l.strip() and l not in base]
        m["progress_new_lines"] = len(added)
        m["breadcrumbs_new"] = [l[:110] for l in added if re.match(r"^(pstack|harness|ROUTING|rea):", l.strip(), re.I)]
        m["converge_mentions"] = len(re.findall(r"converge", prog, re.I))
        m["evidence_ids"] = sorted(set(re.findall(r"ev_[0-9a-f]{64}", prog + "\n".join((arm / "specs" / s / f).read_text() for s in new for f in m["new_spec_files"] if (arm / "specs" / s / f).is_file()))))
        m["final_goal_met"] = bool(re.search(r"final goal.*(met|complete|achieved|closed)", prog, re.I))
        rc, out, err = sh("python3 -m unittest discover -s tests 2>&1 | tail -1", arm)
        m["tests"] = out.splitlines()[-1] if out else err[-80:]
        m["black_box"] = black_box_edit(arm) if (arm / "todo").is_file() else "no todo"
        # commits the run added on top of the shared base (3ff57a9), ignoring the Cursor rule commit
        rc, out, _ = sh("git log --format=%s 3ff57a9..HEAD | grep -v -c 'chore: add Cursor agentic-sdd rule'", arm)
        m["commits"] = int(out or 0)
        rc, out, _ = sh("git status --short | wc -l", arm)
        m["dirty_files"] = int(out or 0)
        m["transcript"] = transcript_facts(host)
        print(json.dumps(m, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
