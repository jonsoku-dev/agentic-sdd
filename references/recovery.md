# Collaborative recovery without scope drift

Use for repeated failure, conflicting evidence, or verification that is starting
to expand the product. A retry threshold triggers a change of method, not an
arbitrary end to the user's goal. Clear small failures can be fixed directly.

## Detect verification loops by evidence, not elapsed time alone

Before a verification batch, name the acceptance condition it can establish and
what result would change the next action. Use existing commands and checkpoints.
If it establishes neither a required condition nor resolves a specific uncertainty,
skip that optional check and do the next admitted delivery task.

Reuse a passing result when its relevant implementation, inputs, environment,
test/oracle, and required freshness have not changed. A documentation-only edit
does not by itself invalidate UI evidence. Shared dependency/token/schema changes
can invalidate many consumers; do not pretend those are isolated. Run narrow
checks during repair, then the required integration/full matrix at its declared
checkpoint once the relevant batch stabilizes. Repository-mandated cadence wins.

**Progress** means new valid acceptance evidence, a concrete in-scope defect found,
a defect repaired, or an observation that eliminates a live hypothesis. A new
screenshot filename, larger report, repeated green run, reviewer agreement, model
switch, or higher reviewer confidence alone is not progress. Slow work that is reducing
real gaps is not a verification loop.

After two attempts of the same check with no such progress, or an earlier sign
of scope drift, enter the checkpoint below instead of another same-state run.
With pstack present, two failed fixes sharing one premise trigger
`principle-attack-the-premise`: write the premise down and test it directly
before another fix; use `why` for regression history.
Count each check separately: progress in another check cannot clear its loop,
and one stuck check cannot block an independent check that has not run yet.
After a real implementation/input/environment/oracle change, allow the first
observation on that basis; if the same failure persists, its loop history remains.
An attempt can include a batch of checks; do not instrument every tool call. Carry
this history across reviewer/model changes and compaction. Record only:

`acceptance → last outcome → evidence/diagnosis delta → chosen next action`

Count attempts from the record with code, not by estimate. This
threshold changes the method, not the required checks or the overall goal.

## Bound the whole feature, not only one check

`converge` runs once per spec. After its single bounded fix round, reconcile
a complete remaining-gap list in the existing tasks/steering artifact and move
it into the next, smaller numbered spec (`closed-carryover`) instead of another
converge: `acceptance ID → concrete defect/missing evidence → owner → smallest
repair/observation → affected checks`. Group duplicate findings. Keep required
failures open; move unrelated discoveries to separately admitted future work.
A changing score without new evidence is not a new gap. Keep closed bundles closed
unless a concrete defect or relevant source change invalidates their evidence.
Report open blocking defects and missing required evidence, not task percentage.

Before an expensive full matrix, state which relevant inputs changed and why
those changes invalidate the full scope. Prefer per-case evidence reuse when
only a story or review classification changed. Shared tokens, dependencies,
fixtures, oracle behavior or a declared final integration checkpoint can justify
a full run. `run_check` permits execution; it does not choose the cheapest scope.
Preserve failed commands. A missing manual-review row may be resolved by a separate
review of its preserved raw evidence without pretending the failed command passed.

Use a stable logical check ID and recipe across attempts. Output folder names and
new timestamps are not new acceptance checkpoints. Keep generated evidence out
of source basis; use the runner's snapshots for run-specific artifacts. If a
recipe truly changes, retain its history and inspect the affected evidence.

Keep one current checkpoint in the existing feature steering artifact. Other
handoff/roadmap documents link to it instead of duplicating live counts. Date and
label historical receipts so compaction cannot promote them to current state.

## Evidence-backed guard and execution

Use `scripts/verification_guard.py --state progress.json --evidence-root PROJECT`
for read-only judgment before an expensive/repeated check. Use the collector in
[verification execution](verification-execution.md) for actual approved commands.
It records process results and source/log/artifact hashes and enforces the guard
before execution. Do not fabricate a pass entry or its hashes to reuse evidence.

A missing/changed receipt, log, declared artifact, source, command, or declared
environment invalidates reuse. `required_gaps` stays open. `repair_state` means
repair current metadata/recipe, not run the same test again. `run_check` permits
the admitted check; `recover` requires a different action; `reuse_pass` avoids
only a redundant check. None declares the full product complete.

Keep old records even when their checkpoint or evidence is unavailable. An
unscoped historical `always` pass never satisfies the current checkpoint; it
appears in `legacy_unscoped_history` and a fresh current run may proceed. Missing
metadata for an unselected optional check does not block unrelated required work.
Never guess historical IDs or discard failures. Only a selected `always` check
with no CURRENT checkpoint needs `repair_state` before it can run.

Per-check counters prevent one stuck check from blocking fresh independent work,
or another check's success from hiding its loop. A real basis change permits its
first check; an unchanged repeated failure remains a recovery signal. For an
`always` check, a verified pass within the current checkpoint can be reused;
a new actual CI/release/batch checkpoint requires fresh evidence.

A new adapter/monitor is allowed when an existing path cannot obtain required
proof or retain progress state. Record its necessity, bounded ownership, and
acceptance. Extend an existing runner first; framework work is a prerequisite
of the original goal, never a new implicit product goal.

## Progress checkpoint: choose once, perform one action

Write down the original goal, remaining acceptance, the last two attempts and their
computed per-check/aggregate counts, validity of existing evidence, current failure, and
an enumerated set of actions. Decide `verification_loop` and `next_move` from
those facts in one pass; pick model/effort for the chosen action at the same time.

Choose only an action supported by the current facts:

- **resume_delivery:** reuse sufficient valid evidence and implement the next
  admitted task; finish only if the original goal and all required gates are met.
- **targeted_check:** make one observation that separates named hypotheses or
  supplies a missing required result; name the predicted difference first.
- **repair_product:** fix a reproduced defect in the owning implementation phase,
  then rerun the affected acceptance check.
- **repair_harness:** use an existing supported tool/environment path or correct a
  demonstrated oracle defect without changing the intended product condition.
  Harness work must be a necessary, bounded prerequisite, not a new platform.
- **external_block:** record a concrete unavailable dependency/authority boundary
  after relevant alternatives were checked; continue other admitted work.

A high loop score rejects the redundant proposed check; it does not waive a failed
required gate. The primary decides from these facts and rules. Do not summon more
reviewers or change models without new evidence. One independent challenger can help resolve a real conflict;
otherwise make the smallest discriminating observation and proceed.

Execute the chosen action before the next judgment. If it fails with no delta,
exclude that unchanged approach and choose a materially different hypothesis or
available path. Do not reset the counter by renaming a check. Stop only the
nonproductive verification branch, not the original delivery objective. Never
change an assertion merely to make a failure disappear.

## Diagnose before adding work

Classify with evidence, keeping uncertainty explicit:

- **Change defect:** reproduce the failure in the changed path; fix in implement.
- **Existing defect:** compare against a safe baseline when useful. Repair only if
  it is a necessary prerequisite for original acceptance; otherwise report it
  separately. Do not waive a required gate just because it previously failed.
- **Environment/tool gap:** repair the owned local setup or use an equivalent
  supported observation path. Do not alter product behavior for tool convenience.
- **Requirement/test conflict:** distinguish an incorrect test from a real defect.
  Reconcile the owning artifact without weakening the original outcome.
- **Authority/external block:** identify the missing authorization, ownership, or
  dependency. Do not make it disappear with a score or majority vote.

A prerequisite is admitted only when it names the original acceptance ID, shows
why that condition cannot pass without it, and is the smallest compatible repair
within authorized scope. Record its task and evidence. A broad refactor, new
framework, or new product behavior is not automatically a prerequisite.

## Deliberate briefly, then act

1. The primary pins goal, current code state, failed check, and the next uncertainty.
   Give one independent reviewer the raw relevant evidence and bounded question.
   Request their diagnosis before showing the primary's preferred explanation.
2. Compare hypotheses and at most a few concrete alternatives. Collaborators
   advise; the primary retains the decision. Use another specialist only if an
   unresolved consequential disagreement warrants it. No standing committee.
3. Make the direction/model/effort choice once from the enumerated options.
   Arithmetic and permission decisions are never delegated to a reviewer.
   Record the reason the evidence supports the chosen action.
4. If diagnoses disagree, run the smallest reversible observation that distinguishes
   them. Consensus means an actionable hypothesis supported by evidence, not
   unanimity or repeated voting. Do not wait for every agent to agree.
5. Apply one scoped action in its owning phase, then rerun the original affected
   check. Continue until acceptance is met. If a test was wrong, document the
   contradiction and use a corrected check of the same intended behavior.

One writer per checkout. Reviewers do not concurrently fix the worker's files.
With limited slots, serialize review. If delegation fails or is unavailable,
perform an explicit counter-hypothesis review in the primary and disclose that
independent consensus was unavailable; continue useful authorized work.

## Prevent both drift and abandonment

Track only `failure → hypothesis → action → observation → next` in the existing
artifact. A repeated action with the same result and no new evidence changes
hypothesis, tool path, or assignee. Increasing effort is appropriate for reasoning
difficulty, not missing credentials, unsupported tools, or a broken environment.
Once uncertainty resolves, return to the lowest capable model/effort.

A local retry cap cannot end the overall task. Explicit user/runtime budgets still
apply: preserve a resumable handoff if those prevent further work. An affected path
can be blocked only by a concrete unsatisfied dependency/authority boundary after
relevant available alternatives were checked. Continue independent admitted tasks;
when no useful work remains, report the exact needed input and remaining acceptance.
Do not poll, invent tasks, bypass required gates, or claim completion to avoid a stop.

When original acceptance and required checks pass, stop expanding verification.
Resume a passing check only after new changes, failures, or a concrete unresolved
risk justify it. No new validation platform is required by this recovery procedure.
