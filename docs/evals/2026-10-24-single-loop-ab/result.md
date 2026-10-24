# Single-loop A/B result: 1.1.6 vs 1.2.0, then a 1.2.1 candidate

Run 2026-10-24 on one Mac, Claude Code 2.1.304, model `opus`, pstack 0.9.94,
rea-agents 6.7.0. Isolation, briefs, predictions, and the judgment rule were
committed before any run (`prediction.md`, 756bbb9); the scorer before any
result was read (`measure.py`, c48166e). Every number below comes from
`measure.py` over transcripts and shipped files, never from an agent's summary.
n = 2 per cell.

## 1.1.6 vs 1.2.0

| Cell | Cost (each, mean) | Active time (each, mean) | Wall (each) | Implement leaves | Reviewers | Black-box checks |
|---|---|---|---|---|---|---|
| S 1.1.6 | $1.88, $1.69 → $1.79 | 309 s, 242 s → 276 s | 311 s, 245 s | 0, 0 | 2, 2 | 2/2, 2/2 |
| S 1.2.0 | $2.22, $1.70 → $1.96 | 361 s, 260 s → 311 s | 364 s, 263 s | 0, 0 | 2, 2 | 2/2, 2/2 |
| L 1.1.6 | $2.51, $2.83 → $2.67 | 398 s, 463 s → 431 s | 401 s, 525 s | 0, 0 | 2, 4 | 8/8, 8/8 |
| L 1.2.0 | $4.09, $2.89 → $3.49 | 577 s, 519 s → 548 s | **1734 s**, 522 s | 0, 0 | 4, 2 | 8/8, 8/8 |

All eight runs: tests green, one `converge.md` per spec, REA evidence ids
recorded, Final Goal marked met.

Predictions:

1. **Fewer implement-leaf spawns: premise false.** 1.1.6 spawned no implement
   leaf in any run; the parent already implemented inline ("Economy: done in
   parent, no leaf"). There was nothing for 1.2.0 to remove.
2. **Wall time −20% on S: not met** (+13%, inside noise).
3. **Cost −15%: not met** (S +10%, L +31%; the L gap is one outlier, below).
4. **No acceptance regression: met** on the pre-registered checks.
5. **Review independence kept: met** (2–4 reviewer spawns in every run).
6. **`inline` / trigger in `pstack: O-poteto` lines: not met** — no 1.2.0 run
   wrote a column-1 `O-poteto` line, and no 1.2.0 run opened
   `single-loop-default.md`. Only the `SKILL.md` text reached the model.

Judgment (pre-registered rule): 4 and 5 hold, 2 and 3 do not, so the
single-loop change **bought nothing measurable on these briefs**. It is kept
because it cost no quality and guards a behaviour seen elsewhere (the
2026-10-20 host matrix shows Claude dispatching a `poteto-agent-medium` leaf for
a comparable feature), but no speed or cost claim is made for it.

### Two defects the runs exposed (present in both versions)

- **Parked critical path.** 1.2.0-L-1 launched its converge reviewers with
  `run_in_background: true`, then called `ScheduleWakeup` (1200 s) four times
  and idled: 577 s of model time, 1734 s wall. The background dispatch came from
  the Claude row of pstack-integration's Leaf dispatch table, which both
  versions carry. Background reviewer launches appeared in 5 of 8 runs.
- **Uncounted breadcrumbs.** 6 of 8 runs wrote `- pstack: …` bullets or no
  breadcrumbs at all; `harness_probe.py` L7 and this scorer count only lines
  that start at column 1. The rule lived in `pstack-integration.md`, which runs
  read only partway.

## 1.2.1 candidate (fixes for the two defects)

Changes: `SKILL.md` states the column-1 breadcrumb form with an example and
says to launch gating reviewers/leaves together in the foreground, never behind
`ScheduleWakeup`, sleep, or polling; the Claude dispatch row in
`pstack-integration.md` drops the unconditional `run_in_background: true`;
`single-loop-default.md` gains "Waiting on a subagent".

| Cell | Cost | Active / wall | Background spawns | Wakeups | Column-1 / bulleted breadcrumbs | Black-box checks |
|---|---|---|---|---|---|---|
| S rc-1 | $1.83 | 219 s / 222 s | 0 | 0 | 13 / 0 | 2/2 |
| S rc-2 | $2.16 | 295 s / 298 s | 0 | 0 | 19 / 0 | 2/2 |
| L rc-1 | $3.07 | 599 s / 602 s | 0 | 0 | 28 / 0 | 8/8 |
| L rc-2 | $2.56 | 396 s / 416 s | 0 | 0 | 24 / 0 | 8/8 |

- Breadcrumbs: column-1 lines in 4/4 runs (before: 2/8), each with an
  `O-poteto|claude|inline → <task ids> verified` line.
- Background launches 0/4 (before: 5/8); wakeups 0/4 (before: 1/8); wall time
  now equals active time within 20 s.
- Cost and time: S mean $2.00 / 257 s, L mean $2.82 / 498 s — within noise of
  1.1.6 and 1.2.0 (n = 2).
- Quality: all pre-registered checks pass.

## Disclosed scorer change

After the first scoring pass, the large-brief check `add --priority 1 high --due
2000-01-01` was split: the scored check now puts flags before the text, and a
separate unscored check `extra_flags_after_text` tries `add late --priority 2`.
The brief does not fix flag position. Results for that extra check: 1.1.6 2/2,
1.2.0 1/2, candidate 0/2. Each failing run's own spec documents "flags are
parsed only before the first non-flag word" as an assumption, so this is brief
ambiguity resolved differently per run, not a regression against the brief. It
does not enter the judgment.

## Limits

- n = 2 per cell, one host (Claude Code), one model, two small briefs on one
  50-line CLI. Differences under about 15% are noise here.
- The 1.1.6 baseline never delegated implementation, so the experiment could not
  test the single-loop rule against a harness that over-delegates.
- Total spend for 12 runs: $29.42 (sum of `total_cost_usd`).
