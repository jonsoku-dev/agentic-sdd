# progress.md

## Final Goal
**Status: met (2026-10-20).** Extend the existing todo CLI with priorities 1-3 (`todo add --priority N`) shown in list output; due dates (`todo add --due YYYY-MM-DD`); `todo list --sort due|priority` and `todo list --overdue`; a no-data-loss migration from the current JSON store; and tests for every new behavior. Deliver with Agentic SDD (`specify → plan → tasks → implement → converge once → REA closeout`), commit as work proceeds, and stop only when this file records Final Goal met or names the next spec as carryover.

## Breadcrumbs
pstack: 0.9.92|claude
harness: L1 gap|L2 ok|L3 ok|L4 gap|L5 ok|L6 ok|L7 gap
harness: L7 now ok (progress.md has Outputs/Completed/Decisions/Open issues/Next action); L1/L4 gaps left (no CLAUDE.md, no deny rules; outside Final Goal)
pstack: hook-mandate → satisfied by O-poteto
pstack: O-sharpen|claude|/pstack:sharpen → Final Goal + AC pinned below
ROUTING: parent=claude-opus-5-5 (unchanged); sheet absent -> pstack defaults; how explainer pstack:effort-low opus; architect runners effort-low opus+sonnet; implement leaves pstack:poteto-agent-medium x2 (requested medium, observed unknown); interrogate effort-medium opus/fable/sonnet/haiku; re-review effort-medium fable
pstack: O-specify|claude|obligation-only (no technical-writing/unslop skill run) -> spec.md assumptions listed as assumptions
pstack: O-how|claude|/pstack:how -> plan.md §Context (greenfield, no collisions, no root .gitignore)
pstack: O-architect|claude|/pstack:architect -> 2 candidates (argparse+list vs match+dict), A base + B grafts, plan.md §Design
pstack: O-sequence|claude|principle-sequence-verifiable-units -> tasks.md, each task ends in a check
pstack: O-poteto|claude|pstack:poteto-agent-medium -> T001-T010 verified (worktree, 224231e)
pstack: O-poteto|claude|pstack:poteto-agent-medium -> T011-T014 verified (worktree, 6ed2a43); lead fixes 69737bb, 37a48d4
pstack: O-blast|claude|/pstack:blast-radius -> safety fact proven at level 4 (a failed save leaves the store unchanged)
pstack: O-hygiene|claude|/pstack:no-comments -> 0 comments, 0 kills
pstack: O-interrogate|claude|/pstack:interrogate -> 4 reviewers, 4 act-on -> T011-T014 appended; round-2 independent re-review clean after test fix
pstack: O-rea|claude|mcp rea -> blocked-limitation (host swiftc modulemap error; static open unsupported)
pstack: O-rea|claude|rea CLI capture-process -> pass (ev_500769f77dcd683a767e00aca8fa1517a60f62f73ed46be8eff22ff1d718cbdb) after CLT 26.6 fix

## Acceptance (pinned)
- AC-1 `todo add "text"` appends an item and prints its id
- AC-2 `todo list` prints open items as `<id> <text>`, oldest first
- AC-3 `todo done <id>` marks done; unknown id exits non-zero with stderr message
- AC-4 persistence in JSON at `$TODO_FILE` (default `./todo.json`)
- AC-5 test suite passes from repo root
- Constraints: stdlib only; nothing beyond AC-1..AC-5; code < 200 lines

## Decisions (defaults, no human quiz)
- Harness probe gaps: L1 no CLAUDE.md, L4 no deny rules, L7 progress.md absent at probe time (now created). Not fixed: outside Final Goal scope.
- Project playbook `.agents/playbooks/agentic-sdd.md` was not present at entry. It appeared later, and its content routes poteto runs into Spec Kit phases, which matches the flow followed. It was not installed or edited by this run.
- Constitution is the unfilled template; Final Goal constraints act as the governing rules.
- Entry point: executable `todo` script at repo root (shebang `python3`), invoked as `./todo ...`; tests drive it via subprocess.
- IDs: positive integers, `max(existing ids) + 1`; done items kept in file so ids never reused.
- `done` on an already-done id: succeeds silently (idempotent). Missing file = empty list.
- Test command: `python3 -m unittest discover -s tests -v`

## Outputs
- todo (executable, 80 lines; spec SC-004 counts implementation only), tests/test_todo.py (15 tests, 127 lines), .gitignore
- specs/001-todo-cli/{spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/cli.md, tasks.md, converge.md, checklists/requirements.md}

## Completed
- specify -> plan -> tasks -> implement (T001-T010) -> converge r1 (T011-T014 appended) -> implement -> converge r2: converged
- AC-1..AC-5 met: `python3 -m unittest discover -s tests -v` -> Ran 15 tests, OK, exit 0

## Open issues
- (resolved 2026-10-20) REA closeout: blocked-limitation (see specs/001-todo-cli/converge.md §REA closeout). Under agentic-sdd rules the feature stays open until REA reaches pass. No install was attempted, per the user's instruction.
- `.agents/playbooks/agentic-sdd.md` appeared untracked mid-run (mtime 21:20) and was not found at entry. Its content matches the pstack-claude port template, so it was committed unchanged as the project playbook the user described.

## Next action
- Feature 001 closed: REA pass recorded in converge.md. (Previous: Fix the host Command Line Tools (duplicate SwiftBridging modulemap), then rerun REA `capture_process_scenario` with /tmp/rea-todo-001/scenario.sh on HEAD and record the Evidence IDs

## Active delivery (2026-10-20)

### Run facts
- Existing feature: `001-todo-cli`, complete with REA pass; new bounded change starts at `002-todo-priority-dates`.
- Entry revision: `900b125`; working tree clean; existing CLI is `todo`; tests are `tests/test_todo.py`.
- Runtime host observed by harness: Codex; pstack 0.9.94 available; active parent model remains session-inherited and unchanged. Economy behavior: use a small spec, one implementation worker if any, two converge reviewers; no unnecessary setup or broad checks.
- `skill_gate.py` chose `agentic-sdd` (prose confidence 0.01, selection confidence 0.99). pstack hook mandate is satisfied inside Agentic SDD phases.
- Harness probe: `pstack: 0.9.94|codex`; `harness: L1 gap|L2 ok|L3 ok|L4 ok|L5 ok|L6 ok|L7 ok`.
- Existing store shape is a JSON array of `{id, text, done}` objects. Preserve those records and add defaults during read/migration; do not rewrite on read-only commands. Detailed compatibility choices will be pinned in spec 002.

### Phase trail
- Enter/resume O-sharpen: pinned this Final Goal; no human quiz.
- Specify: complete for feature 002; three P1 stories cover entry, retrieval, and legacy migration. Acceptance pins default priority 3, ascending stable sorts, undated last, local-date overdue strict-before-today, and lazy read-safe migration. O-specify technical-writing and unslop applied; requirements checklist is pending reviewer-quality review.
- Plan: complete; O-how source locations cited; O-architect skipped under Economy because implementation remains in the existing single executable. Standard-library parsing, current JSON format, lazy normalization, and test mapping are recorded in plan/research/data-model/contract/quickstart.
- Tasks: complete; 7 ordered tasks across 3 stories, below the 12-task split threshold. O-sequence applied; tests precede implementation in each story and every task has an observable check.

### Implementation updates
- O-poteto|codex|inline after worker dispatch rejected parent model `gpt-6.1-sol` for this account; no worker changed files. Continued as sole writer in `/tmp/todo-priority-dates` on isolated branch `codex/todo-priority-dates`. Requested feature worker model was `gpt-6-luna` per sheet; observed dispatch failure was injected `gpt-6.1-sol`; no successful child execution.
- T001 complete: added real-command tests for metadata add/default/display and invalid input non-mutation. Red check: `python3 -m unittest discover -s tests -p test_todo.py -v` -> 18 tests, 6 expected failures for missing metadata display/persistence. The invalid-input non-mutation cases already pass because argparse rejects unknown options before any write.
- T002 complete: add accepts priority 1-3 (default 3) and canonical dates, stores the values, validates persisted metadata, and displays `[P<N>]` plus optional `[due YYYY-MM-DD]`. `python3 -m unittest discover -s tests -v` -> 18 tests, OK. The first focused run exposed two stale baseline expectations; updated the output and persisted JSON assertions, then the full suite passed.
- T003 complete: added subprocess tests for stable due/priority sorting, undated-last ordering, local today/past/future overdue boundaries, done filtering, and combined options. Red check: focused suite -> 21 tests, 3 expected failures because `list` does not yet accept the new flags.
- T004 complete: `list` now accepts both flags, filters overdue open items strictly before local today, sorts ascending with stable ties, and puts undated records last. `python3 -m unittest discover -s tests -p test_todo.py -v` -> 21 tests, OK.
- T005 complete: added subprocess tests for legacy read-only bytes, migration on add/done, old field/order preservation, defaults, and metadata retention. Red check: focused suite -> 25 tests, 2 expected failures because successful writes do not yet normalize legacy records.
- T006 complete: `load` supplies missing fields in memory; only successful add/done writes save them. Legacy read-only bytes, add/done migration, Unicode text, record order, done state, and migrated values all pass. `python3 -m unittest discover -s tests -p test_todo.py -v` -> 25 tests, OK.
- T007 complete: `python3 -m unittest discover -s tests -v` -> 25 tests, OK; `wc -l todo` -> 116; `git diff --check` clean.
- O-blast: caller census found no additional product consumers beyond `todo` and `tests/test_todo.py`; exact legacy-store add/done/list tests run against the real executable passed (3 tests), and `test_done_unknown_id` checks failed-operation bytes remain unchanged.
- O-hygiene and deslop: independent read-only pass found no comments or slop in the changed implementation/tests; comment scan found only the shebang.
- O-interrogate (Economy, two independent reviewers): reviewer 1 found no issue in CLI behavior; reviewer 2 found one LOW coverage gap for partially migrated records. A different-family reviewer could not start because the account rejected `gpt-6-astra`; both successful reviews used the sheet-selected `gpt-6-luna` in separate contexts.
- Requirements checklist: independent reviewer marked CHK001-CHK007 satisfied against the exact checklist text; statuses recorded in `checklists/requirements.md`.
- Converge ran once at code state `76cfe75`: one LOW partial coverage finding, no behavior/data-loss defects. T008 was appended for a partially migrated store test. Do not reconverge.
- T008 complete in the single fix round: added a mixed partially upgraded store test. Focused suite and full suite each report 26 tests, OK; `wc -l todo` remains 116; `git diff --check` clean. No implementation code changed in the fix round.
- O-rea: first capture launched `/bin/sh` and was excluded because its executable digest did not bind to `todo`. Direct MCP capture of `todo` at `4d45fea` passed with Evidence ID `ev_064ed609e379aa1033ae8e865a2c5ba6a1a8a9d007d616c796d2c144376b5f3a`; captured SHA-256 matches the file. Exit 0, id 9, old records retained/defaulted, new metadata persisted; no material findings.
- Converge prerequisite: initial helper call failed because no `.specify/feature.json` pointer exists; rerun with `SPECIFY_FEATURE_DIRECTORY=$PWD/specs/002-todo-priority-dates` succeeded. No project config was written.

### Outputs
- Existing source of truth and runnable baseline: `todo`, `tests/test_todo.py`, `specs/001-todo-cli/`.
- New specification: `specs/002-todo-priority-dates/spec.md` and `checklists/requirements.md`.
- Plan artifacts: `plan.md`, `research.md`, `data-model.md`, `contracts/cli.md`, and `quickstart.md`.
- Task plan: `specs/002-todo-priority-dates/tasks.md` (8 tasks after the single converge finding).
- Converge record: `specs/002-todo-priority-dates/converge.md`.

### Completed
- Initial checkout, ownership, existing feature state and tool/model constraints inspected.
- Specify, plan, tasks, implementation, single converge, one gap fix round, and REA closeout pass completed for feature 002.
- US1 add/display behavior, US2 sorting/overdue behavior, and US3 lazy migration/data preservation are covered by 26 passing subprocess tests.

### Open issues
- None. REA disposition is pass; no carryover spec is needed.

### Next action
- Final Goal met. No next spec or carryover is required.
