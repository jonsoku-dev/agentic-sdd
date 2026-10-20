# Converge: 001-todo-cli

## Round 1 (code state 224231e)

Checks: `python3 -m unittest discover -s tests -v` -> 10 tests OK. `wc -l todo` -> 63.

Obligations run:
- O-blast (`/pstack:blast-radius`): safety fact "a failed save never changes the store" proven at level 4 (script: a save that raises TypeError leaves the bytes unchanged and leaves no temp file). Risks found: the store is rewritten as mode 0600; `TODO_FILE` in a missing directory gives a traceback.
- O-hygiene (`/pstack:no-comments`, comment-sicko): 0 comments, 0 kills, no edits.
- O-interrogate (`/pstack:interrogate`): Reviewer A opus (7 findings), B fable (5), C sonnet (7), D haiku (5).

Lead judgment:
- Act on: wrong-shape store gives a traceback (A, B, C, D) -> T011. Write errors give a traceback (A, B, C, D) -> T012. 0600 mode and symlink replacement (A, B, C, D, plus symlink from A) -> T013. Tests check only for a non-zero exit, and FR-002 has no test (A, B, D) -> T014.
- Consider: none.
- Noted: no fsync before replace (A, C), acceptable for a personal todo list. `add "-x"` needs `--` (A), which is standard argparse behaviour. Implicit `else` for `done` (C), folded into T012's edit.
- Dismissed: a newline in the text breaks the list format (A, C, D), and empty text is accepted (B, C). The spec says text is "stored and printed unchanged", and FR-008 forbids extra validation features. Concurrent writes (C) are excluded by the spec's single-process assumption.

Outcome: tasks_appended (T011-T014) -> implement.

## Round 2 (code state 69737bb, then 37a48d4)

- implement: T011-T014 were done by a poteto-agent leaf (6ed2a43). The lead's review found that a 0600 store became 0644 after the rewrite (`AssertionError: 420 != 384`), fixed in 69737bb by `shutil.copymode`.
- Independent re-review (fable): T011-T014 close their findings, with no regression against AC-1..AC-5 or the contract. It found one warning: the mode test used 0600, which the original `mkstemp` code also produced, so the test did not discriminate. Fixed in 37a48d4 with 0o640. Proof: 224231e gives 600 and 6ed2a43 gives 644, so both fail the test.
- Nits dismissed: a fixed `<store>.tmp` name overwrites a stray file of that name, and when `.tmp` is a directory the error message changes. Both stay exit 1 with no data loss. The spec assumes a single process.
- Checks: `python3 -m unittest discover -s tests -v` -> `Ran 15 tests ... OK`. `wc -l todo` -> 80.

Outcome: converged (no new tasks).

## REA closeout
- Tooling: MCP rea (rea-agents 6.4.0 via npx). No `rea` CLI on PATH. installed-this-session: no (the user said not to install).
- Host setup client: claude_code (MCP already registered)
- Artifact: `./todo` at 37a48d45588f663de4b1be3b4b094ff60f975feb, clean tree for todo and tests
- Attempt 1: `capture_process_scenario` on /tmp/rea-todo-001/scenario.sh -> `process_capture_failed`: "macOS process ownership helper compilation failed via xcrun (compiler result: 1)" (`/Library/Developer/CommandLineTools/usr/include/swift/module.modulemap:13:8: error: redefinition of module 'SwiftBridging'`). This is a host Command Line Tools defect, not something in this repo.
- Attempt 2 (alternate static path): `open_binary` on ./todo -> `target_unavailable`: "unsupported binary format" (a Python source script).
- Evidence IDs: none issued.
- Non-REA runtime substitute: the same scenario run directly printed `1`, `2`, `1 buy milk`/`2 write report`, `rc=0`, `2 write report`, `todo: no item with id 99`, `rc=1`, and the expected JSON store. This does not replace REA Evidence.
- Findings: none material
- Disposition: blocked-limitation
- Remediation: repair the duplicate SwiftBridging modulemap in Command Line Tools (reinstall CLT or `sudo xcode-select -s` to a full Xcode), then rerun `capture_process_scenario` with /tmp/rea-todo-001/scenario.sh against this commit.

## REA closeout, retry after host fix (2026-10-20)
- Host fix: Command Line Tools 26.6 installed (was 16.4 on macOS 26.6.2); `xcrun swiftc` on `bridge/process/*.swift` compiles.
- The session's REA MCP server predated the fix and still failed (`cleanup_incomplete`); the same scenario through a fresh CLI process succeeded.
- Command: `npx -y rea-agents@6.4.0 capture-process rea-scenario.json --format json --full-output` on HEAD 9f3546b (todo unchanged since 37a48d4).
- Evidence ID: `ev_500769f77dcd683a767e00aca8fa1517a60f62f73ed46be8eff22ff1d718cbdb`; executable sha256 `c0eaf44f…f373e100`; cleanup `owned_process_group: verified, temporary_root: removed`.
- Observed frames: `1`, `2`, `1 buy milk` / `2 write report`, `rc=0`, `2 write report`, `todo: no item with id 99`, `rc=1`, JSON store with id 1 done.
- Findings: none material. Disposition: **pass**.
