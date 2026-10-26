---
extends: feature, bug-fix
when: Any feature, bug, or multi-file change in a repository that has a Spec Kit `.specify/` directory, or any request that names agentic-sdd, Spec Kit, a numbered feature, or a Final Goal.
---

# agentic-sdd (Spec Kit owns the phases)

This repository runs Spec Kit through the `agentic-sdd` skill. pstack playbooks
execute *inside* an admitted Spec Kit phase; they do not replace
`specify → plan → tasks → implement → converge → REA closeout`.
Implement runs inline. Spawn a leaf only for a `bloat`, `parallel`, or `conflict` trigger. Paste the phase-card spawn brief into that prompt. This playbook does not apply inside the subagent.

- **Before** "`how` over the affected subsystem." resolve the Spec Kit project
  (nearest `.specify/`), the active numbered feature, and its phase from the
  feature artifacts and `progress.md`. Load the `agentic-sdd` skill and its
  `references/pstack-integration.md`. If the phase is not `implement`, hand
  off to the owning Spec Kit phase command and stop this playbook here; the
  phase's own obligation (`O-architect`, `O-interrogate`, …) runs pstack skills
  from there. If the phase is `implement`, continue the Feature playbook as the
  `O-poteto` batch for the admitted task IDs only, with `tasks.md` as the todo
  source of truth.
- **Before** "Reproduce it yourself on the matching surface via the driver skill" resolve the
  Spec Kit bug slug under `.specify/bugs/<slug>/` and its stage
  (`assess` / `fix` / `test`). Assessment writes no code: run `how` and `why`
  (`O-why`) and stop this playbook after `assessment.md` is written. Only the
  `fix` stage continues the Bug fix playbook, scoped to the assessed paths.
- **Before** "Run **Opening a PR**." record `pstack: O-poteto|<host>|<skill> → <task ids> verified`
  in `progress.md`, then return to the Spec Kit sequence: `converge` (with
  `O-blast`, `O-hygiene`, `O-interrogate`), then REA closeout. Open the PR only
  when the Final Goal or the repository's commit policy says so; stop this
  playbook here.
