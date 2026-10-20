# Converge: 003-sort-overdue

## Round 1 (code state a34585c / 5b52e70)

Checks: `python3 -m unittest discover -s tests -v` -> 28 tests OK. `wc -l todo` -> 110.

Obligations run:
- O-blast (obligation): premise "ISO `YYYY-MM-DD` string order equals date order" checked on 2000 random dates; 002's `is_date` guarantees the stored form, so the sort key and the `< today` compare need no parsing.
- O-hygiene (obligation): 0 comments in the diff.
- O-interrogate (Economy, 2 reviewers, different families): A = pstack:effort-medium opus, B = pstack:effort-medium haiku. Both ran the real script against mixed stores (missing keys, done items, today, far past/future) and confirmed plain `list` is byte-identical to 8c3f1dc.

Lead judgment:
- No must-fix or should-fix from either reviewer.
- Act on (small, in scope of FR-001): `todo list --sort` with no value exits 2 but has no test (B); two blank-line style slips in the test file (A, B) -> T006.
- Noted: repeated `--sort` flags are last-wins (B), standard argparse, not in the spec. Hand-edited stores with ids out of order sort by file order (A), outside the single-writer assumption.

Outcome: tasks_appended (T006, test-only) -> implement once, then REA. No second converge on this spec.

## Implement round after converge (lead, T006)

- `test_list_sort_invalid` now loops over `("--sort", "text")` and a bare `("--sort",)`; blank lines restored. `todo` unchanged from a34585c.
- Checks: `python3 -m unittest discover -s tests -v` -> `Ran 28 tests ... OK`.

Outcome: affected checks green -> REA closeout.

## REA closeout
- Tooling: MCP rea (rea-agents 6.7.0 via npx) | installed-this-session: no
- Host setup client: claude_code (already registered)
- Artifact: `./todo` at 59c948a (todo unchanged since a34585c; clean tree); scenario /tmp/rea-todo-003/scenario.sh (4 adds with mixed priority/due, one done, plain list, --sort due, --sort priority, --overdue, --overdue --sort priority, --sort text)
- Command: `capture_process_scenario` executable /bin/sh, arguments [/tmp/rea-todo-003/scenario.sh], filesystem_observation_paths [/tmp/rea-todo-003/store.json]
- Evidence ID: `ev_3ee0707c99234ea3f75330965c68c600e9fcf35dd18b084f20da326b844d129d`
- Observed frames: ids `1`-`4`; plain list `1 [P3] [due 2026-12-31] a` / `2 b` / `3 [P1] [due 2000-01-01] c` (done item 4 hidden); `--sort due` and `--sort priority` both `3, 1, 2` (no-key item last); `--overdue` only `3 [P1] [due 2000-01-01] c`; combined the same; `--sort text` usage + `invalid choice: 'text'` rc=2. exit 0, cleanup `owned_process_group: verified`.
- Findings: none material
- Disposition: **pass**
