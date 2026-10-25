---
description: Optional Kanban view over Spec Kit feature and bug artifacts.
---

# Kanban Board

## Purpose

Visual progress over existing Spec Kit artifacts — no separate board file.

Reads:

- `specs/*/spec.md` and/or `.specify/specs/*/spec.md`
- sibling `tasks.md` for feature column movement
- `.specify/bugs/*/` for bug columns
- root `progress.md` Overall line

## Columns

### Features

- **Specified** — spec exists, no checked tasks
- **In Progress** — some tasks checked
- **Done** — all tasks checked

### Bugs

- **Assessed** — `assessment.md` exists
- **Fixed** — fix applied
- **Verified** / **Failed** — from `test.md`

## How agents update

Update normal Spec Kit artifacts (`tasks.md`, bug stage files, `progress.md`).
Do not maintain a parallel board document unless the user wants a text fallback.

## Running the visualizer

The skill is usually installed outside the project. Always pass the project root:

```bash
python ~/.agents/skills/agentic-sdd/visualizer/server.py --project /path/to/repo
```

Or:

```bash
export AGENTIC_SDD_PROJECT=/path/to/repo
python ~/.agents/skills/agentic-sdd/visualizer/server.py
```

Open http://127.0.0.1:8765

Works the same from Claude Code, Codex, Cursor, and Grok Build terminals.

## Lightweight alternative (no server)

In `progress.md`:

```markdown
## Board
- Specified: 001-auth
- In Progress: 002-export
- Done: 000-overview
- Bugs: login-crash (assessed)
```
