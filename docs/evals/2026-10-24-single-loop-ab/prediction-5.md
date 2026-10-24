# Round 5 pre-registration (written before any round-5 run)

Lever: progressive disclosure. In round 3, Claude runs read `rea-closeout.md`
(9 KB) in 7 of 8 runs and `pstack-integration.md` (23 KB) in 5 of 8, on top of
the always-loaded `SKILL.md` (16 KB), and used mostly the phase→obligation
table and the common REA path.

## Change under test ("card")

New `references/phase-card.md` (3.9 KB): required obligation rows, breadcrumb
lines, the common REA path, and a table saying when to open the long
references. `SKILL.md` first action 6 and its other pointers now name the card
first; the long references stay for dispatch detail, REA failures, and web
capture.

## Cells

Baseline: the round-4 "split" runs (same runner, prompts, models).

| Cell | Baseline | Candidate |
|---|---|---|
| sonnet, todo S | p1, p2 | ×2 |
| opus, kv K | p1, p2 | ×2 |
| sonnet, kv K | sp1, sp2 | ×2 |

## Predictions

1. Runs that open `pstack-integration.md` fall to at most 1 of 6; runs that
   open `rea-closeout.md` fall to at most 2 of 6.
2. Mean cache-read tokens per cell drop at least 10%.
3. No regression: every run passes all black-box checks, writes both gate
   lines, spawns a reviewer, and records an `O-poteto` breadcrumb.

## Judgment rule

Keep the card if 1 and 3 hold. Report 2 and cost as measured. If 3 fails, the
long references carried something the card lacks: add it to the card and rerun
the failing cell.
