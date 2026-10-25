#!/usr/bin/env python3
"""PostToolUse hook (Agent|Task), async: record each subagent spawn in the local ledger.

Metadata only: subagent type, description, background flag. Never the prompt or the result.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def main() -> int:
    data = common.read_input()
    root = common.project_root(data.get("cwd"))
    if root is None:
        return 0
    inp = data.get("tool_input") or {}
    common.append(root, {"event": "spawn", "session": data.get("session_id", ""),
                         "subagent_type": inp.get("subagent_type"), "description": inp.get("description"),
                         "background": bool(inp.get("run_in_background"))})
    return 0


if __name__ == "__main__":
    sys.exit(main())
