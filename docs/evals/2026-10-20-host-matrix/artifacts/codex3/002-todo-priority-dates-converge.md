# Converge: Todo priorities and due dates

## Single converge pass

**Code state**: HEAD `76cfe75` in the isolated implementation worktree; `todo` is 116 lines. Full suite at the prior task checkpoint passed: 25 tests. This converge pass ran once.

**Reviewed scope**: spec FR-001..FR-009, SC-001..SC-004, all three user stories, plan decisions for legacy array compatibility and atomic writes, and the reviewer-owned requirements checklist CHK001..CHK007. The constitution is an unfilled template, so no project principles apply.

**Obligations**:
- O-blast: no other product callers found; real-executable tests passed for legacy list/add/done and unknown-done no-write behavior.
- O-hygiene and deslop: no comments or slop in changed code/tests.
- O-interrogate, Economy: two independent reviewers used `gpt-6-luna` in separate contexts because the account rejected `gpt-6-astra`. Reviewer 1 found no CLI behavior gaps. Reviewer 2 found the partial-migration test gap below.
- Requirements-quality reviewer found CHK001..CHK007 satisfied.

## Findings

| ID | Gap type | Severity | Source | Evidence | Remaining work |
|---|---|---|---|---|---|
| F1 | partial | LOW | FR-006, FR-007 | `tests/test_todo.py` covers fully legacy records and records with both fields, but does not cover partially migrated records. `todo` fills missing fields with `setdefault` during load. | T008 tests a mixed store containing priority-only and due-only records across a successful write. |

**Summary**: 9 functional requirements, 4 success criteria, 3 user stories, and 7 checklist criteria reviewed. One low-severity test coverage gap was found. No runtime defect or data-loss issue was found. No acceptance criterion was relaxed.

**Outcome**: `tasks_appended` (T008). Run one implement round for T008, then affected checks and REA closeout. Do not converge again on this feature.

## Single fix round

- T008 added `test_write_migrates_partially_upgraded_records`, which covers a priority-only item and a due-only item in one store.
- Focused suite: `python3 -m unittest discover -s tests -p test_todo.py -v` -> 26 tests, OK.
- Full suite: `python3 -m unittest discover -s tests -v` -> 26 tests, OK.
- Size: `wc -l todo` -> 116. `git diff --check` clean.
- No remaining convergence tasks. Converge was not rerun.

## REA closeout

- Tooling: REA MCP `capture_process_scenario`, REA 6.7.0; no CLI installation this session.
- Host setup client: Codex (MCP already available).
- Artifact: `todo` at commit `4d45fea`; SHA-256 `bf4aea4cddfd42845466747bf63310a7d9c684e104e2b17ecb657967606aefce`.
- First capture (`ev_4e85e0ee6e15ffc67f0a047a32e9b661ea8bb06f9364387319d70de929d57c7f`) launched `/bin/sh`, so it did not bind evidence to `todo` and is not used for disposition.
- Direct capture: `ev_064ed609e379aa1033ae8e865a2c5ba6a1a8a9d007d616c796d2c144376b5f3a`. The tool ran `todo add --priority 1 --due 2026-10-25 ship`, exited 0, printed id `9`, and observed the existing store change from 81 to 269 bytes. The resulting records retained the legacy entries and added their default fields plus the new item metadata.
- Findings: none material.
- Disposition: **pass**.
- Limitations: REA reports artifact identity unavailable and its process capture has the documented prelaunch digest, sampled-process, before/after-filesystem, and inherited-environment limits. The direct executable digest matches the `todo` file at the recorded commit. Automated tests provide the full behavior coverage.
