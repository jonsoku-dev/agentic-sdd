#!/usr/bin/env python3
"""One read-only snapshot of an agentic-sdd project, shared by the dashboard and report.py.

usage: sdd_status.py [--project DIR]   (prints the snapshot as JSON)

Sources, all local: specs/*/ (or .specify/specs/*/) artifacts, progress.md, the hooks ledger at
.agentic-sdd/ledger.jsonl when the guarded plugin wrote one, and Claude Code transcripts under
~/.claude/projects/<encoded project path>/ for token use. Nothing is sent anywhere.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import progress_gate  # noqa: E402

PHASES = ["specify", "plan", "tasks", "implement", "converge", "rea"]
CRUMB = re.compile(r"^(pstack|harness|ROUTING|rea):\s*(.*)$")


def feature_dirs(project: Path) -> list[Path]:
    return sorted(d for d in [*project.glob("specs/*/"), *project.glob(".specify/specs/*/")] if d.is_dir())


def feature(d: Path, progress_text: str) -> dict:
    tasks_md = d / "tasks.md"
    lines = tasks_md.read_text(errors="replace").splitlines() if tasks_md.is_file() else []
    boxes = [l for l in lines if re.match(r"^\s*- \[[ xX]\]", l)]
    done = sum(1 for l in boxes if re.match(r"^\s*- \[[xX]\]", l))
    converged = (d / "converge.md").is_file() or any(re.match(r"^##+ .*Convergence", l, re.I) for l in lines)
    rea = re.search(rf"^rea: {re.escape(d.name)}\|(\w[\w-]*)\|(\S+)", progress_text, re.M)
    reached = {
        "specify": (d / "spec.md").is_file(),
        "plan": (d / "plan.md").is_file(),
        "tasks": bool(boxes),
        "implement": bool(boxes) and done == len(boxes),
        "converge": converged,
        "rea": bool(rea and rea.group(1) in {"pass", "not-applicable"}),
    }
    phase = next((p for p in PHASES if not reached[p]), "closed")
    return {"name": d.name, "tasks_done": done, "tasks_total": len(boxes), "phase": phase,
            "phases": reached, "rea": {"disposition": rea.group(1), "evidence": rea.group(2)} if rea else None}


def encoded(project: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(project.resolve()))


def sessions(project: Path, claude_home: Path) -> list[dict]:
    """Token use per Claude Code session for this project; usage is counted once per message id."""
    tdir = claude_home / "projects" / encoded(project)
    out = []
    for jl in sorted(tdir.glob("*.jsonl")) if tdir.is_dir() else []:
        out.append(_session(jl, sub=sorted((tdir / jl.stem / "subagents").glob("*.jsonl"))))
    return sorted(out, key=lambda s: s["start"] or "")


def _usage(paths: list[Path]) -> tuple[dict, set, str | None, str | None, int]:
    tot = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    seen, models, first, last, turns = set(), set(), None, None, 0
    for p in paths:
        for line in p.read_text(errors="replace").splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            ts = e.get("timestamp")
            if ts:
                first = first or ts
                last = ts
            msg = e.get("message") if isinstance(e.get("message"), dict) else {}
            u = msg.get("usage")
            if e.get("type") != "assistant" or not u or msg.get("id") in seen:
                continue
            seen.add(msg.get("id"))
            turns += 1
            models.add(msg.get("model", "?"))
            tot["input"] += u.get("input_tokens", 0) or 0
            tot["output"] += u.get("output_tokens", 0) or 0
            tot["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
            tot["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
    return tot, models, first, last, turns


def _session(jl: Path, sub: list[Path]) -> dict:
    main, models, first, last, turns = _usage([jl])
    subs, smodels, *_ = _usage(sub)
    return {"id": jl.stem, "start": first, "end": last, "turns": turns, "models": sorted(models | smodels),
            "tokens": main, "subagent_tokens": subs, "subagents": len(sub)}


def ledger(project: Path) -> list[dict]:
    path = project / ".agentic-sdd" / "ledger.jsonl"
    rows = []
    for line in path.read_text(errors="replace").splitlines() if path.is_file() else []:
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def snapshot(project: Path, claude_home: Path | None = None) -> dict:
    project = project.resolve()
    progress = project / "progress.md"
    text = progress.read_text(errors="replace") if progress.is_file() else ""
    gate = progress_gate.check(progress) if progress.is_file() else ["no progress.md"]
    crumbs = [{"line": n, "kind": m.group(1), "text": m.group(2)}
              for n, l in enumerate(text.splitlines(), 1) if (m := CRUMB.match(l))]
    return {
        "project": str(project),
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "final_goal_claimed": progress_gate.claims_met(text),
        "gate": {"ok": not gate, "problems": gate},
        "features": [feature(d, text) for d in feature_dirs(project)],
        "breadcrumbs": crumbs,
        "ledger": ledger(project),
        "sessions": sessions(project, claude_home or Path.home() / ".claude"),
        "reports": sorted(p.name for p in (project / ".agentic-sdd" / "reports").glob("*.md")),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", default=".")
    print(json.dumps(snapshot(Path(ap.parse_args().project)), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
