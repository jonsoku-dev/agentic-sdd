# Converge: 002-priority-due

## Round 1 (code state b79a017)

Checks: `python3 -m unittest discover -s tests -v` -> 22 tests OK. `wc -l todo` -> 104.

Obligations run:
- O-blast (obligation): the 001 script at 900b125 lists and writes a store written by 002 and keeps `priority`/`due`; the 002 script reads it back. A 001-shape store round-trips through `list`, `add --priority`, `done` with old items byte-identical (test_old_store_round_trip).
- O-hygiene (obligation): 0 comments in the diff, no slop words.
- O-interrogate (Economy, 2 reviewers, different families): A = pstack:effort-medium opus (3 findings), B = pstack:effort-medium haiku (3 findings). Both ran the real script.

Lead judgment:
- Act on: `is_date` accepts a space-padded day `2026-01- 5` (A must-fix, B must-fix) and full-width digits `２０２６-01-01` (A must-fix), on `--due` and in the store, because `strptime` `%d` accepts a leading space and `int()` accepts Unicode digits while the 10-char check still passes. Confirmed by the lead. Fix is a round trip through `date().isoformat()`, which also replaces the length check -> T008. The usage error naming the helper (`invalid is_date value`, B nit) folds into T008 via `ArgumentTypeError`.
- Dismissed: `--priority " 2"` accepted as 2 (A, B nit): `int()` semantics, stored value is in contract.
- Noted: text starting with `-` needs `--` (B): 001 argparse behaviour, unchanged.

Outcome: tasks_appended (T008) -> implement once, then REA. No second converge on this spec.

## Implement round after converge (lead, T008)

- Code: `is_date` is now a boolean round trip (`strptime(...).date().isoformat() == s`), `due` is the argparse type and raises `ArgumentTypeError("expected YYYY-MM-DD")`; `is_due` deleted. Net 103 lines.
- Discrimination: at b79a017 `add --due "2026-01- 5" x` exited 0 (reviewers A, B and the lead); now exits 2 with `argument --due: expected YYYY-MM-DD`.
- Checks: `python3 -m unittest discover -s tests -v` -> `Ran 22 tests ... OK` (the new inputs are subTests).

Outcome: affected checks green -> REA closeout.

## REA closeout
- Tooling: MCP rea (rea-agents 6.7.0 via npx, pinned in ~/.claude.json) | installed-this-session: no
- Host setup client: claude_code (already registered)
- Artifact: `./todo` at db15367 (clean tree); executable sha256 of /bin/sh recorded by the tool `c0eaf44f…f373e100`; scenario /tmp/rea-todo-002/scenario.sh (001-shape store, add with --priority/--due, list, two invalid inputs, store dump)
- Command: `capture_process_scenario` executable /bin/sh, arguments [/tmp/rea-todo-002/scenario.sh], filesystem_observation_paths [/tmp/rea-todo-002/store.json]
- Evidence ID: `ev_ae808042ce714843cdfbdaf431bd48b4fec6885ce58933f29abc9f4864188087`
- Observed frames: `1 old open`; ids `3`,`4`,`5`; `1 old open` / `3 [P1] [due 2026-12-31] taxes` / `4 [due 2000-01-01] late` / `5 [P3] low`; `argument --priority: invalid choice: '4'` rc=2; `argument --due: expected YYYY-MM-DD` rc=2; store JSON with items 1-2 unchanged (no new keys) and 3-5 carrying only the keys given. exit 0, cleanup `owned_process_group: verified`.
- Findings: none material
- Disposition: **pass**
