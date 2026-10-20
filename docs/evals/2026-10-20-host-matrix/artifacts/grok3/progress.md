# progress.md

## Final Goal
Extend the todo CLI with (1) priorities 1-3 via `todo add --priority N` shown in list, (2) due dates via `todo add --due YYYY-MM-DD`, (3) `todo list --sort due|priority` and `todo list --overdue`, (4) migration of existing stores written by the current version with no data loss, (5) tests for every new behaviour. Economy Spec Kit. One converge per spec. Stop when this file says the Final Goal is met or names the next spec as carryover.

In the user's words: the daily `todo` command should rank items, date them, filter the list, and open the JSON file people already have without dropping anything.

## Final Goal status

The Final Goal is met.

Specs 002, 003, and 004 are closed. Each had one converge and an REA pass. None is closed-carryover. There is no next spec.

- AC-P met in `specs/002-add-priority`. Evidence `ev_b505f7e4dc974308f26ae99a09b838add33d2818254c0b40dbab528549d676c6`.
- AC-M met in `specs/002-add-priority`. A current file of `id`, `text`, and `done` still lists, and a later save keeps those fields plus any extra field.
- AC-D met in `specs/003-add-due-date`. Evidence `ev_ac1063c279de06db2c88b0235f5bed6e9d68e6fcc75b35290fd439ca0576a0f0`.
- AC-L met in `specs/004-list-sort`. Evidence `ev_05bd78108b448f0798b74672ca411395b628625012c17b4ea246f4ddde506a59`.
- AC-T met. `python3 -m unittest discover -s tests -v` → Ran 45 tests, OK.

`todo` sha256 `6ba64a2355a8107ddde293efd12fd3d110b4b1ff41e528d6770730b9aa7d7d99` at product commit `8222d42`.

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
pstack: 0.9.93|grok
harness: L1 gap|L2 ok|L3 ok|L4 ok|L5 ok|L6 ok|L7 ok
pstack: hook-mandate → satisfied by O-poteto
pstack: O-sharpen|grok|sharpen+in-your-own-words → Final Goal pinned; first spec is priority plus lossless current stores
pstack: O-specify|grok|technical-writing+unslop → specs/002-add-priority/spec.md assumptions listed as assumptions
pstack: O-how|grok|how explainer → plan.md §Context cites todo:9-11, todo:55-69, tests/test_todo.py:46-52
pstack: O-architect|grok|n/a single-file → plan.md §Design, Economy skip
pstack: O-sequence|grok|principle-sequence-verifiable-units → tasks.md T001-T007, each task ends in a check
ROUTING: parent=grok-4.7 (unchanged); sheet absent -> pstack defaults; cost=Economy; how explainer requested opus observed grok-4.7 (spawn has no model pin); implement = 1 poteto-agent leaf, worker effort, observed unknown until dispatch
pstack: O-poteto|grok|commits 89eea8b 140506a c3893a4 → T001-T007 checked; python3 -m unittest discover -s tests -v → Ran 26 tests, OK
pstack: O-blast|grok|blast-radius → safety fact proven at level 4 (list and a rejected add leave store bytes unchanged; a later add keeps an extra key and fills priority 3). Script exit BLAST_OK.
pstack: O-hygiene|grok|comment-sicko → 0 comments, 0 kills. Diff af595f2..HEAD adds no comment lines.
pstack: O-interrogate|grok|2 poteto-agent reviewers → no findings. Lead inventory zero gaps. tasks.md unchanged. Same host, no model pin.
rea: O-rea|grok|mcp capture_process_scenario → pass ev_b505f7e4dc974308f26ae99a09b838add33d2818254c0b40dbab528549d676c6
pstack: O-specify|grok|technical-writing+unslop → specs/003-add-due-date/spec.md assumptions listed as assumptions
pstack: O-how|grok|how explainer → plan.md §Context cites todo:9-14, todo:64-68, todo:82-84
pstack: O-architect|grok|n/a single-file → plan.md §Design, Economy skip
pstack: O-sequence|grok|principle-sequence-verifiable-units → tasks.md T001-T007, each task ends in a check
pstack: O-poteto|grok|poteto-agent worktree → T001-T007 verified (ae5e8ca, 0876d83, 441c86a, 71d988c). python3 -m unittest discover -s tests -v → Ran 38 tests, OK
pstack: O-blast|grok|blast-radius → safety fact proven at level 4 (list and a bad --due leave bytes unchanged; a later add does not invent due on the old item). Script exit BLAST_OK.
pstack: O-hygiene|grok|comment-sicko → 0 comments killed on c0f981d..71d988c
pstack: O-interrogate|grok|2 poteto-agent reviewers → no findings. Lead inventory zero gaps. tasks.md unchanged. Same host, no model pin.
rea: O-rea|grok|mcp capture_process_scenario → pass ev_ac1063c279de06db2c88b0235f5bed6e9d68e6fcc75b35290fd439ca0576a0f0
pstack: O-specify|grok|technical-writing+unslop → specs/004-list-sort/spec.md assumptions listed as assumptions
pstack: O-how|grok|how explainer → plan.md §Context cites todo:78, todo:92-101, todo:34-42
pstack: O-architect|grok|n/a single-file → plan.md §Design, Economy skip
pstack: O-sequence|grok|principle-sequence-verifiable-units → tasks.md T001-T007, each task ends in a check
pstack: O-poteto|grok|poteto-agent worktree → T001-T007 verified (leaf b51f94a 26af034 6057b6e 6dda5f5, integrated as 8222d42). python3 -m unittest discover -s tests -v → Ran 45 tests, OK
pstack: O-blast|grok|blast-radius → safety fact proven at level 4 (list --sort and list --overdue leave bytes unchanged; --sort foo exits 2 and leaves bytes unchanged). Script exit BLAST_OK.
pstack: O-hygiene|grok|comment-sicko → 0 comments killed on 3e63594..8222d42
pstack: O-interrogate|grok|2 poteto-agent reviewers → no findings. Lead inventory zero gaps. tasks.md unchanged. Same host, no model pin.
rea: O-rea|grok|mcp capture_process_scenario → pass ev_05bd78108b448f0798b74672ca411395b628625012c17b4ea246f4ddde506a59

## Acceptance (pinned)
Whole goal, admitted in order:
- AC-P `todo add --priority N` for N in 1..3, shown in `todo list`. Omitted flag stores priority 3 (1 most urgent).
- AC-D `todo add --due YYYY-MM-DD`.
- AC-L `todo list --sort due|priority` and `todo list --overdue`.
- AC-M Stores written by feature 001 (`id`, `text`, `done` only) load with no data loss.
- AC-T Every new behaviour has a test. `python3 -m unittest discover -s tests -v` exits 0.
Feature 002 admits AC-P, AC-M, and the priority part of AC-T. Feature 003 admits AC-D. Feature 004 admits AC-L. All five acceptance lines are met. See Final Goal status.

## Decisions (defaults, no human quiz)
- Harness probe gaps from feature 001 stand. This run's probe: L1 still gap (no project instruction file). Not added. It is outside the Final Goal.
- Cost mode Economy. One converge per spec. If the single fix round leaves gaps, mark closed-carryover and specify the next smaller spec.
- Spec split: 002 priority and migration, then 003 due dates, then 004 sort and overdue. Split up front because the combined task list would pass 12 tasks.
- Priority 1 is most urgent, 3 is least. Default 3. List token `pN` in `<id> p<priority> <text>`.
- Listing does not rewrite the file. A later save fills a missing priority and keeps id, text, done, and any extra stored field.
- A stored priority outside 1..3 makes the file unreadable and is not rewritten.
- No git branch hook (no `.specify/extensions.yml`). Commits stay on the current branch.
- Constitution is still the unfilled template. Feature 001 constraints plus this Final Goal govern.
- Grok has no `/goal` tool in this session. This file is the completion record.
- Decision log: `decisions.tsv` (local, not committed).

## Outputs
- Feature 001: `todo` (executable), `tests/test_todo.py`, `.gitignore`, `specs/001-todo-cli/`
- Feature 002: `specs/002-add-priority/` closed, including `converge.md`. `.specify/feature.json` is local and gitignored.
- Feature 003: `specs/003-add-due-date/` closed, including `converge.md`.
- Feature 004: `specs/004-list-sort/` closed, including `converge.md`.

## Completed
- Feature 001: specify -> plan -> tasks -> implement -> converge -> REA pass. `python3 -m unittest discover -s tests -v` -> Ran 15 tests, OK.
- Feature 002: specify -> plan -> tasks -> implement -> converge -> REA pass. Evidence `ev_b505f7e4dc974308f26ae99a09b838add33d2818254c0b40dbab528549d676c6`. Suite: Ran 26 tests, OK. AC-P and AC-M for current stores are met.
- Feature 003: specify -> plan -> tasks -> implement -> converge -> REA pass. Evidence `ev_ac1063c279de06db2c88b0235f5bed6e9d68e6fcc75b35290fd439ca0576a0f0`. Suite: Ran 38 tests, OK. AC-D is met.
- Feature 004: specify -> plan -> tasks -> implement -> converge -> REA pass. Evidence `ev_05bd78108b448f0798b74672ca411395b628625012c17b4ea246f4ddde506a59`. Suite: Ran 45 tests, OK. AC-L is met.
- Final Goal is met. No next spec.

## Open issues
- L1 instruction-file gap remains, outside this goal.

## Next action
- None. The Final Goal is met. Do not open another spec.

## Handoff
PROJECT: todo CLI at this repo
SPEC ROOT: `specs/`
FEATURE: `specs/004-list-sort` closed
PHASE: done
CODE STATE: product commit `8222d42`. `todo` sha256 `6ba64a2355a8107ddde293efd12fd3d110b4b1ff41e528d6770730b9aa7d7d99`. `decisions.tsv` stays untracked.
GOAL: Final Goal is met. AC-P, AC-D, AC-L, AC-M, and AC-T are met.
DONE / NEXT: 004 REA pass. No next spec.
CHECKS: `python3 -m unittest discover -s tests -v` → Ran 45 tests, OK.
RECOVERY: none
ROUTING: parent grok-4.7, Economy, sheet absent
BUDGET: Economy. Architect skipped (single-file). Interrogate = 2 reviewers.
BLOCKERS: none
RESUME: none (Grok has no resume.mjs checkpoint)
