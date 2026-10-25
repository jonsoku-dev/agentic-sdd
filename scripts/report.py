#!/usr/bin/env python3
"""Write a dated tracking report for an agentic-sdd project and print its path.

usage: report.py [--project DIR] [--stdout]
Writes <project>/.agentic-sdd/reports/<UTC stamp>.md plus a .json twin; the next report
compares against the newest twin. Reports are meant to be committed so progress can be tracked.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sdd_status  # noqa: E402


def totals(snap: dict) -> dict:
    t = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    for s in snap["sessions"]:
        for part in ("tokens", "subagent_tokens"):
            for k in t:
                t[k] += s[part][k]
    return t


def summary(snap: dict) -> dict:
    feats = snap["features"]
    return {
        "gate_ok": snap["gate"]["ok"],
        "final_goal_claimed": snap["final_goal_claimed"],
        "features_closed": sum(f["phase"] == "closed" for f in feats),
        "features": len(feats),
        "tasks_done": sum(f["tasks_done"] for f in feats),
        "tasks_total": sum(f["tasks_total"] for f in feats),
        "spawns": sum(e.get("event") == "spawn" for e in snap["ledger"]),
        "gate_blocks": sum(e.get("event") == "gate_blocked" for e in snap["ledger"]),
        "sessions": len(snap["sessions"]),
        "tokens": totals(snap),
    }


def delta(now: dict, before: dict | None) -> list[str]:
    if not before:
        return ["first report"]
    out = []
    for k in ("features_closed", "tasks_done", "spawns", "gate_blocks", "sessions"):
        if now[k] != before.get(k):
            out.append(f"{k}: {before.get(k)} → {now[k]}")
    if now["gate_ok"] != before.get("gate_ok"):
        out.append(f"gate: {'ok' if before.get('gate_ok') else 'open'} → {'ok' if now['gate_ok'] else 'open'}")
    for k, v in now["tokens"].items():
        prev = before.get("tokens", {}).get(k, 0)
        if v != prev:
            out.append(f"tokens.{k}: {prev:,} → {v:,}")
    return out or ["no change"]


def render(snap: dict, s: dict, changes: list[str]) -> str:
    t = s["tokens"]
    lines = [
        f"# agentic-sdd report — {snap['generated']}",
        "",
        f"Project: `{snap['project']}`",
        "",
        "## Summary",
        "",
        f"- Gate: **{'ok' if s['gate_ok'] else 'open'}**; Final Goal claimed: {'yes' if s['final_goal_claimed'] else 'no'}",
        f"- Features closed: {s['features_closed']} / {s['features']}; tasks done: {s['tasks_done']} / {s['tasks_total']}",
        f"- Subagent spawns logged: {s['spawns']}; gate blocks: {s['gate_blocks']}; Claude sessions: {s['sessions']}",
        f"- Tokens: input {t['input']:,}, output {t['output']:,}, cache read {t['cache_read']:,}, cache write {t['cache_write']:,}",
        "",
        "## Since the last report",
        "",
        *[f"- {c}" for c in changes],
        "",
        "## Features",
        "",
        "| Feature | Phase | Tasks | REA |",
        "|---|---|---|---|",
        *[f"| {f['name']} | {f['phase']} | {f['tasks_done']}/{f['tasks_total']} | "
          f"{(f['rea'] or {}).get('disposition', '—')} {(f['rea'] or {}).get('evidence', '')[:16]} |" for f in snap["features"]],
        "",
        "## Gate",
        "",
        *([f"- {p}" for p in snap["gate"]["problems"]] or ["- ok"]),
        "",
        "## Breadcrumbs",
        "",
        *([f"- `{b['kind']}: {b['text'][:140]}`" for b in snap["breadcrumbs"]] or ["- none"]),
        "",
        "## Sessions",
        "",
        "| Session | Start | Turns | Output tokens | Subagents |",
        "|---|---|---|---|---|",
        *[f"| {x['id'][:8]} | {x['start'] or '—'} | {x['turns']} | {x['tokens']['output']:,} | {x['subagents']} |"
          for x in snap["sessions"]],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", default=".")
    ap.add_argument("--stdout", action="store_true", help="print the report instead of writing it")
    args = ap.parse_args()
    project = Path(args.project).resolve()
    snap = sdd_status.snapshot(project)
    s = summary(snap)
    rdir = project / ".agentic-sdd" / "reports"
    prev = sorted(rdir.glob("*.json"))
    before = json.loads(prev[-1].read_text()).get("summary") if prev else None
    text = render(snap, s, delta(s, before))
    if args.stdout:
        print(text)
        return 0
    rdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (rdir / f"{stamp}.md").write_text(text)
    (rdir / f"{stamp}.json").write_text(json.dumps({"summary": s, "features": snap["features"]}, indent=1))
    print(rdir / f"{stamp}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
