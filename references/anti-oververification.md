---
description: Prevent infinite verification loops during Spec Kit implement; full proof at converge / bug test.
---

# Anti-Over-Verification Rules

## Core principle

Verification intensity must match the Spec Kit phase. Intermediate `implement`
steps record status for the changed task. Full acceptance evidence belongs at
`converge` (features) or bug `test` (repairs).

## Allowed during implement

- Record pass / fail / unresolved for the 1–2 most relevant acceptance IDs of
  the current task.
- Note open questions in `progress.md`.
- Continue to the next admitted task when blockers are recorded.
- Reuse still-valid passing evidence after unrelated edits.

## Forbidden during implement

- Re-running the full acceptance suite after every small change without new risk.
- Expanding the current feature to absorb mid-flight edge cases (split / new feature).
- Looping the same check until perfect before any progress (use verification_guard).
- Treating converge as a coding phase.

## Final verification (converge / bug test)

- Only after current tasks (or bug fix) are done.
- Check every required acceptance criterion for that feature/bug.
- Unmet gaps stay open: append tasks and return to implement (features) or fix (bugs).
  Do not accept residual gaps to get green.
- After a clean converge (or bug test evidence, before writing `verified`), run
  mandatory [REA closeout](rea-closeout.md). Write feature close / `verified`
  only when REA disposition is `pass` or `not-applicable`.

## Guard helper

After two unchanged attempts of the same check:

```bash
python scripts/verification_guard.py ...
```

See [verification-execution.md](verification-execution.md).

## Split triggers

Stop and split (new numbered feature or sibling bug) if:

- Intermediate verification time exceeds implementation time.
- Spec exceeds size guidance (`scripts/check-spec-size.sh`).
- The agent revisits the same criteria without new evidence.
