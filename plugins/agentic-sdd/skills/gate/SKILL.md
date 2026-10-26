---
name: gate
description: Check the agentic-sdd completion gate for the current project. progress_gate.py is the only completion predicate (review line, rea pass or not-applicable per in-scope feature, historical specs only via gate: exclude). Use before writing "Final Goal met", or when asked whether a feature or the Final Goal is really done.
---

Run `agentic-sdd-gate progress.md` from the project root (Claude Code puts the plugin's `bin/` on PATH).
Where that command is missing (Codex), run `python3 <this skill's folder>/../agentic-sdd/scripts/progress_gate.py progress.md`.

- `ok` → the gate holds.
- Anything else → fix each printed line in `progress.md` or in the work it points at, then run it again.
  Do not write "Final Goal met" until it prints `ok`.
