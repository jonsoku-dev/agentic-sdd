# progress.md

## Final Goal
Add `todo edit <id> <new text>` to this repository's todo CLI. The command replaces that item's text. An unknown id exits non-zero and writes a message to stderr. Tests cover both cases. Deliver it as numbered Spec Kit feature 002 in Economy cost mode: specify, plan, tasks, implement, converge once, then REA closeout. Commit as you go. Stop when this file states the Final Goal is met.

**The Final Goal is met.** Feature `002-todo-edit` is closed. `todo edit <id> <new text>` replaces the item text. An unknown id exits non-zero with `todo: no item with id <id>` on stderr. Tests cover both (`test_edit_replaces_text`, `test_edit_unknown_id`). Converge ran once and appended no tasks. REA closeout disposition is `pass`. Evidence ID `ev_145d76d8f47e5b3cac7bc28995579ee7bb2cc2abcdf11438a9235adc2f280787`, bound to `todo` at 0042d0e. No admitted work remains.

## Breadcrumbs
pstack: 0.9.93|grok
harness: L1 gap|L2 ok|L3 ok|L4 ok|L5 ok|L6 ok|L7 ok
harness: L1 gap left (no project AGENTS.md or CLAUDE.md). Outside this Final Goal. Probe: `python3 ~/.grok/skills/agentic-sdd/scripts/harness_probe.py --host grok --project .`
pstack: hook-mandate → satisfied by O-poteto
pstack: O-sharpen|grok|sharpen → Final Goal + AC pinned below. Expert check is the real `todo` process, same shape as `todo done` failures.
cost-mode: Economy
ROUTING: parent=grok-4.7 (unchanged); sheet absent -> pstack defaults; Economy leaves = 1 worker leaf
pstack: O-specify|grok|technical-writing + unslop → specs/002-todo-edit/spec.md. Assumptions are assumptions. No NEEDS CLARIFICATION markers.
pstack: O-how|grok|poteto-agent explainer 01a1560d → plan.md §Context cites todo:40-76, todo:63-68, tests/test_todo.py:46-52
pstack: O-architect|grok|poteto-agent x2 (model unpinned, observed unknown) → A base (/tmp/arch-a/candidate.md), B rejected as a rewrite of add/done (/tmp/arch-b/candidate.md). plan.md §Design
pstack: O-sequence|grok|principle-sequence-verifiable-units → specs/002-todo-edit/tasks.md, 5 tasks, each ends in a check. Commit follows this line.
pstack: O-poteto|grok|poteto-agent worktree 01a15617 → T002-T004. Parent copied the diff, pinned exact unknown-id stderr, verified suite.
Checklist gate before implement: requirements.md 16/16 checked, PASS. .gitignore already ignores todo.json and __pycache__. No Docker, eslint, or npm project. Ignore file left as it was.
pstack: O-blast|grok|blast-radius → safety fact at level 4. Unknown edit does not write. test_edit_unknown_id keeps bytes. Missing file: `TODO_FILE=/tmp/todo-edit-missing.json ./todo edit 1 x` exit 1, file not created. Done item edit stays hidden: list byte count 0, stored text "new", done true.
pstack: O-interrogate|grok|2 reviewers (no new spawn this turn) → A <session-id> no findings; B <session-id> no findings.
pstack: O-converge|grok|speckit-converge → specs/002-todo-edit/converge.md. Outcome converged. tasks.md unchanged. Suite `Ran 17 tests in 1.205s` `OK` at 0042d0e.
pstack: O-rea|grok|capture_process_scenario → Evidence `ev_145d76d8f47e5b3cac7bc28995579ee7bb2cc2abcdf11438a9235adc2f280787`. Bundle `/tmp/rea-todo-002/evidence.json` (20994 bytes). `close_binary` returned `target_unavailable` (no native target). Disposition pass.
decision-log: decisions.tsv (local, untracked)

## Acceptance (pinned)
- AC-E1 `todo edit <id> <new text>` replaces that item's text. Id, done state, and order stay. Exit 0. Stdout empty.
- AC-E2 unknown id exits non-zero with a stderr message and does not change the saved list
- AC-E3 tests cover AC-E1 and AC-E2 by running the real command
- AC-E4 existing add, list, and done checks still pass (`python3 -m unittest discover -s tests -v` from the repo root)
- Non-goals: delete, priorities, bulk edit, id renumbering, storage-format changes

## Decisions (defaults, no human quiz)
- Host is Grok Build. No native Spec Kit key. Phase commands are the project skills under `.claude/skills/speckit-*`, executed against `specs/`.
- Numbered feature `specs/002-todo-edit`. Feature 001 stays closed.
- Stay on `main`. No `before_specify` hook, and feature 001 landed on `main`.
- Success is silent (exit 0, empty stdout), matching `todo done`.
- Edit changes text only, including items that are already done.
- Unknown id matches the `todo done` failure: non-zero, stderr names the id, store not written.
- Non-integer id is a usage error, same as `todo done`.
- Empty text is a valid replacement.
- Constitution is still the unfilled template. Feature 001 constraints plus this Final Goal govern.
- Test command: `python3 -m unittest discover -s tests -v`
- Cost mode Economy: skip architect only if the spec stays single-file. This spec touches `todo` and `tests/test_todo.py`, so architect still runs, kept small. Interrogate panel is 2 reviewers from different families. One implement leaf.

## Outputs
- specs/002-todo-edit/spec.md
- specs/002-todo-edit/checklists/requirements.md
- specs/002-todo-edit/plan.md, research.md, data-model.md, quickstart.md, contracts/cli.md
- .specify/feature.json → specs/002-todo-edit (gitignored, local pointer)

## Completed
- specify: checklist iteration 1 passed (no clarification markers). Commit b8fc9d3.
- plan: design artifacts written. Synthesis is candidate A. Commit 5e0b71c.
- tasks: T001-T005 in specs/002-todo-edit/tasks.md. Commit 84952b6.
- implement: T001 baseline `Ran 15 tests in 1.051s` `OK`. T002-T004 in worktree, parent re-ran `Ran 17 tests in 1.168s` `OK`. `wc -l todo` = 89. Quickstart: add prints 1, edit prints nothing exit 0, list prints `1 buy oat milk`, edit 99 prints `todo: no item with id 99` exit 1.
- converge (once): no findings. tasks.md unchanged. Re-check `Ran 17 tests in 1.205s` `OK` at 0042d0e. `wc -l todo` = 89. Commit 21c4749.
- REA closeout: pass. Evidence `ev_145d76d8f47e5b3cac7bc28995579ee7bb2cc2abcdf11438a9235adc2f280787`. Observed `rc_edit=0`, list `2 write report`, store text `buy oat milk` with done true, then `todo: no item with id 99` and `rc_unknown=1`.

## Open issues
- None. The Final Goal is met.

## Next action
- Stop. Do not open feature 003. Do not run converge again.

## Handoff
PROJECT: this repo (todo CLI) / SPEC ROOT: specs/ / FEATURE: specs/002-todo-edit / PHASE: closed
CODE STATE: main. `todo` last changed in 0042d0e. decisions.tsv untracked, leave it.
GOAL: The Final Goal is met. AC-E1..AC-E4 and REA pass.
DONE / NEXT: specify, plan, tasks, implement, converge once, REA pass / stop
CHECKS: `python3 -m unittest discover -s tests -v` → Ran 17 tests in 1.205s, OK, exit 0. Bound to 0042d0e. REA evidence `ev_145d76d8f47e5b3cac7bc28995579ee7bb2cc2abcdf11438a9235adc2f280787`.
RECOVERY: none
ROUTING: implement leaf poteto-agent, model unpinned. observed: unknown. Parent grok-4.7 verified the suite.
RECOVERY: none
ROUTING: how explainer and two architect runners requested poteto-agent, model unpinned. observed: unknown
BUDGET: Economy. Escalation passes 0. Architect ran because the change is two files, not a single-file skip.
BLOCKERS: none
RESUME: none (Grok has no resume.mjs checkpoint)

## Prior feature 001 (closed)
Delivered the stdlib todo CLI (add, list, done) under the previous Final Goal. REA pass is in specs/001-todo-cli/converge.md. Do not reopen it.
Prior probe on Claude was `pstack: 0.9.92|claude` with L1 and L4 gaps. This run re-probed on Grok (see Breadcrumbs).
