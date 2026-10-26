---
description: >
  One-page card loaded on every feature: the required phase→obligation rows,
  the breadcrumb lines, and the common REA closeout path. Open the long
  references only for the cases listed at the end.
---

# Phase card

## Obligations per phase

Run each row as the pstack skill when it is installed (`/pstack:<skill>` on
Claude, bare names on Cursor, by name on Codex), else as the obligation in your
own words. Record one breadcrumb per row.

| Phase | Obligation | Skill | Must leave |
|-------|------------|-------|------------|
| Enter / resume | `O-sharpen` | `sharpen` (`recall` when cold) | Final Goal + AC pinned in `progress.md`; plan the whole Final Goal as **one** spec, even when it names several commands; split only at `tasks`, past ~12 tasks |
| Enter, existing code touched | `O-how` | `how` | file:line evidence in `plan.md` |
| `specify` / `clarify` | `O-specify` | `technical-writing` + `unslop` | spec prose; assumptions marked |
| `plan`, code crosses a function boundary | `O-architect` | `architect` | plan + verification contract |
| `tasks` | `O-sequence` | `principle-sequence-verifiable-units` | ordered `tasks.md`, each task ends in a check; `progress_gate.py` refuses more than 12 tasks |
| `implement` | `O-poteto` | poteto-mode non-negotiables | admitted task IDs only; inline unless a single-loop trigger holds; a leaf's worktree is removed (`git worktree remove`) once its diff is merged |
| Pre-converge | `O-blast`, `O-hygiene` | `blast-radius`, `no-comments` | external risk proved or task-tracked; no narrating comments |
| `converge` | `O-interrogate` | `interrogate` | a **spawned** reviewer's findings (foreground; no `ScheduleWakeup`, not even as a heartbeat); gaps appended to `tasks.md` |
| Post-converge | `O-rea` | REA (below) | Evidence ID bound to the current code |
| Before `/compact` or host switch | `O-pause` | `pause-safely` | `progress.md` current |

`converge` runs once per spec. `progress_gate.py` refuses a second `Convergence` header and a leftover git worktree. Gap tasks get one `implement` round, then
REA; still failing → `closed-carryover` and the gap becomes the next spec.

## Breadcrumbs

One line per obligation, at column 1, in `progress.md`. Bullets are not
counted.

```text
harness: L1 ok|L2 ok|…            (from scripts/harness_probe.py)
pstack: O-poteto|<host>|inline → T001–T004 verified
pstack: O-interrogate|<host>|<reviewer subagent_type> → <n> findings
rea: <feature>|pass|<ev_… id copied verbatim>
ROUTING: <role> → <model>@<level> (source: sheet|default|parent) observed: …|unknown
```

No reviewer can run → `pstack: O-interrogate|<host>|BLOCKED: independent review`,
and the Final Goal stays open.

Before "Final Goal met": `python3 <this skill>/scripts/progress_gate.py progress.md`
must print `ok`. That script is the only completion predicate. It names any
bulleted or backticked breadcrumb to rewrite, any line that looks like a secret
(write `<REDACTED>` instead), and any feature directory still missing a closing
line. Close with `rea: <feature>|pass|ev_…` or, when nothing runnable exists,
`rea: <feature>|not-applicable|<why>`. A directory that predates this Final Goal
is omitted only with `gate: exclude|<feature>|<why>`.

## REA closeout, common path

1. Use the REA MCP tools when connected, else the `rea` CLI. Missing both in
   delivery/repair → `npm install -g rea-agents@6.7.0`, then
   `rea setup --yes --client <claude_code|codex|cursor|grok_build>` for the
   active host only.
2. Pick the smallest capture for the artifact:
   - CLI or script → `capture_process_scenario` on the real command (P1 path
     and one failure path).
   - Node/Electron bundle → `analyze_javascript_application`.
   - Web app → `capture_browser_scenario` with a real P1 action and `at_end`
     `url` + `dom` or `accessibility`; a URL-only capture is not a pass.
3. Copy the Evidence ID verbatim into `progress.md` (`rea:` line) and
   `converge.md` if the feature has one.
4. Disposition, which `scripts/progress_gate.py` enforces: `pass` (ID present,
   no material finding), `not-applicable` (no runnable artifact, reason
   recorded), `tasks-appended` (material finding → one fix round, then REA
   again), `blocked-limitation` (tooling failed after an alternate path; does
   not finish). Only `pass` and `not-applicable` close the feature.

## Open the long references only when

| Need | Read |
|------|------|
| Spawning a leaf or panel on a given host; review gate details; port-only skills | [pstack-integration.md](pstack-integration.md) |
| REA install fails, web/SPA capture details, known REA failures | [rea-closeout.md](rea-closeout.md) |
| A harness layer reports a gap | [harness-layers.md](harness-layers.md) |
| Whether to spawn at all | [single-loop-default.md](single-loop-default.md) |
