# progress.md

## Final Goal
Deliver a runnable stdlib-only (Python 3.11+) `todo` CLI with tests, per `sources/task.md` AC-1..AC-5, under 200 lines, no extra features.

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
