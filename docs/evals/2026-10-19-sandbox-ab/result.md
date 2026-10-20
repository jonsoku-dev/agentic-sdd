# A/B result: Spec Kit alone (A) vs agentic-sdd + pstack + harness layers (B)

Same brief (`todo` CLI, AC-1..AC-5, <200 LOC), same Spec Kit 1.0.1 scaffold,
same model (opus, headless `claude -p`, bypassPermissions). B started before
the one-converge-per-spec rule landed, so its two converge rounds reflect the
old policy.

| Metric (measured) | A | B |
|---|---|---|
| Black-box AC-1..AC-4 (measure.py) | all pass | all pass |
| Own test suite | 6 tests, OK | 15 tests, OK |
| Corrupt store (`{"oops":1}`) | Python traceback | `todo: cannot read …: not a todo store`, exit 1 |
| Unwritable path | traceback | `todo: cannot write …`, exit 1 |
| `done abc` | "no item with id abc" (string compare) | argparse int error |
| Implementation LOC | 63 (`todo.py` + 8-line `todo` shim) | 80 (`todo`) |
| Spec artifacts | spec/plan/tasks/research/data-model/contracts/quickstart | same + `converge.md` |
| progress.md | none | 8 sections, Next action, 16 breadcrumbs, ROUTING line |
| Independent review | none | interrogate 4 models → 4 act-on → T011–T014; blast-radius level-4 proof; re-review by a second model |
| REA closeout | not attempted | attempted twice, `blocked-limitation` (host CLT modulemap defect), feature left open |
| Commits | 3 | 8 |
| Turns / wall / cost | 21 / 135 s / $0.96 | 24 / 582 s / $11.24 |

## Failure probes (verbatim)

```text
== A corrupt store
TypeError: string indices must be integers, not 'str'   (traceback, rc=1)
== A unwritable dir
FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/dir/todo.json'   (traceback)
== A done non-int
todo: no item with id abc
== B corrupt store
todo: cannot read _bad.json: not a todo store   (rc=1)
== B unwritable dir
todo: cannot write /nonexistent/dir/todo.json: [Errno 2] No such file or directory: '/nonexistent/dir/todo.json.tmp'
== B done non-int
todo done: error: argument id: invalid int value: 'abc'
```

## Against the pre-registered prediction

- Row 2 (independent review recorded): B won in this run. Four-model interrogate produced
  real defects (unvalidated store shape, write errors as tracebacks, file mode
  regression) that A shipped.
- Row 3 (resumable progress): B won in this run. A has no progress.md; B's `Next action`
  names the exact REA rerun.
- Row 6 (black-box parity or better): parity on AC-1..4; B strictly better on
  the three failure probes.
- Row 5 (scope control): both stayed inside AC; B added robustness, not
  features; both under 200 LOC.
- Cost: B is 11.7× the dollars and 4.3× the wall time of A. Prediction said
  2–4×; the panel (4 reviewers + re-review + 2 poteto leaves) is the cost.
- REA: B spent effort on a closeout that the host could not run. Correct per
  the rules (blocked-limitation, not finish), but zero evidence returned.

## Limits of this run

n = 1 per arm on one 60-line task. The prompts were asymmetric: B's prompt
named every obligation (`harness_probe`, `pstack:sharpen`, `how`, `architect`,
`poteto-agent`, `blast-radius`, `no-comments`, `interrogate`, breadcrumbs,
`ROUTING:`), while A's said only "use the speckit skills, no pstack". So the
run shows that the obligations, when executed, catch defects A shipped; it does
not show that `/agentic-sdd` alone triggers all of them unprompted. B's own
breadcrumb `O-specify … obligation-only` shows one Required row was skipped
even when prompted. Failure probes below are the load-bearing evidence.

## Judgment

Effective for SDD: **yes, on correctness evidence and continuity; no, on cost
for a task this small.** The stack found and fixed three defects A shipped,
left an auditable trail, and never claimed finish without REA. For a 60-line
feature that is $10 of insurance. The value claim scales with feature size and
risk: the per-feature fixed cost (probe, sharpen, how, architect, interrogate,
REA) is roughly constant while the defects it catches grow with surface area.

## What this run tells us to change

1. Cost tiering: `cost-modes.md` Economy/Balanced should shrink the interrogate
   panel (2 reviewers) and skip `architect` for single-file specs; Thorough
   keeps the full panel. Already partly expressed; make it explicit per
   obligation.
2. REA on a plain Python script: `open_binary` is unsupported and
   `capture_process_scenario` depends on host toolchain. Document the
   `not-applicable` path for source-only CLIs with no build artifact, so a
   healthy host is not blocked by a tooling gap it cannot fix.
3. One-converge rule (now landed) would have cut B's second converge; the
   re-review would still run as "affected checks".

## Host-fix follow-up (after the measured run)

The table above is the experiment. These checks ran later, on 2026-10-19,
after Command Line Tools 26.6.0.0.1781586589 replaced CLT 16.4. They do not
change the A/B cost or the original `blocked-limitation`.

- `xcrun swiftc` of `rea-agents` `bridge/process/ProcessRunTokenReader*.swift` exits 0. The 2023 `usr/include/swift/module.modulemap` is still on disk; this compiler no longer reports `redefinition of module 'SwiftBridging'`.
- Fresh CLI `npx -y rea-agents@6.4.0 capture-process` on arm B's `./todo` scenario: `ev_500769f77dcd683a767e00aca8fa1517a60f62f73ed46be8eff22ff1d718cbdb`, exit 0, cleanup `owned_process_group: verified`. Terminal shows add/list/done and the JSON store.
- Cursor MCP `capture_process_scenario` on `/usr/bin/true`: `ev_b9bcb0045959c76f93729a5fc0e892f26bbb385fc25df87eb55e347a4b65fe2e`, exit 0, cleanup verified.
- Same MCP on the arm B `./todo` scenario: `ev_7dc83a232e62fc41354807e92a2f66d5e89a90360e9c7fc511a47e1578e02aa1`, exit 0. Rendered lines include `1 buy milk`, `2 write report`, `rc=0`, `todo: no item with id 99`, `rc=1`, and the store with id 1 done. Disposition for this rerun: `pass`. No material finding.
- 2026-10-20 follow-up: this Claude session's MCP server (rea-agents 6.4.0, started before the CLT update) kept failing with `cleanup_incomplete … environment_unavailable` after reconnect. The live candidates were Chrome Helper (Renderer) processes (`csops` flags: `CS_RESTRICT` set, not platform binaries) spawned during the capture; 6.4.0 fails closed on them. Concurrent 14 s captures of `/bin/sleep` while tabs opened and closed: 6.4.0 rc=1 (`environment_unavailable=2`), 6.7.0 rc=0, `ev_92225e1401e61b2d0a4132e82caf8d7343d2b15617f7347a8a66b46eb41f027d`, cleanup verified, those PIDs recorded as `restricted_process_environment_withheld`. All four host configs now pin 6.7.0.
- Lesson 1 is in the panel-size table in `references/pstack-integration.md` (Economy: skip single-file architect, 2 reviewers).
- Lesson 2 stays `blocked-limitation` when the capture helper cannot compile. A source-only script is not `not-applicable`; it uses `capture_process_scenario`. A healthy host now returns Evidence.

Host checks from the same night, outside the A/B cost:

- Codex has no `/goal` (`codex --help`). `spawn_agent` with `model=gpt-6-luna` and `reasoning_effort=low` started; the child replied OK. Omitting the model is still rejected as `gpt-6.1-sol`.
- Cursor CLI `agent -p` can open the linked `poteto-mode` skill by path. It does not list that skill in the session catalog.
- Grok `spawn_subagent` enum includes user agent `poteto-agent`. `grok models` (logged in) lists `grok-4.7`, `grok-4.7-build-fast`, `grok-4.6`, `grok-4.5`. The pstack SessionStart script is not executed; the mandate is the home rule.
- `install.sh --apply-cursor-hooks` and `--uninstall` were run against a temporary HOME. Uninstall removes the continuation hooks and leaves unrelated hooks. The live `~/.cursor/hooks.json` entries stayed. `python3 -m unittest discover -s tests` → 90 tests OK.
- `git init` in this skill directory. No commit.

## Host verification after the run (2026-10-19/20)

| Item | Result |
|---|---|
| REA on this Mac | CLT 16.4 → 26.6 fixed `SwiftBridging` (CLI Evidence `ev_500769f7…` pass). Remaining `cleanup_incomplete` was rea-agents 6.4.0 failing closed on Chrome renderer processes started mid-capture; 6.7.0 passes (`ev_92225e14…`). Claude/Cursor/Codex/Grok configs repinned to 6.7.0. After a Claude Code restart the MCP server (6.7.0) passes `/usr/bin/true` (`ev_05f218af…`) and the arm B `./todo` scenario (`ev_7cd25a9a…`, exit 0, cleanup verified) |
| Claude Code | `pstack:poteto-agent` dispatch verified (smoke test); `/goal` facts from official docs |
| Codex | pstack skills visible; `spawn_agent` rejects the parent slug when `model` is omitted → sheet now names `gpt-6-luna`, spawn ok; SessionStart mandate not injected until `/hooks` trust |
| Cursor | IDE plugin 0.15.28; Agent CLI lists `poteto-agent`, effort agents, `/goal`; plugin skills not loaded by the CLI → `install.sh --cursor-cli-skills` links them (names appear; invocation unverified, CLI quota exhausted) |
| Grok Build | `pstack@pstack-claude` installed; `poteto-agent` user link spawns and reads SKILL.md; hook stdout never injected → `--grok-mandate` home rule verified loaded; models grok-4.7 / 4.7-build-fast / 4.6 |
