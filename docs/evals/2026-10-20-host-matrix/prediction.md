# Host matrix: does agentic-sdd + pstack + the seven layers fire correctly on every host?

Written before any run. Judged from transcripts and files, never from the agent's own summary.

## Setup

- Base project: the `001-todo-cli` sandbox from `2026-10-19-sandbox-ab` (Spec Kit 1.0.1, feature 001 closed, `.agents/playbooks/agentic-sdd.md` installed, `progress.md` with breadcrumbs). One clone per host under the scratchpad `hm/<host>/`.
- Hosts and headless drivers: Claude Code `claude -p --output-format stream-json`, Codex `codex exec --json -m gpt-6-luna`, Cursor `agent -p --output-format stream-json --force`, Grok `grok -p --always-approve --output-format json`.
- Entry directions tested: (a) explicit `/agentic-sdd` style request, (b) a plain request in a Spec Kit repo that the pstack mandate should route through poteto-mode and the project playbook.

## Tiers

| Tier | What | Cost | Pass condition |
|---|---|---|---|
| 0 static | `harness_probe.py` per host; `check-playbooks.mjs` on the port; Cursor plugin playbook text vs the port | none | probe L2/L3/L5/L6 ok on all hosts; port validates; Cursor divergence documented |
| 1 routing | four "plan only, name the skills you would run, then stop" prompts per host: T (typo), F (multi-file feature), B (unknown bug), D (design question) | small | T: no poteto-mode, no agentic-sdd. F: agentic-sdd + Spec Kit phase named + poteto Feature steps. B: bug workflow + `how`/`why`. D: investigation/`how`/`architect`, no implement |
| 2 feature | one real small feature (`todo edit`) end to end on each host that can run unattended | moderate | files: new `specs/002-*`, `progress.md` gains `pstack:`/`harness:`/`ROUTING:` lines, one converge, REA Evidence id; transcript: poteto agent dispatch, review skill run |
| 3 split | Claude only: a change sized to exceed ~12 tasks (priorities + due dates + filter + store migration) | high | `closed-carryover` recorded and a smaller next spec specified, no second converge |

## Predictions

1. Tier 0: all four hosts L2 ok. Cursor's official plugin (0.15.28) has no project-playbook support and marks poteto-mode `disable-model-invocation: true`, so on Cursor the handoff relies on the agentic-sdd skill text, not the playbook.
2. Tier 1 T: every host answers without naming poteto-mode or agentic-sdd. Risk: Claude over-invokes because the mandate is injected every session.
3. Tier 1 F: Claude, Codex, Grok name agentic-sdd and the Spec Kit `specify` phase. Cursor names poteto-mode Feature steps but may miss the Spec Kit handoff unless it opens the agentic-sdd skill.
4. Tier 1 B: all hosts name a reproduce-first bug flow; Claude and Codex name `how`/`why`.
5. Tier 2: Claude completes with Evidence. Codex completes if `spawn_agent` is given `gpt-6-luna`. Grok completes with `poteto-agent`. Cursor may stop at a question or skip REA.
6. Tier 3: Claude records carryover rather than reconverging.
