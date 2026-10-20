# Converge: 002-add-priority

## Round 1 (code state c3893a4, todo sha256 4f0bdada64b5030941cdafb8ce88100ed789392c4464abe2605ca94b465bff48)

Checks: `python3 -m unittest discover -s tests -v` -> Ran 26 tests, OK.

Obligations run:

- O-blast: safety fact "list and a rejected add leave the store bytes unchanged, and a later add keeps an extra key while filling priority 3" proven at level 4. The script also rejected `--priority 0` and `--priority -1` and kept the last repeated `--priority`.
- O-hygiene (comment-sicko): 0 comments, 0 kills. The diff `af595f2..c3893a4` adds no comment lines.
- O-interrogate: two poteto-agent reviewers (Economy panel, same host, no model pin). Reviewer A and Reviewer B each reported no findings after reading the diff.

Lead inventory against spec FR-001..FR-008, US1..US3 acceptance, the plan's save-path fill, and the contract: no missing, partial, contradicting, or unrequested product gap. Constitution skipped (unfilled template). `tasks.md` stays unchanged.

Outcome: converged.

## REA closeout

- Tooling: MCP `rea__capture_process_scenario` (rea-agents 6.7.0). installed-this-session: no
- Host setup client: grok_build (MCP already connected)
- Artifact: `./todo` at content sha256 `4f0bdada64b5030941cdafb8ce88100ed789392c4464abe2605ca94b465bff48`, git HEAD `4b1fcab` (docs only on top of `c3893a4`)
- Command: capture of `/tmp/rea-todo-002/scenario.sh`, working directory `/tmp/rea-todo-002`, observing `/tmp/rea-todo-002/store.json`
- Evidence ID: `ev_b505f7e4dc974308f26ae99a09b838add33d2818254c0b40dbab528549d676c6`
- Scenario script sha256: `c79b6746269dfc1130ecefa7e3b70564daf75f1430aa2d9398d165c9b35d2f87`
- Cleanup: `owned_process_group: verified`, `temporary_root: removed`. Exit code 0.
- Observed frames: old file lists `1 p3 a` with `bytes_same=yes`; adds print `2`, `3`, `4`; list is `1 p3 a`, `2 p1 pay rent`, `3 p3 file taxes`, `4 p2 call sam`; `--priority 4` prints `todo: priority must be 1, 2, or 3` and `rc=1`; the store keeps the old text and done flag, fills `"priority": 3` on that row, and stores 1, 3, and 2 on the new rows.
- Findings: none material
- Disposition: pass
