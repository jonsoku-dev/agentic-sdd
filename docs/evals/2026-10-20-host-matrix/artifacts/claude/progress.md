# progress.md

## Final Goal
Feature 002: add a `todo edit <id> <new text>` subcommand that replaces the item's text; an unknown id exits non-zero with a stderr message; tests cover both paths. Delivered as numbered Spec Kit feature `002-todo-edit` through agentic-sdd in Economy cost mode: specify, plan, tasks, implement, converge (once), REA closeout. Autonomous, commits as it goes.

Previous Final Goal (feature 001, closed 2026-10-20): runnable stdlib-only `todo` CLI per `sources/task.md` AC-1..AC-5.

## Breadcrumbs (002-todo-edit)
pstack: 0.9.92|claude
harness: L1 gap|L2 ok|L3 ok|L4 gap|L5 ok|L6 ok|L7 ok
pstack: hook-mandate -> satisfied by O-poteto
mode: Economy (cost-modes.md): O-architect n/a single-file, interrogate 2 reviewers, 1 implement leaf on worker model
pstack: O-sharpen|claude|obligation (sharpen + in-your-own-words inline, Economy) -> Final Goal + AC-6/AC-7 pinned below
speckit: specify -> specs/002-todo-edit/{spec.md, contracts/cli.md}; .specify/feature.json points at it
pstack: O-specify|claude|obligation-only (no technical-writing/unslop run, Economy) -> assumptions listed as assumptions; 001 FR-008 superseded in spec §Relation
pstack: O-how|claude|obligation (inline read, Economy) -> plan.md §Context cites todo:43-45, 63-68, 69-73 and tests/test_todo.py:18-22, 46
pstack: O-architect: n/a single-file (Economy) -> plan.md §Design shape: shared done/edit lookup
speckit: plan -> plan.md, quickstart.md; tasks -> tasks.md (T001-T003)
pstack: O-sequence|claude|principle-sequence-verifiable-units -> each task ends in a check; T001 must fail first
ROUTING: parent=claude-fable-5-1; sheet absent -> Economy defaults; implement leaf pstack:poteto-agent-low model sonnet (1 leaf, worktree); interrogate 2x pstack:effort-low on different families
pstack: O-poteto|claude|pstack:poteto-agent-low sonnet -> dispatched T001-T002 (worktree, base b89408e)
pstack: O-poteto|claude|pstack:poteto-agent-low sonnet -> T001-T002 verified (leaf c3aa897, cherry-picked as 91750f6); lead review: diff matches plan §Design, 17 tests OK, todo 86 lines
speckit: implement -> T001-T003 done; T003 quickstart by hand rc 0/1/2 as contracted
pstack: O-blast|claude|obligation inline -> unknown-id edit leaves store byte-identical (sha256 compare + test_edit_unknown_id)
pstack: O-hygiene|claude|obligation inline -> 0 comments added in diff
pstack: O-interrogate|claude|2x pstack:effort-low (opus, haiku) -> dispatched on 91750f6
speckit: converge (round 1, the only one) -> assessment: FR-101..FR-105, SC-101..SC-103 met; no tasks appended pending reviewer verdicts
pstack: O-interrogate|claude|2x pstack:effort-low (opus clean, haiku gaps<=consider) -> 1 act-on (exit-2 rows untested) -> T004 appended; rest dismissed in converge.md
speckit: converge outcome tasks_appended (T004) -> implement round (lead, test only) -> 18 tests OK; no second converge
pstack: O-rea|claude|mcp rea 6.7.0 capture_process_scenario -> pass (ev_d529d7963c852e02d319ffca3124c807d8ecfbb847ec3a1a0d616a1249e01e4d) on 97ac5ad
pstack: O-reflect: skipped (optional; no repeated mistake this feature)

## Acceptance 002 (pinned)
- AC-6 `todo edit <id> <new text>` replaces the text of the item with that id; `todo list` then shows the new text; exit 0
- AC-7 `todo edit` with an id matching no item exits non-zero with a message on stderr and leaves the store unchanged
- AC-8 tests cover AC-6 and AC-7 and the full suite passes from repo root
- Constraints carried from 001: stdlib only; `todo` under 200 lines; no features beyond the Final Goal (no multi-word join without quotes, no interactive edit)

## Breadcrumbs (001-todo-cli, closed)
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

## Acceptance 001 (pinned)
- AC-1 `todo add "text"` appends an item and prints its id
- AC-2 `todo list` prints open items as `<id> <text>`, oldest first
- AC-3 `todo done <id>` marks done; unknown id exits non-zero with stderr message
- AC-4 persistence in JSON at `$TODO_FILE` (default `./todo.json`)
- AC-5 test suite passes from repo root
- Constraints: stdlib only; nothing beyond AC-1..AC-5; code < 200 lines

## Decisions 002 (defaults, no human quiz)
- `edit` on a done item is allowed; text changes, item stays done (spec Edge Cases).
- Empty text and dash-prefixed text follow `add` (argparse; `--` needed); no validation added (FR-105).
- Unknown-id message and exit code copy `done` (`todo: no item with id <id>`, exit 1) so one convention holds.
- Economy: O-architect n/a single-file; O-blast and O-hygiene done inline; interrogate panel 2 (opus, haiku); one implement leaf (sonnet, poteto-agent-low); T004 test written by the lead.
- Spec 001 FR-008 (no edit) is superseded by 002 spec §Relation; 001 artifacts were not edited.

## Outputs 002
- todo (86 lines), tests/test_todo.py (18 tests), specs/002-todo-edit/{spec.md, plan.md, quickstart.md, tasks.md, converge.md, contracts/cli.md}, .specify/feature.json
- Commits: bf230fd specify, b89408e plan+tasks, 91750f6 feat (T001-T002), 97bac44 converge r1, 97ac5ad T004

## Completed 002
- specify -> plan -> tasks -> implement (T001-T003) -> converge once (T004 appended) -> implement T004 -> REA pass
- AC-6, AC-7, AC-8 met: `python3 -m unittest discover -s tests -v` -> Ran 18 tests, OK, exit 0; REA Evidence above

## Final Goal status
**The Final Goal is met.** Feature 002-todo-edit delivered `todo edit <id> <new text>` with tests for both the replace path and the unknown-id failure path; converge ran once; REA closeout disposition is `pass` with Evidence ID ev_d529d7963c852e02d319ffca3124c807d8ecfbb847ec3a1a0d616a1249e01e4d bound to commit 97ac5ad. No admitted work remains.

## Decisions 001 (defaults, no human quiz)
- Harness probe gaps: L1 no CLAUDE.md, L4 no deny rules, L7 progress.md absent at probe time (now created). Not fixed: outside Final Goal scope.
- Project playbook `.agents/playbooks/agentic-sdd.md` was not present at entry. It appeared later, and its content routes poteto runs into Spec Kit phases, which matches the flow followed. It was not installed or edited by this run.
- Constitution is the unfilled template; Final Goal constraints act as the governing rules.
- Entry point: executable `todo` script at repo root (shebang `python3`), invoked as `./todo ...`; tests drive it via subprocess.
- IDs: positive integers, `max(existing ids) + 1`; done items kept in file so ids never reused.
- `done` on an already-done id: succeeds silently (idempotent). Missing file = empty list.
- Test command: `python3 -m unittest discover -s tests -v`

## Outputs 001
- todo (executable, 80 lines; spec SC-004 counts implementation only), tests/test_todo.py (15 tests, 127 lines), .gitignore
- specs/001-todo-cli/{spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/cli.md, tasks.md, converge.md, checklists/requirements.md}

## Completed 001
- specify -> plan -> tasks -> implement (T001-T010) -> converge r1 (T011-T014 appended) -> implement -> converge r2: converged
- AC-1..AC-5 met: `python3 -m unittest discover -s tests -v` -> Ran 15 tests, OK, exit 0

## Open issues (001, resolved)
- (resolved 2026-10-20) REA closeout: blocked-limitation (see specs/001-todo-cli/converge.md §REA closeout). Under agentic-sdd rules the feature stays open until REA reaches pass. No install was attempted, per the user's instruction.
- `.agents/playbooks/agentic-sdd.md` appeared untracked mid-run (mtime 21:20) and was not found at entry. Its content matches the pstack-claude port template, so it was committed unchanged as the project playbook the user described.

## Next action
- None. Feature 002 closed (REA pass). Previous: Feature 001 closed: REA pass recorded in converge.md. (Previous: Fix the host Command Line Tools (duplicate SwiftBridging modulemap), then rerun REA `capture_process_scenario` with /tmp/rea-todo-001/scenario.sh on HEAD and record the Evidence IDs
