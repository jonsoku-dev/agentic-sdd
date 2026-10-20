# Converge: 003-sort-overdue

**Date**: 2026-10-20  
**Commit**: 953b644

## Obligations (Economy)

- **O-blast**: Premise "ISO string order == calendar order" holds for 002-validated `YYYY-MM-DD` (lexicographic == chronological). Overdue uses `due < today.isoformat()`.
- **O-hygiene**: No new comments beyond shebang.
- **O-interrogate**: 2-seat panel unavailable|usage-limit (same host limit as 002). Lead dual-perspective review → no must-fix (bare `--sort` / invalid choice covered by `test_sort_bare_and_invalid`; plain list still green).

## Assessment

| Req | Status |
|-----|--------|
| FR-001..FR-004 sort/overdue | met |
| FR-005 plain list | met (001/002 list tests OK) |
| FR-006 suite | `Ran 28 tests ... OK` |

## Result

**converged** — no Convergence tasks appended.

## REA closeout

- Disposition: **pass**
- Tool: MCP `rea` `capture_process_scenario` on `/tmp/rea-todo-003/scenario.sh`
- Evidence ID: `ev_18de17b23e2c28290860b1c42d9a2fac99e64221cae9fddc0f1f3ba6ee41fc1c`
- Bound to commit: `70e030b` (todo/tests unchanged since `953b644`)
- Observed: plain/sort due/sort priority/overdue listings; `Ran 28 tests ... OK`; exit 0
- Material findings: none
