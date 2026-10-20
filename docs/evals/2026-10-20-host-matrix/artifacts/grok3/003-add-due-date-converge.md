# Converge: 003-add-due-date

## Round 1 (code state 71d988c, todo sha256 9f44726115d0a196fe6a493a12b8b07d073e2f90233c703db019ee7d54860b06)

Checks: `python3 -m unittest discover -s tests -v` -> Ran 38 tests, OK.

Obligations run:

- O-blast: safety fact "list and a bad `--due` leave the store bytes unchanged, and a later add does not invent `due` on the old item" proven at level 4. Script exit `BLAST_OK`.
- O-hygiene (comment-sicko): 0 comments killed. Diff `c0f981d..71d988c` has no narrating comments. Nothing edited.
- O-interrogate: two poteto-agent reviewers (Economy panel, same host, no model pin). Reviewer A and Reviewer B each reported no findings.

Lead inventory against spec FR-001..FR-008, US1..US3 acceptance, the plan's pre-load check, and the contract: no missing, partial, contradicting, or unrequested product gap. Constitution skipped (unfilled template). `tasks.md` stays unchanged.

Outcome: converged.

## REA closeout

- Tooling: MCP `rea__capture_process_scenario` (rea-agents 6.7.0). installed-this-session: no
- Host setup client: grok_build (MCP already connected)
- Artifact: `./todo` at content sha256 `9f44726115d0a196fe6a493a12b8b07d073e2f90233c703db019ee7d54860b06`, git HEAD `181f7e0` (docs only on top of `71d988c`)
- Command: capture of `/tmp/rea-todo-003/scenario.sh`, working directory `/tmp/rea-todo-003`, observing `/tmp/rea-todo-003/store.json`
- Evidence ID: `ev_ac1063c279de06db2c88b0235f5bed6e9d68e6fcc75b35290fd439ca0576a0f0`
- Scenario script sha256: `19890fd08f4df38807158f472e0cd466d96414a346616210af35a305bbe5e344`
- Cleanup: `owned_process_group: verified`, `temporary_root: removed`. Exit code 0.
- Observed frames: old file lists `1 p3 a` with `bytes_same=yes`; adds print `2` and `3`; list is `1 p3 a`, `2 p1 due 2026-10-21 pay rent`, `3 p3 file taxes`; `--due 2026-02-31` prints `todo: due must be YYYY-MM-DD` and `rc=1`; the saved store fills priority 3 on the old row, does not add `due` there, and stores the new dated row as priority 1 with `due` `2026-10-21`.
- Findings: none material
- Disposition: pass
