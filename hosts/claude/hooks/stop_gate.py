#!/usr/bin/env python3
"""Stop hook: refuse to end a turn that claims "Final Goal met" while the completion gate is open.

Checks progress_gate.py and that a reviewer subagent was actually spawned (this session's
transcript or the ledger). The first open-gate refusal blocks. `stop_hook_active` does
not release that block. The second consecutive refusal with the same progress.md text,
the same problem list, and the same git state allows the stop. The reason starts with
`NOT complete / blocked:` and says the Final Goal is not met. The hook rewrites the met
claim in progress.md the same way. A change to progress.md or the git state resets the count.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

REVIEW = re.compile(r"(?i)review|interrogat|audit|critic|thermo")


def reviewer_spawned(transcript: str | None, ledger: list[dict]) -> bool:
    if any(e.get("event") == "spawn" and REVIEW.search(f"{e.get('description', '')} {e.get('subagent_type', '')}")
           for e in ledger):
        return True
    if not transcript or not Path(transcript).is_file():
        return False
    for line in Path(transcript).read_text(errors="replace").splitlines():
        if '"Agent"' not in line and '"Task"' not in line:
            continue
        try:
            msg = json.loads(line).get("message", {})
        except ValueError:
            continue
        for c in msg.get("content", []) if isinstance(msg, dict) else []:
            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") in ("Agent", "Task"):
                inp = c.get("input", {})
                if REVIEW.search(f"{inp.get('description', '')} {inp.get('subagent_type', '')}"):
                    return True
    return False


def _consecutive_blocks(ledger: list[dict], key: str) -> int:
    count = 0
    for event in reversed(ledger):
        if event.get("event") != "gate_blocked" or event.get("refusal_key") != key:
            break
        count += 1
    return count


def main() -> int:
    data = common.read_input()
    root = common.project_root(data.get("cwd"))
    if root is None:
        return 0
    progress = root / "progress.md"
    text = progress.read_text(errors="replace")
    gate = common.gate_module()
    if not gate.claims_met(text):
        return 0
    session = data.get("session_id", "")
    ledger = common.events(root)
    problems = gate.check(progress)
    if re.search(r"^pstack: O-interrogate\|", text, re.M) and not reviewer_spawned(data.get("transcript_path"), ledger):
        problems.append("no reviewer subagent was spawned: launch one (Agent tool, run_in_background: false) "
                        "and record what it found")
    if not problems:
        common.append(root, {"event": "gate_ok", "session": session})
        return 0
    key = gate.refusal_key(progress, problems)
    if _consecutive_blocks(ledger, key) + 1 >= gate.STUCK_LIMIT:
        message = gate.stuck_message(problems)
        gate.clear_met_claim(progress, message)
        common.append(root, {"event": "gate_stuck", "session": session, "refusal_key": key, "problems": problems[:10]})
        print(json.dumps({"reason": message}))
        return 0
    common.append(root, {"event": "gate_blocked", "session": session, "refusal_key": key, "problems": problems[:10]})
    reason = ("agentic-sdd completion gate is open, so the Final Goal is not met. "
              "This stop stays blocked while progress.md still claims it is met. "
              "Fix these and rerun scripts/progress_gate.py until it prints ok, or remove the claim "
              "(write `pstack: O-interrogate|<host>|BLOCKED: independent review` when no reviewer can run, "
              "say the Final Goal is not met, and tell the user what is missing):\n- "
              + "\n- ".join(problems[:10]))
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
