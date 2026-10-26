---
description: Multi-perspective checklist for Spec Kit converge (or bug test). Not for mid-implement.
---

# Multi-Perspective Review (Converge / Bug Test Only)

Apply at feature `converge` or bug `test` — not during intermediate `implement`
or bug `fix` steps. The one independent verifier uses this as a checklist in
Thorough mode or when risk warrants it. Perspectives are lenses, not seats.

## Perspectives

### Product / User Value
- [ ] Acceptance criteria map directly to the user story / Final Goal slice.
- [ ] Happy path and at least one meaningful failure path are observable.
- [ ] No unrequested features were added.

### Engineering Feasibility & Maintainability
- [ ] Change is localized to the admitted scope.
- [ ] New code follows existing patterns (or deviation is justified in progress.md).
- [ ] Dependencies introduced are minimal and justified.

### Security & Permissions
- [ ] No secrets or credentials in code, logs, or progress.md.
- [ ] Auth / data access boundaries are unchanged or explicitly updated and tested.
- [ ] External calls or file system writes stay within approved scope.

### Operations & Reliability
- [ ] Failure modes do not leave the system inconsistent.
- [ ] The change is detectable if it fails later (log, status, or progress.md).
- [ ] Rollback path exists or the change is low-risk and reversible.

### UX / Accessibility / i18n (when relevant)
- [ ] Error / empty states defined for user-visible output.
- [ ] Accessibility or localization impact noted (or explicitly out of scope).

## Usage Rules

- Check only perspectives material to the current feature/bug.
- Record results in `progress.md` under Decisions or Open issues.
- Material gaps → append tasks and return to implement once (one converge per
  spec), or open a sibling
  feature/bug. Do not silently expand or relax acceptance.
- This is a short multi-lens pass, not a substitute for required evidence classes
  in [phase-contract.md](phase-contract.md).
- With pstack on any host: one verifier runs `interrogate` (`/interrogate` on
  Cursor, `/pstack:interrogate` on Claude, native skill on Codex) — obligation
  `O-interrogate`. Add `thermos` on the Claude/Codex port for auth, payment,
  schema, or public-API changes. Do not spawn a second reviewer to cover
  another perspective.
- Reconcile that verifier's findings into this checklist and `tasks.md`.
  Interrogate agreement alone is not Spec Kit convergence.
- With pstack present, a required review that no independent reviewer can run
  stays `BLOCKED: independent review` (recorded in `progress.md`); the feature
  stays open. Self-review, green tests, or CI do not close it.
- Only if pstack is absent: one explicit single-model self-review with the
  limit recorded. Never claim multi-model consensus. A second reviewer is
  added only by the restore procedure in
  [pstack-integration.md](pstack-integration.md#restoring-a-wider-review-panel).
