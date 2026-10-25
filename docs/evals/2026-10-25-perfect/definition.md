# Definition of "perfect" (fixed before any run against it)

agentic-sdd is perfect, for this repository's purposes, when one full run of
the matrix below passes every criterion in every run, and a second full run,
started only after the first passed, also passes. Two clean passes in a row
rule out one lucky matrix. Criteria are judged by `perfect.py` from shipped
files and transcripts, never from an agent's summary.

## Matrix (14 runs, isolated as in `../2026-10-24-single-loop-ab/run3.sh`)

| Host / model | Briefs | Runs |
|---|---|---|
| Claude Code / sonnet | todo S, kv K | 2 + 2 |
| Claude Code / opus | kv K, todo L | 2 + 2 |
| Codex / gpt-6-luna | todo S, kv K | 2 + 2 |
| Grok / grok-4.7-build (pstack absent) | todo S | 6 (amendment below) |

Cursor is out of scope: account-synced rules reach every isolated config dir.

## Criteria (every run must pass all)

| Id | Criterion | How it is judged |
|---|---|---|
| C1 | Delivers the brief | every scored black-box check passes (`measure.acceptance`; the unscored flag-position check is excluded) |
| C2 | Repository tests green | the repo's own suite exits 0 |
| C3 | Completion gate | `scripts/progress_gate.py progress.md` prints `ok` |
| C4 | Review is real | a reviewer subagent was spawned in the transcript (Claude `Agent`, Codex `collab_tool_call`, Grok `spawn_subagent`) |
| C5 | Honest finish | "Final Goal met" appears only when C3 holds |
| C6 | Right spec count | one spec when the plan has ≤ 12 tasks in total; a split only when a spec would exceed ~12 |
| C7 | One converge per spec | no `tasks.md` holds more than one Convergence phase header |
| C8 | No parked waits | no `ScheduleWakeup`, no placeholder agent (Claude transcript) |
| C9 | No leftovers | no extra git worktrees left registered in the repo |
| C10 | Bounded cost | per-cell mean at or below the 1.3.1 baseline + 15% (baseline = first matrix run) |

C10 is relative: the first matrix fixes the baseline; later fixes may not buy
correctness with more than 15% extra spend.

Amendment (after matrix 2, before matrix 3; disclosed in result.md): C10 is
judged on all runs of a cell, with at least 6 per version on Grok. Same-version
Grok runs ranged $0.86–$1.62, and a same-time pair reversed the sign of a +28%
gap seen across different hours, so 2–4 Grok runs cannot separate a 15%
change from noise.

## Loop

1. Run the matrix on the current release.
2. Any failed criterion → find the cause in the transcript, fix the skill
   (text or a check script), rerun only the failing cells until they pass.
3. Then run the full matrix again; repeat 2–3 until two consecutive full
   matrices pass with no fix in between.

## Plugin editions (added after the skill-copy bar was met)

The same bar applies to each plugin edition: two consecutive full plugin
matrices with no skill or plugin change in between. Plugin matrix per run:

| Cell | Hook-free | Guarded |
|---|---|---|
| Claude sonnet, todo S | 6 | 6 |
| Claude sonnet, kv K | 6 | 6 |
| Claude opus, kv K | 2 | 2 |
| Claude opus, todo L | 2 | 2 |
| Codex, todo S / kv K | 2 / 2 | — |

C10 generalised: a cell whose same-version cost varies by more than 15% of its
mean (coefficient of variation) is judged on at least six runs. Sonnet cells
showed 12–28%, Grok up to 25%. Codex C4 is judged from rollout files (a
subagent writes its own rollout with the run's cwd); `codex exec --json` omits
spawn events, which made the judge report two real Codex reviews as missing.
