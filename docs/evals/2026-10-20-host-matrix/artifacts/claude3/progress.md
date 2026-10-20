# progress.md

## Final Goal (2026-10-20)
Extend the todo CLI with (1) priorities 1-3 via `todo add --priority N` shown in list, (2) due dates via `todo add --due YYYY-MM-DD`, (3) `todo list --sort due|priority` and `todo list --overdue`, (4) migration of existing stores written by the current version with no data loss, (5) tests for every new behaviour. Delivered as two small specs: 002 covers (1), (2), (4); 003 covers (3). Mode: Economy. Status: met (002 and 003 closed with REA pass).

### Goal acceptance (pinned)
- G-1 `todo add --priority N` (N in 1..3) stores the priority; `todo list` shows it
- G-2 `todo add --due YYYY-MM-DD` stores the date; `todo list` shows it
- G-3 `todo list --sort due|priority` orders items; `todo list --overdue` filters to past-due open items
- G-4 a store written by 001 loads with no item lost or changed
- G-5 every new behaviour has a test; the suite passes from the repo root

## Previous Final Goal (closed 2026-10-20, feature 001)
Deliver a runnable stdlib-only (Python 3.11+) `todo` CLI with tests, per `sources/task.md` AC-1..AC-5, under 200 lines, no extra features. Met: REA pass recorded in specs/001-todo-cli/converge.md.

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

## Feature 002: priorities and due dates
- Breadcrumbs:
  - pstack: 0.9.92|claude
  - harness: L1 gap|L2 ok|L3 ok|L4 gap|L5 ok|L6 ok|L7 ok
  - pstack: hook-mandate -> satisfied by O-poteto
  - pstack: O-sharpen|claude|obligation (goal pinned above as G-1..G-5; split 002/003 decided by dependency: sort/overdue need the stored fields)
  - ROUTING: parent=claude-fable-5-1; sheet absent -> Economy defaults: O-architect n/a single-file; implement 1 leaf pstack:poteto-agent-medium model sonnet; interrogate 2 reviewers pstack:effort-medium (opus, haiku)
  - pstack: O-specify|claude|obligation-only -> specs/002-priority-due/spec.md, assumptions listed as assumptions
- Decisions:
  - Priority 1 = highest. Both fields optional and absent from JSON and from the list line when not set, so 001's 15 tests and contract stay byte-identical.
  - `due` stored as the `YYYY-MM-DD` string; strict parse via `strptime("%Y-%m-%d")` because `date.fromisoformat` on 3.14 also accepts `20261020` and week forms (checked).
  - Migration = `load` tolerates missing keys and validates present ones. No version field, no rewrite-on-load.
  - 001's 200-line cap not carried as a requirement.
  - Spec dir created with `create-new-feature.sh`; it makes no git branch, so work stays on `main` like 001.
  - pstack: O-how|claude|obligation (file:line read by the lead; no explainer subagent in Economy) -> plan.md §Context cites todo:9-11,14-22,44-48,57-65 and tests/test_todo.py:68-77,91-99
  - pstack: O-architect|claude|n/a single-file (Economy) -> plan.md §Design names the data shape
  - pstack: O-sequence|claude|obligation -> tasks.md T001-T007, each ends in a check; 7 tasks so no split
  - Decision: research.md/data-model.md/quickstart.md folded into plan.md and contracts/cli.md (Economy)
  - pstack: O-poteto|claude|pstack:poteto-agent-medium (sonnet, worktree) -> T001-T007 verified (e4758bb, 22 tests OK); lead fix: strict 10-char date (leaf accepted `2026-1-5`), list line de-nested, tests extended
  - pstack: O-blast|claude|obligation -> proven by run: 001 script (900b125) lists and writes a 002 store, keeping `priority`/`due`; 002 reads it back (`1 [P1] [due 2026-12-31] a`); new script on 001 store covered by test_old_store_round_trip
  - pstack: O-hygiene|claude|obligation -> 0 comments in diff, no slop words
  - pstack: O-interrogate|claude|obligation, 2 reviewers (pstack:effort-medium opus + haiku) -> 1 must-fix shared by both (space-padded day / non-ASCII digits pass `is_date`) -> T008 appended, converge.md
  - implement T008 by the lead (2-file, 8-line fix; no leaf in Economy) -> 22 tests OK
  - pstack: O-rea|claude|mcp rea capture_process_scenario -> pass, ev_ae808042ce714843cdfbdaf431bd48b4fec6885ce58933f29abc9f4864188087 on db15367
- Status: **closed** (G-1, G-2, G-4 met; G-5 met for 002 scope: 22 tests OK). Remaining goal work: G-3 -> feature 003.

## Feature 003: list sort and overdue
- Breadcrumbs:
  - pstack: O-sharpen|claude|obligation (scope = G-3 only; depends on 002 fields)
  - pstack: O-specify|claude|obligation-only -> specs/003-sort-overdue/spec.md
  - pstack: O-how|claude|obligation -> plan.md §Context cites todo:59,72-77,32-35,7 and tests/test_todo.py:19-23,125-129
  - pstack: O-architect|claude|n/a single-file (Economy)
  - pstack: O-sequence|claude|obligation -> tasks.md T001-T005
  - ROUTING: same as 002 (1 leaf pstack:poteto-agent-medium sonnet; 2 reviewers effort-medium opus + haiku)
- Decisions:
  - Missing sort key sorts last; ties keep file order (stable sort). Overdue = `due < today` string compare, strictly before; due today is not overdue.
  - Tests use far-past/far-future dates plus the real today; no clock env var.
  - pstack: O-poteto|claude|pstack:poteto-agent-medium (sonnet, worktree) -> T001-T005 verified (a34585c, 28 tests OK); lead review: diff matches plan sketch, no fix needed
  - pstack: O-blast|claude|obligation -> premise "ISO string order == date order" checked on 2000 random dates; 002's `is_date` guarantees the stored form
  - pstack: O-hygiene|claude|obligation -> 0 comments in diff
  - pstack: O-interrogate|claude|obligation, 2 reviewers (pstack:effort-medium opus + haiku) -> no must/should-fix; test gap for bare `--sort` + blank-line nits -> T006 appended, converge.md
  - implement T006 by the lead (test-only) -> 28 tests OK
  - pstack: O-rea|claude|mcp rea capture_process_scenario -> pass, ev_3ee0707c99234ea3f75330965c68c600e9fcf35dd18b084f20da326b844d129d on 59c948a
- Status: **closed** (G-3 met; G-5 met: 28 tests OK)

## Final Goal status (2026-10-20)
**The Final Goal is met.** G-1, G-2, G-4 by feature 002 (REA pass ev_ae808042ce714843cdfbdaf431bd48b4fec6885ce58933f29abc9f4864188087), G-3 by feature 003 (REA pass ev_3ee0707c99234ea3f75330965c68c600e9fcf35dd18b084f20da326b844d129d), G-5 by `python3 -m unittest discover -s tests -v` -> `Ran 28 tests ... OK` at 59c948a and re-run at 1a1bae3 (15 from 001 unchanged, 7 from 002, 6 from 003). No carryover spec.

## Feature 001 (closed)

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
- todo (executable, 110 lines), tests/test_todo.py (28 tests), .gitignore
- specs/001-todo-cli/{spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/cli.md, tasks.md, converge.md, checklists/requirements.md}
- specs/002-priority-due/{spec.md, plan.md, tasks.md, converge.md, contracts/cli.md, checklists/requirements.md}
- specs/003-sort-overdue/{spec.md, plan.md, tasks.md, converge.md, contracts/cli.md, checklists/requirements.md}

## Completed
- 001: specify -> plan -> tasks -> implement (T001-T010) -> converge r1 (T011-T014 appended) -> implement -> converge r2: converged -> REA pass
- 002: specify -> plan -> tasks -> implement (T001-T007, leaf + lead fix) -> converge (T008 appended) -> implement -> REA pass
- 003: specify -> plan -> tasks -> implement (T001-T005, leaf) -> converge (T006 appended, test-only) -> implement -> REA pass
- Final Goal met: `python3 -m unittest discover -s tests -v` -> Ran 28 tests, OK, exit 0 at 59c948a

## Open issues
- (resolved 2026-10-20) REA closeout: blocked-limitation (see specs/001-todo-cli/converge.md §REA closeout). Under agentic-sdd rules the feature stays open until REA reaches pass. No install was attempted, per the user's instruction.
- `.agents/playbooks/agentic-sdd.md` appeared untracked mid-run (mtime 21:20) and was not found at entry. Its content matches the pstack-claude port template, so it was committed unchanged as the project playbook the user described.

## Next action
- None. The Final Goal is met (see "Final Goal status"). No carryover spec.
- (history) Feature 001 closed: REA pass recorded in converge.md. (Previous: Fix the host Command Line Tools (duplicate SwiftBridging modulemap), then rerun REA `capture_process_scenario` with /tmp/rea-todo-001/scenario.sh on HEAD and record the Evidence IDs
