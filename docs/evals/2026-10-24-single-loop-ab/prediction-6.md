# Round 6 pre-registration (written before any round-6 run)

Release 1.3.0 (phase card + one-spec default) against the limits left after
round 5: one large-brief run, n = 2–3 per cell, rounds 4–5 measured on Claude
only, Cursor not isolated.

## Cells (all 1.3.0, isolated as before)

| Id | Host / model | Brief | Runs | Question |
|---|---|---|---|---|
| L | Claude / opus | todo L | 2 | Does a ~14-task goal stay in one spec, and does quality hold? |
| R | Claude / sonnet, opus | todo S (sonnet), kv K (opus) | 1 + 1 | Extra reps for rounds 4–5 |
| C | Codex / gpt-6-luna | todo S, kv K | 2 + 1 | One spec, phase card read, gate lines on Codex |
| G | Grok / grok-4.7-build | todo S | 1 | Same on Grok (pstack absent) |

Cursor stays out: account-synced User Rules still reach an isolated config
dir, and only the user can clear them.

## Predictions

1. L: both runs pass 9/9 checks. If both stay in one spec, the threshold is
   restated as "about 15 tasks" with this evidence; if either splits and still
   passes, the threshold stays.
2. R, C, G: every run writes both gate lines, spawns a reviewer, passes all
   checks, and uses one spec.
3. C, G: `pstack-integration.md` opened in at most 1 of 4 runs.

## Judgment rule

Any failure in 2 is a defect: fix the text, rerun that cell. 3 is reported.
