# progress.md

## Final Goal (2026-10-20)
Extend this todo CLI with (1) priorities 1-3 via `todo add --priority N` shown in list, (2) due dates via `todo add --due YYYY-MM-DD`, (3) `todo list --sort due|priority` and `todo list --overdue`, (4) migration of existing stores written by the current version with no data loss, (5) tests for every new behaviour. Delivered as two small specs: **002** covers (1)(2)(4); **003** covers (3). Mode: Economy. Status: **met** (002 and 003 closed with REA pass).

### Goal acceptance (pinned)
- G-1 `todo add --priority N` (N in 1..3) stores the priority; `todo list` shows it
- G-2 `todo add --due YYYY-MM-DD` stores the date; `todo list` shows it
- G-3 `todo list --sort due|priority` orders items; `todo list --overdue` filters to past-due open items
- G-4 a store written by 001 loads with no item lost or changed
- G-5 every new behaviour has a test; the suite passes from the repo root

## Final Goal status (2026-10-20)
**The Final Goal is met.** G-1, G-2, G-4 by feature 002 (REA `ev_fafe77f2903e52d5190f5f98c8eac76ffdc9f33801d58df3ed5578c171fd5ea6`), G-3 by feature 003 (REA `ev_18de17b23e2c28290860b1c42d9a2fac99e64221cae9fddc0f1f3ba6ee41fc1c`), G-5 by `python3 -m unittest discover -s tests -v` → `Ran 28 tests ... OK`. No carryover spec.

## Previous Final Goal (closed, feature 001)
Deliver a runnable stdlib-only (Python 3.11+) `todo` CLI with tests, per `sources/task.md` AC-1..AC-5. Met: REA pass in specs/001-todo-cli/converge.md.

## Breadcrumbs
host: cursor
pstack: 0.15.28|cursor
harness: L1 ok|L2 ok|L3 ok|L4 ok|L5 ok|L6 ok|L7 ok
pstack: hook-mandate → satisfied by O-poteto
cost-mode: Economy
pstack: O-sharpen|cursor|obligation → Final Goal + G-1..G-5; split 002/003
ROUTING: parent=composer; sheet absent → Economy; O-architect n/a single-file; O-poteto parent (leaf unavailable|usage-limit); O-interrogate 2 seats unavailable|usage-limit → lead dual-perspective

## Feature 002: priorities and due dates
- Status: **closed**
- pstack: O-specify → plan → tasks T001-T007 → implement e065297 (23 tests) → converge clean → REA pass `ev_fafe77f2903e52d5190f5f98c8eac76ffdc9f33801d58df3ed5578c171fd5ea6`

## Feature 003: list sort and overdue
- Status: **closed**
- pstack: O-specify → plan → tasks T001-T005 → implement 953b644 (28 tests) → converge clean → REA pass `ev_18de17b23e2c28290860b1c42d9a2fac99e64221cae9fddc0f1f3ba6ee41fc1c`

## Decisions
- Priority 1 = highest; optional fields omitted from JSON/list when unset.
- Due: strict 10-char `strptime("%Y-%m-%d")` + isoformat round-trip.
- Migration = load tolerates missing keys; no version field.
- Missing sort key sorts last; ties keep file order; overdue = `due < today` (today not overdue).
- Test: `python3 -m unittest discover -s tests -v`

## Outputs
- `todo` (~130 lines), `tests/test_todo.py` (28 tests)
- specs/001-todo-cli/, specs/002-priority-due/, specs/003-sort-overdue/

## Completed
- 002: specify → plan → tasks → implement → converge once → REA pass
- 003: specify → plan → tasks → implement → converge once → REA pass
- Final Goal met

## Open issues
- (none)

## Next action
- None. The Final Goal is met. No carryover spec.
