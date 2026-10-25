# Direction keeping

Read when steering a phase, recovering, or advancing to the next feature. Pin the
Final Goal in existing `steering.md` or the project's equivalent artifact. Keep
admitted acceptance and non-goals stable; implementation discovery may change the
method or reveal a necessary prerequisite, not authorize a new product outcome.

## Phase and recovery gate

At each meaningful phase transition or recovery decision, enumerate concrete next
moves and pick child model/effort as described in model-routing.md. Judge each
move against goal, current artifacts/evidence, and constraints on these heads:

- `next_move`: continue, repair, investigate, reconcile_artifacts, or external_block.
- `in_scope`: the next action serves an admitted acceptance condition.
- `invented`: the proposal introduces unrelated behavior or verification machinery.
- `authority_conflict`: the proposal violates an unresolved authority boundary.
- `recoverable`: missing evidence can be obtained within available authority/tools.
- At a no-progress checkpoint, `verification_loop`: the proposed check repeats
  valid evidence or unchanged failure without resolving a named uncertainty.
  Use the recovery reference's concrete actions for `next_move`: resume_delivery,
  targeted_check, repair_product, repair_harness, external_block.

Compute counts and costs with code first. No reviewer grants authorization or
attests unrun tests. When a real fork remains after the written rules, use one
independent pstack reviewer (`interrogate` / `arena`); otherwise primary judgment,
recorded, and continue.

A blocking authority/out-of-scope check at probability >= 0.7 overrides a continue
label. Reject that action and choose an in-scope path; it does not automatically
stop unrelated admitted work. Missing obtainable evidence routes to recovery.
At the recovery no-progress checkpoint, include the original goal, remaining
acceptance, recent attempt outcomes, evidence validity, and the compact
`verification_guard.py` result in state. Its count is computed from the complete
checkpoint history. Use the declared evidence root so file/source integrity is
checked before reuse; a legacy self-report cannot establish a pass. Use
the selected-check counter to diagnose its loop, without masking it with another
check's progress or blocking fresh independent checks. For `always` checks, only
the actual current checkpoint's result satisfies its cadence. A loop finding at probability >= 0.7 rejects the
redundant check, not its underlying requirement. Execute one selected action
before asking again. Do not re-score unchanged evidence or invalidate passing
checks merely because another agent wants its own receipt.
For `review`/`abstain`/`uncertain`, inspect the evidence and act under the written
rule. Low confidence is not a reason to keep re-judging: use the least disruptive
admissible action or a discriminating check.

Record the chosen action and reason, actual check outcome,
and requested/observed routing. Then execute; do not substitute a receipt for
work. Invoke the recovery reference when a real disagreement needs collaborators.

## Acceptance coverage before advancing

Converge runs once per spec. Gaps that survive its single fix round become the
next numbered spec's scope (`closed-carryover`); do not reopen converge on the
current spec.

After installed `converge` reports converged, run REA closeout before the next
feature or finish ([rea-closeout.md](rea-closeout.md)). Continue admitted Final
Goal work when any acceptance or REA disposition is still open (`tasks-appended`
or `blocked-limitation` are not finish).

After installed `converge` reports converged, reconcile the full spec's acceptance
conditions with the check inventory. `criterion_gate.py` extracts English listed
Given/When/Then scenarios, not every prose requirement, success metric, or language.
For other formats or additional criteria, provide the COMPLETE reviewed list as
`[{"id":"AC-1","text":"..."}, ...]` using `--criteria-file`. Do not silently
narrow coverage to what a regex recognizes or replace the canonical spec.

```sh
python scripts/criterion_gate.py questions --spec path/to/spec.md
# For more than 64 criteria, use --batch 1, --batch 2, ...; preserve all IDs.
python scripts/criterion_gate.py decide --spec path/to/spec.md \
  --answers-file criterion-answers.json
```

`--criteria-file` replaces `--spec` in either command. Enumerate the complete
reviewed list, including prose requirements, before execution. An independent
reviewer may examine changed or uncertain criteria in bounded evidence packets; completeness is checked
against the full list, not by repeatedly rescoring every passing criterion.

`decide` now requires `--review-file review.json --evidence-root PROJECT` before
it can return `advance=true`. Scores-only callers receive `advance=false` with
`evidence_review_required`; old score files remain historical advisory data.
`--answers-file` is optional; the primary's own adjudication may be used. A low score asks the primary
to inspect a named uncertainty; it is not a reproduced defect or a new task.
Resolve it once against the source and actual check evidence. Record the concrete
reason; retain unmet/blocked for real gaps. Respect reviewer-owned decisions.

The review is a compact index in the existing feature evidence directory:

```json
{
  "criteria_digest": "digest returned by a scores-only decide call",
  "reviewer": "authorized primary or reviewer identity",
  "decisions": [{
    "id": "AC-1",
    "status": "met",
    "reason": "Current reload test observed the same saved value.",
    "basis": [{"path": "src/store.py", "sha256": "actual 64-character hash"}],
    "evidence": [{"path": "proofs/save.json", "sha256": "actual 64-character hash"}]
  }]
}
```

Every criterion appears exactly once. Status is `met`, `unmet`, or `blocked`.
For `met`, include the relevant implementation, input, dependency/environment
manifest and oracle files in `basis`, plus actual receipts/results in `evidence`.
Use root-relative paths and real hashes. The helper validates complete coverage,
criteria identity, path confinement and current content hashes; it does not prove
that an assertion is meaningful or a reviewer's claim is true. The authorized
reviewer must read the evidence. Never fabricate an adjudication to defeat a gate.
Unknown/missing/duplicate IDs and stale references fail closed.

Reuse a previously reviewed criterion while its acceptance and relevant basis
remain valid. New evidence for another criterion does not reopen it. A changed
criterion list requires reconciliation with the new digest, not automatic reruns
of unaffected behavior. Explicitly record the concrete defect or affected basis
that reopens a met item. Numeric confidence alone is insufficient.

Exit codes: 0 reviewed coverage passes, 1 review/gaps remain, 2 invalid input or
stale evidence. `completion_decided=false` always: required checks, actual
convergence, reviewer authority, and merge/release gates remain separate. A review
index is not a security attestation and never replaces raw execution receipts.
If REA is `pass` or `not-applicable` and no admitted Final Goal work remains,
finish. If work remains, specify the next feature. Never finish on
`blocked-limitation` or `tasks-appended`.

## Clarification and checklist authority

Resolve ordinary implementation ambiguity with evidence and recorded assumptions,
not pretend human answers. Repair requirements gaps in specify/clarify, design
gaps in plan, and task gaps in tasks. Analyze stays read-only; converge stays
append-only. Custom checklist reviews go to their authorized owner. An explicitly
human-owned decision cannot be forged by an agent or reviewer; complete all independent
work before requesting the specific missing input.
