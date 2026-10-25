# progress.md Template

Update this file after every meaningful stage.

```markdown
# Progress

## Overall
[auth: done] → [dashboard: in progress] → [notifications: waiting] | Bugs: login-crash (assessed)

## Scope for this session
[Feature dir + Spec Kit phase, or bug slug + assess|fix|test]

## Current outputs
- [path/to/file] — [short status]

## Completed
- [item] — [observed result or check status]

## Decisions
- [choice] — [brief evidence or reason]

## Open issues
- [issue] — [severity / blocker?]

## Next action
[One concrete Spec Kit phase step or bug stage]

## Last updated
[YYYY-MM-DD HH:MM]
```

Rules:
- Always keep the Overall line up to date (features + open bugs + phase).
- Keep the next action singular and Spec Kit–phase actionable.
- Reference exact file paths under the canonical spec root / `.specify/`.
- On host switches, include the handoff block from phase-contract.md.
