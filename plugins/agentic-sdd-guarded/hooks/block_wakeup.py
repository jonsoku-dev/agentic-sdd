#!/usr/bin/env python3
"""PreToolUse hook (ScheduleWakeup): in an agentic-sdd project, deny parking the run behind a wakeup.

A wakeup used as a "fallback heartbeat" kept a headless session alive ~20 minutes after its work
finished (docs/evals/2026-10-25-perfect/result.md).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def main() -> int:
    data = common.read_input()
    root = common.project_root(data.get("cwd"))
    if root is None:
        return 0
    common.append(root, {"event": "wakeup_denied", "session": data.get("session_id", "")})
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": ("agentic-sdd: do not schedule a wakeup. Run reviewers and leaves in the "
                                     "foreground; to wait for a background agent, end the turn and let its "
                                     "completion notice resume you."),
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
