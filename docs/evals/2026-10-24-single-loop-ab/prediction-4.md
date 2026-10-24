# Round 4 pre-registration (written before any round-4 run)

Round 3 found every Claude run splitting a small brief into two specs (combined
6–14 tasks, under the ~12-task threshold); Codex did not split. Each extra spec
repeats converge, review, and REA. Suspected cause: `SKILL.md` says "Prefer
several short numbered specs over one long one" before stating the threshold.

## Change under test ("split")

The bullet now reads: one numbered spec per Final Goal slice by default; decide
at `tasks`; split only past ~12 tasks or two compactions; a happy path and its
error cases are one spec.

## Cells

Same runner (`run3.sh`), prompts, isolation, and models as round 3, so the
round-3 "main" runs (identical to release 1.2.3) are the baseline.

| Cell | Baseline (round 3) | Candidate |
|---|---|---|
| sonnet, todo S | g1, g2 | ×2 |
| opus, kv K | o1, o2 | ×2 |
| sonnet, kv K | s1, s2 | ×2 |

## Predictions

1. Specs per run drop from 2 to 1 in at least 5 of 6 candidate runs.
2. Mean cost per cell drops at least 20%.
3. No regression: every candidate run passes all black-box checks, writes both
   gate lines, and spawns a reviewer.

## Judgment rule

Keep the change if 1 and 3 hold. Report 2 as measured; if 2 fails while 1
holds, the split was not where the cost was, and that is the finding.
