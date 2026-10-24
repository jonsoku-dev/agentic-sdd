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
because it cost no quality and guards a behaviour seen elsewhere (in the
2026-10-20 host matrix Tier 2 run, not isolated and in Economy mode, Claude
dispatched a `pstack:poteto-agent-low` implement leaf on `sonnet`), but no speed or cost claim is made for it.

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

## Round 2: looking for a delegating baseline, and a sonnet review gap

Scorer fix first (42e5dab): spawns whose `subagent_type` contains
`poteto-agent` or whose description names an implement packet now count as
work; round 1 numbers did not change.

### Probes on 1.1.6

| Condition | Cost | Implement leaves | Reviewer spawns | Black-box checks |
|---|---|---|---|---|
| S, "Economy cost mode", opus | $1.27 | 0 | 2 | 2/2 |
| L, "Thorough cost mode; high-risk", opus | $6.30 | 0 | 6 | 9/9 |
| S, sonnet parent | $0.57 | 0 | **0** | 2/2 |

Across five conditions and 15 runs on this host, 1.1.6 never delegated
implementation. The single-loop rule has no waste to remove here; it stays as a
guard, and no speed or cost claim is made for it.

The sonnet probe exposed a different defect: no reviewer spawned, no column-1
breadcrumbs, yet "Final Goal met".

### Sonnet: 1.2.1 vs completion gate

Candidate change: a **Completion gate** block at the top of `SKILL.md`. A
feature is not done until `progress.md` holds, at column 1,
`pstack: O-interrogate|<host>|<reviewer subagent_type> → <n> findings` naming a
reviewer actually spawned at converge (or `BLOCKED: independent review`, which
keeps the Final Goal open) and `rea: <feature>|pass|<ev_… id>`.

| Arm (sonnet) | Runs | Reviewer spawned | Review line | `rea:` pass line | Black-box checks | Mean cost |
|---|---|---|---|---|---|---|
| 1.2.1 | S×4, L×2 | **2/6** | 3/6 | 0/6 | 6/6 | $0.62 |
| gate | S×2, L×2 | **4/4** | 4/4 | 4/4 | 4/4 | $0.71 |

- 1.2.1-S-s4 wrote `pstack: O-interrogate|claude|inline → no independent
  reviewer triggered (spec has no required review)`: a self-review labelled as
  the obligation. The gate's wording ("a separate subagent, not your own
  reading of the diff") closes that reading.
- Gate reviewers found 1–7 findings per spec; the L runs appended and fixed
  in-scope ones before REA.
- Cost +15% (one extra reviewer call per spec).
- One gate run spawned a `poteto-agent-low` "Noop wait" agent to block until a
  background reviewer returned: wasteful but harmless; seen once, not acted on.

Opus regression check, gate on L once: $3.19, 617 s, 2 reviewers, 9/9 checks,
both gate lines present, 22 column-1 breadcrumbs. Within noise of the round-1
L cells.

Round 2 spend: $17.90 (probes, 10 sonnet runs, 1 opus run). Both rounds:
$47.32.
