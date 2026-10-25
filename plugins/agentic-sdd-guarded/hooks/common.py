"""Shared helpers for the agentic-sdd-guarded hooks: project detection and the local ledger.

The ledger (<project>/.agentic-sdd/ledger.jsonl) holds metadata only: timestamps, session ids,
event names, subagent types and descriptions. It never stores prompts, tool output, or file content.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

# progress.md pins the goal as "## Final Goal", "Final Goal: …" or a status line; any mention marks the project
FINAL_GOAL = re.compile(r"(?i)\bfinal goal\b")


def read_input() -> dict:
    try:
        return json.load(sys.stdin)
    except ValueError:
        return {}


def project_root(cwd: str | None) -> Path | None:
    """The nearest directory at or above cwd whose progress.md pins a Final Goal."""
    if not cwd:
        return None
    here = Path(cwd).resolve()
    for d in (here, *here.parents):
        p = d / "progress.md"
        if p.is_file() and FINAL_GOAL.search(p.read_text(errors="replace")):
            return d
    return None


def ledger_path(root: Path) -> Path:
    return root / ".agentic-sdd" / "ledger.jsonl"


def append(root: Path, event: dict) -> None:
    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps({"ts": round(time.time(), 3), **event}) + "\n")


def events(root: Path) -> list[dict]:
    path = ledger_path(root)
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def gate_module():
    """progress_gate from the plugin's bundled skill, or from the repository checkout."""
    here = Path(__file__).resolve().parent
    for d in (here.parent / "skills" / "agentic-sdd" / "scripts", here.parents[2] / "scripts"):
        if (d / "progress_gate.py").is_file():
            sys.path.insert(0, str(d))
            import progress_gate
            return progress_gate
    raise ImportError("progress_gate.py not found next to the hooks")
