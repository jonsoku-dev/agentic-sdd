# progress.md

## Final Goal
Deliver a new numbered Spec Kit feature adding `todo edit <id> <new text>` to replace an existing item's text. Unknown IDs exit non-zero with a stderr message. Tests cover both success and unknown-ID failure. Finish specify → plan → tasks → implement → one converge → REA closeout, committing each phase, and stop when this file states the goal is met.

## Active Feature 002

### Acceptance
- AC-1 `todo edit <id> <new text>` replaces the matching item's text and preserves its ID and done state.
- AC-2 an unknown ID exits non-zero, writes a message to stderr, and leaves storage unchanged.
- AC-3 automated subprocess tests cover successful replacement and unknown-ID failure.
- Constraints: stdlib only; retain existing CLI behavior and data format; no unrelated features.

### Breadcrumbs
- Start state: clean `main` at `3ff57a9`; feature `001-todo-cli` closed with REA pass.
- Skill gate: agentic-sdd selected (0.99); pstack mandate fulfilled within Spec Kit phases, no standalone playbook.
- Economy mode: preserve full Spec Kit phase sequence; skip architect panel for single-file scope; use a two-reviewer converge panel; narrow checks to CLI behavior and repository suite.
- Harness: `python ~/.codex/skills/agentic-sdd/scripts/harness_probe.py --host codex --project .` → L1 gap; L2-L7 ok.
- Specify: `specs/002-todo-edit/spec.md` and requirements checklist reviewed; AC-1..AC-3 cover success, unknown ID, and real-command tests. Initializer state recorded in `.specify/feature.json`.
- Plan: reuse argparse, ID lookup/error, item shape, and atomic save; one-file behavior change plus CLI contract tests. Economy single-file scope skips the architect panel. `setup-plan.sh --json` resolved the active feature correctly.
- Tasks: T001 adds three user-visible subprocess checks (open replacement, completed status preservation, unknown-ID no-write); T002 implements parser/handler; T003 runs suite, quickstart, and line budget. `setup-tasks.sh --json` resolved all planned design inputs.
- Implement: isolated leaf completed T001/T002 in `/tmp/codex-002-todo-edit-worktree`, requested `gpt-6-luna@low` from the Economy sheet; observed model/effort unknown. Pre-implementation focused tests failed with argparse's unsupported-command exit 2; post-implementation focused tests passed (leaf report). Main checkout re-reviewed and integrated only `todo` and `tests/test_todo.py`.
- T003: main checkout `python3 -m unittest discover -s tests -v` → 18 tests, OK; quickstart subprocess flow add/edit/list passed and unknown ID returned 1 with stderr; `wc -l todo` → 86, below 200. `git diff --check` passed in leaf.
- O-hygiene/deslop: reviewed the complete source/test diff; general read-only Economy agent substituted after the specialized reviewer role rejected unsupported `gpt-6.1-sol`; no findings, no new comments or unnecessary defense. Runtime model/effort observed unknown.
- O-blast: unknown edit ID returns before shared `save`; real subprocess test `test_edit_unknown_id_fails_without_changing_store` compares store bytes and passes. Cleared risk: unknown ID cannot rewrite storage on this path.
- O-interrogate: Economy panel completed with Reviewer A `gpt-6-luna@low` requested and Reviewer B `gpt-5.6-terra@low` requested; runtime model/effort observed unknown for both. Both independently returned no findings. Review was read-only on `todo` and `tests/test_todo.py` at commit `b665d8e`.
- Converge (single run): reviewed FR-001..FR-004, SC-001..SC-004, three scenarios, plan decisions, and tasks T001-T003; zero findings. Tasks hash remained `701314c020202d14a3f1abd318d6160b795553aa6b3b5a9aca4e00e9e393bf2b`; no convergence task appended. Local installed phase contract used because no callable Codex `speckit-converge` command was exposed.
- Post-converge criterion gate: all 11 criteria (4 FR, 4 SC, 3 scenarios) explicitly reviewed against current source and receipts; `criterion_gate.py decide` → `advance=true`, 11/11, no unmet/errors. Digest `0ff715cdb049c7dd249fecb9a8653ccab4d5afa874b7f3b365e57804c9368da1`.
- O-rea: three REA process-capture Evidence IDs recorded in `specs/002-todo-edit/converge.md` and `evidence/rea.json`; observed add/edit/list success, unknown-ID exit 1/stderr, and no-write store hashes. Disposition pass; residual environment/process sampling limitations are non-material to these CLI acceptance conditions.

### Outputs
- `specs/002-todo-edit/spec.md`
- `specs/002-todo-edit/checklists/requirements.md`
- `specs/002-todo-edit/plan.md`
- `specs/002-todo-edit/research.md`
- `specs/002-todo-edit/data-model.md`
- `specs/002-todo-edit/contracts/cli.md`
- `specs/002-todo-edit/quickstart.md`
- `specs/002-todo-edit/tasks.md`
- `specs/002-todo-edit/converge.md`
- `specs/002-todo-edit/evidence/{criteria.json, answers.json, review.json, environment.txt, unittest.txt}`
- `specs/002-todo-edit/evidence/rea.json`

### Completed
- Specify, plan, tasks, implementation, the one converge, criterion coverage, and REA closeout complete. REA pass and all acceptance criteria verified.

### Decisions
- `edit` accepts the existing integer ID parsing convention, replaces only `text`, and succeeds silently like `done`.
- Edit applies to any existing item, including completed items, and preserves `done`; no requirement excludes completed items.
- New text is one CLI positional argument; shell quoting carries spaces and Unicode.

### Open issues
- None.

### Next action
- Final Goal met. Stop.

### Final Goal Status
- MET. The requested `todo edit` feature completed all Spec Kit phases, the single converge, and REA closeout.

## Historical Record: Feature 001

### Breadcrumbs
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

### Acceptance (pinned)
- AC-1 `todo add "text"` appends an item and prints its id
- AC-2 `todo list` prints open items as `<id> <text>`, oldest first
- AC-3 `todo done <id>` marks done; unknown id exits non-zero with stderr message
- AC-4 persistence in JSON at `$TODO_FILE` (default `./todo.json`)
- AC-5 test suite passes from repo root
- Constraints: stdlib only; nothing beyond AC-1..AC-5; code < 200 lines

### Decisions (defaults, no human quiz)
- Harness probe gaps: L1 no CLAUDE.md, L4 no deny rules, L7 progress.md absent at probe time (now created). Not fixed: outside Final Goal scope.
- Project playbook `.agents/playbooks/agentic-sdd.md` was not present at entry. It appeared later, and its content routes poteto runs into Spec Kit phases, which matches the flow followed. It was not installed or edited by this run.
- Constitution is the unfilled template; Final Goal constraints act as the governing rules.
- Entry point: executable `todo` script at repo root (shebang `python3`), invoked as `./todo ...`; tests drive it via subprocess.
- IDs: positive integers, `max(existing ids) + 1`; done items kept in file so ids never reused.
- `done` on an already-done id: succeeds silently (idempotent). Missing file = empty list.
- Test command: `python3 -m unittest discover -s tests -v`

### Outputs at Feature 001 closeout
- todo (executable, 80 lines; spec SC-004 counts implementation only), tests/test_todo.py (15 tests, 127 lines), .gitignore
- specs/001-todo-cli/{spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/cli.md, tasks.md, converge.md, checklists/requirements.md}

### Completed
- specify -> plan -> tasks -> implement (T001-T010) -> converge r1 (T011-T014 appended) -> implement -> converge r2: converged
- AC-1..AC-5 met: `python3 -m unittest discover -s tests -v` -> Ran 15 tests, OK, exit 0

### Issues recorded during Feature 001 recovery
- (resolved 2026-10-20) REA closeout: blocked-limitation (see specs/001-todo-cli/converge.md §REA closeout). Under agentic-sdd rules the feature stays open until REA reaches pass. No install was attempted, per the user's instruction.
- `.agents/playbooks/agentic-sdd.md` appeared untracked mid-run (mtime 21:20) and was not found at entry. Its content matches the pstack-claude port template, so it was committed unchanged as the project playbook the user described.

### Historical next action at Feature 001 closeout
- Feature 001 was closed after REA pass; its earlier Command Line Tools recovery note is retained here for history.
