# Converge: 004-list-sort

## Round 1 (code state 8222d42, todo sha256 6ba64a2355a8107ddde293efd12fd3d110b4b1ff41e528d6770730b9aa7d7d99)

Checks: `python3 -m unittest discover -s tests -v` -> Ran 45 tests, OK.

Obligations run:

- O-blast: safety fact "list --sort and list --overdue leave the store bytes unchanged, and --sort foo exits 2 without changing bytes" proven at level 4. Script exit `BLAST_OK`.
- O-hygiene (comment-sicko): 0 comments killed. Diff `3e63594..8222d42` for `todo` and `tests/test_todo.py` has no narrating comments. Nothing edited.
- O-interrogate: two poteto-agent reviewers (Economy panel, same host, no model pin). Reviewer A and Reviewer B each reported no findings.

Lead inventory against spec FR-001..FR-008, US1..US3 acceptance, the plan's filter-then-stable-sort, and the contract: no missing, partial, contradicting, or unrequested product gap. Constitution skipped (unfilled template). `tasks.md` stays unchanged.

Outcome: converged.

## REA closeout

- Tooling: MCP `rea__capture_process_scenario` (rea-agents 6.7.0). installed-this-session: no
- Host setup client: grok_build (MCP already connected)
- Artifact: `./todo` at content sha256 `6ba64a2355a8107ddde293efd12fd3d110b4b1ff41e528d6770730b9aa7d7d99`, git HEAD `8124add` (docs only on top of `8222d42`)
- Command: capture of `/tmp/rea-todo-004/scenario.sh`, working directory `/tmp/rea-todo-004`, observing `/tmp/rea-todo-004/store.json`
- Evidence ID: `ev_05bd78108b448f0798b74672ca411395b628625012c17b4ea246f4ddde506a59`
- Scenario script sha256: `ba1815086729d3bb048883517876facfb825eef60ccb877c0e5869e3c9b49cdc`
- Cleanup: `owned_process_group: verified`, `temporary_root: removed`. Exit code 0.
- Observed frames: adds print `1`, `2`, `3`. `--sort due` prints `3 p2 due 2020-01-01 past`, `1 p3 due 2026-12-01 later`, `2 p1 undated`. `--sort priority` prints `2 p1 undated`, `3 p2 due 2020-01-01 past`, `1 p3 due 2026-12-01 later`. `--overdue` prints `3 p2 due 2020-01-01 past`. `bytes_same=yes`. `--sort foo` exits 2 with `invalid choice: 'foo'`.
- Findings: none material
- Disposition: pass
