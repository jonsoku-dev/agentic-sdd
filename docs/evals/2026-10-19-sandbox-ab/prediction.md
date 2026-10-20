# Pre-registered prediction (written before either arm finished)

Task: `todo` CLI, AC-1..AC-5, stdlib only, <200 LOC. Same brief, same Spec Kit
1.0.1 scaffold, same model (opus), same permission mode. Arm A = Spec Kit skills
only. Arm B = agentic-sdd + pstack obligations + seven harness layers + project
playbook.

## Expected synergy (what B should do that A will not)

1. L7 goal pinned first (`sharpen`): AC ids appear verbatim in spec/tasks and in
   progress.md; A will paraphrase.
2. L5 reviewer evidence: B runs `interrogate` (multi-model) and `blast-radius`
   at converge and records findings; A has no independent review at all.
3. L2 procedure discipline: B records `pstack:` / `harness:` / `ROUTING:`
   breadcrumbs and a resumable progress.md with Next action; A leaves no
   progress.md or an ad-hoc one.
4. L1 facts: B touches constitution/CLAUDE.md only for durable rules; A may
   write nothing or dump task state there.
5. Scope control (laziness protocol + "no features beyond AC"): B ships
   fewer unrequested features and stays under 200 LOC; A is more likely to add
   extras (priorities, colors, delete command).
6. Correctness on black-box AC checks: both likely pass AC-1..AC-4; B more
   likely to catch AC-3 stderr/exit-code edge via interrogate.

## Expected cost

B spends 2–4× the turns and cost of A (panels, probe, converge, REA). If B's
extra cost buys no difference in rows 2, 5, 6, the stack is overhead for a
task this small and the value claim must be scoped to larger features.

## Judgment rule

Call the stack "effective for SDD" only if B wins on at least rows 2, 3 and 6
(independent review recorded, resumable progress, black-box AC parity or
better) without violating the 200-LOC / no-extra-feature constraint. Cost
ratio is reported, not hidden.
