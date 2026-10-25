# Phase contracts

Read the section for the phase being entered. Use the installed command's exact
contract when it differs; adapt the orchestration, not the command's authority.

Execution *inside* a phase (architect / arena / swarm / interrogate / poteto
non-negotiables) is defined in [pstack-integration.md](pstack-integration.md).
That file does not change artifact ownership below.

## Artifact ownership

- **Constitution:** preserve existing principles unless a change is authorized.
- **Specify:** record the requested behavior, non-goals, and observable acceptance;
  maintain the built-in requirements checklist as the installed command allows.
- **Clarify:** resolve non-authority ambiguities from repository evidence and
  recorded assumptions;
  record agent assumptions as assumptions, never as human answers. The built-in
  requirements checklist may be reevaluated here.
- **Plan:** reuse architecture and define the smallest approach and verification
  contract. Do not create test infrastructure unless directly necessary.
- **Checklist:** evaluate requirements quality, not implementation completion.
  Custom lists are reviewer-owned. An authorized reviewer may evaluate them;
  implementation does not edit their markers or silently approve them.
- **Tasks:** derive dependency-ordered work, exact ownership, and acceptance checks
  from the admitted plan. A prerequisite must trace to an existing acceptance gap.
- **Analyze:** read-only consistency analysis. Fix problems in their owning phase,
  then rerun analysis; do not modify source as part of this command.
- **Implement:** execute admitted tasks and focused checks. Read checklist state;
  route unresolved review to the authorized reviewer instead of ticking boxes.
- **Converge:** only after implementation of current tasks. Assess spec, plan, and
  tasks; append in-scope gaps to tasks.md and return to implement once. Converge
  runs one time per spec; remaining gaps after that round carry over to the next
  numbered spec. A clean converge leaves tasks unchanged. Do not edit code, delete tasks, or broaden requirements
  in the converge command. No reviewer score declares it converged.
- **REA closeout (after clean converge, not a Spec Kit command):** orchestration
  owned by `agentic-sdd`. Mandatory MCP/CLI Evidence pass before feature close
  or Final Goal finish. Install/setup only as [rea-closeout.md](rea-closeout.md)
  allows. Material findings get one bounded fix round and REA again; no
  second converge; further findings carry over to the next spec.

## Verification contract

In the existing plan/tasks/steering artifact record only what is useful:

`acceptance ID → check/repro → required observable result → code state → result`

Record command and outcome, relevant evidence path, and any unverified boundary.
Bind evidence to HEAD plus relevant dirty/untracked state, or a content identity
for Git-free work. Invalidate affected evidence after edits. A generated test,
command, or screenshot with no behavioral assertion is not execution proof.

Use repository-mandated checks plus the smallest proof of the changed behavior.
Do not attach E2E, profiles, heap snapshots, or independent reviewers to every edit.
Mocks prove the mock boundary only; they do not establish a real provider result.

Evidence classes: **static**, **test**, **runtime**, **provider**, **unverified**.
Required classes come from acceptance and repository policy, not a universal quota.
Missing obtainable evidence enters recovery. A genuinely unavailable dependency
blocks only affected acceptance; other admitted work continues. Neither a passing
score nor a retry budget converts missing evidence into success.

## Handoff

Record compactly in existing artifacts:

```text
PROJECT / SPEC ROOT / FEATURE / PHASE
CODE STATE: revision + dirty/untracked owners, or content identity
GOAL: requested outcome; remaining acceptance IDs
DONE / NEXT: artifacts, task IDs, next owning phase
CHECKS: commands, outcomes, evidence classes, current-state binding
RECOVERY: failure class, rejected hypothesis, next discriminating action
ROUTING: requested model/effort, observed run/model/effort or unknown
BUDGET: escalation passes consumed/remaining; host capability limits
BLOCKERS: precise dependency or authority boundary, if any
RESUME: pstack resume.mjs checkpoint path (Claude/Codex port) or none
```

With pstack present, write this block via the poteto `pause-safely` playbook
(`O-pause`) and read it back via `session-pickup`; `progress.md` stays
authoritative over the checkpoint. Receiving agents verify the snapshot before writing. Unexpected revision, feature,
or ownership changes require reconciliation, not resetting another writer's work.
Refresh after an authorized exact-path phase commit. Completion requires the
original outcome, current-state required checks, and REA disposition `pass` or
`not-applicable`, then stops further expansion.
