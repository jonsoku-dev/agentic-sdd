# Result: the "perfect" bar is met

Definition, criteria C1–C10, and the judge were committed before any matrix
(`definition.md`, `perfect.py`, 24aaecc). Every verdict below comes from
`perfect.py` over shipped files, transcripts, and Grok session logs.

| Matrix | Version | Runs | Verdict | Failures |
|---|---|---|---|---|
| m1 | 1.3.1 | 14 (+2 Grok later for C10) | FAIL | Claude sonnet kv: C8, `ScheduleWakeup` "fallback heartbeat" kept the headless session alive (119 s active, 1335 s wall). Grok gk1 C4 was a judge bug: Grok's `-p` JSON omits tool calls; the session log shows 3 `spawn_subagent` calls |
| fix | 632247f | — | — | SKILL.md and the phase card forbid the heartbeat wakeup and tell Claude to pass `run_in_background: false`; the judge reads Grok session logs |
| m2 | fx1 (632247f) | 16 + 4 Grok | **PASS** | C10 first failed on Grok (+39%, n = 2); see amendment |
| m3 | fx1, unchanged | 18 | **PASS** | none |

Two consecutive full matrices passed with no fix in between, which is the bar.

## C10 amendment (disclosed)

After m2, Grok's cost looked 28–39% higher than 1.3.1 with n = 2–4 per arm.
Same-version Grok runs ranged $0.86–$1.62, and a same-time pair reversed the
sign ($1.60 for 1.3.1 vs $1.34 for fx1). With six runs per arm the gap was +10%
($1.34 vs $1.47), inside the 15% bound. `definition.md` now requires six Grok
runs per version for C10, and the matrix runs six; m3 met it at $1.48.

## Cell means (m3 vs m1 baseline)

| Cell | m1 (1.3.1) | m3 (fx1) |
|---|---|---|
| Claude opus, todo L | $2.13 | $2.27 (+7%) |
| Claude opus, kv K | $1.88 | $2.02 (+7%) |
| Claude sonnet, todo S | $0.66 | $0.59 |
| Claude sonnet, kv K | $0.60 | $0.65 (+8%) |
| Grok, todo S (n = 6) | $1.34 | $1.48 (+10%) |
| Codex | subscription | subscription |

## What "perfect" does not cover

- Cursor (account rules cannot be isolated; skipped by the user's decision).
- Hosts other than Claude Code, Codex, and Grok; models other than the four used.
- Briefs other than the three small/medium CLI features in two repositories.
- Enforcement still relies on the model running `progress_gate.py`; nothing
  stops a session that ignores the instruction. A plugin with harness hooks
  is the next step.

Spend: m1 $18.57, m2 $20.12, m3 $19.95, total $58.64 (Codex on subscription).

## Plugin editions: the bar is met

Editions: `agentic-sdd` (hook-free; Claude Code and Codex) and
`agentic-sdd-guarded` (Claude Code hooks). Workspace rebuilt with `setup.sh`
after the scratch data was lost; plugin matrix as in `definition.md` (44 runs
each). Final version bfea069.

| Matrix | Runs | C1–C9 | Notes |
|---|---|---|---|
| attempt at 101d02c | 44 + extras | 1 real defect | a Codex run left two leaf worktrees registered (C9) → fixed in bfea069 |
| pm1 (bfea069) | 44 | 44/44 | baseline |
| pm2 (bfea069) | 44 | 44/44 | C10 vs pm1 flagged opus cells |
| pm3 (bfea069) | 44 | 44/44 | C10 vs pm1 flagged opus L |

All three matrices ran the same version, so their C10 differences are noise
(opus L ranged $1.62–$2.93 per run; pm1's median happened to be low). C10 as
intended, the fixed version against the version before the fix, pooled
medians:

| Cell | Before (101d02c) | After (bfea069) | Change |
|---|---|---|---|
| opus todo L, hook-free | n=12 $2.24 | n=18 $2.39 | +7% |
| opus todo L, guarded | n=12 $2.07 | n=18 $2.27 | +9% |
| opus kv K, hook-free | n=5 $2.07 | n=6 $1.88 | −9% |
| opus kv K, guarded | n=5 $2.30 | n=6 $2.02 | −12% |
| sonnet todo S, hook-free | n=18 $0.62 | n=18 $0.65 | +6% |
| sonnet todo S, guarded | n=18 $0.62 | n=18 $0.64 | +3% |
| sonnet kv K, hook-free | n=18 $0.73 | n=18 $0.71 | −2% |
| sonnet kv K, guarded | n=18 $0.76 | n=18 $0.74 | −3% |

Both editions pass C1–C10. Fixes found on the way, all before bfea069: a
self-review no longer fills the review line; a user ban on subagents keeps the
Final Goal open (adversarial runs: 4 of 9 dishonest before, 10 of 10 honest
after); "Final Goal NOT met" no longer reads as a claim; invoking the skill
counts as the reviewer request on Codex; leaf worktrees are removed after
merge. Judge corrections disclosed: Codex spawns are read from rollout files,
the kv checker uses a 3 s TTL, C10 uses medians and compares versions.
