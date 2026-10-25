---
description: Edge cases and recovery patterns for Spec Kit Agentic SDD.
---

# Edge Cases & Failure Modes

## Classification ambiguity

Under `/agentic-sdd` delivery/repair, prefer a recorded default over a quiz.
Ask once and set `blocked` only when two readings imply incompatible Final Goals
and artifacts/user text give no dominant reading — or when a hard boundary applies.

| Situation | Action |
|-----------|--------|
| Request mixes new feature + bug fix | Pick primary from wording + evidence (fix if existing behavior is broken; else feature). Record assumption in `progress.md`. Ask only if both readings are equally strong and incompatible |
| No clear acceptance | Enter `clarify`; derive 1–2 observable outcomes from repo + Final Goal; record as assumptions — do not invent product scope. Block only if no observable outcome can be stated |
| User says "just do it" / full autonomy | Still use Spec Kit for non-trivial work; list assumptions in Notes; no phase quiz |
| Requirements change mid-implement | New numbered feature or bug — do not silently expand current feature |
| Trivial typo/docs-only | Opt-in light path only (see SKILL.md); otherwise full Spec Kit |

## Partial failure & recovery

- **Interrupted write**: Record intended change set in `progress.md` before multi-file edits. On resume, verify what landed.
- **Tool failure mid-step**: Record exact error, last good path, next safe action. Do not retry unchanged.
- **progress.md missing**: Recreate from feature artifacts + git status; note handoff loss.
- **Conflicting instructions**: Prefer current feature artifacts > `progress.md` > project instructions; ask if unclear.
- **Flaky check**: Mark unresolved; do not loop. Full investigation at converge / bug test.
- **Host switch mid-feature**: Flush handoff, capture dirty owners, activate when supported, verify snapshot.

## Spec Kit / host gaps

- **No Spec Kit installed**: Stop mutating; point user to `setup-speckit-multi-agent`.
- **Grok without slash commands**: Execute phase contracts on shared files; name the phase in `progress.md`.
- **Integration missing for one host**: Do not fork specs; use shared `.specify/` only.
- **Branch vs feature mismatch**: Reconcile pointer before continuing (see setup skill `sdd` report).

## Security & destructive operations

- Never commit secrets. Stop and report the path if discovered.
- Destructive ops require explicit confirmation in the current session; record it.
- External network / publish steps must be in-scope or explicitly approved.
- When permission is unclear, stop affected mutation and ask.

## Multi-perspective gaps (at converge)

Briefly note status against:

- User value vs acceptance
- Security / permissions
- Failure states
- Observability
- Reversibility

Unknown material items become open issues — not silent passes.

## When to stop and ask

- Classification still ambiguous after reading context.
- Change touches paths outside admitted scope.
- Required evidence blocked by missing credentials/external systems.
- Same bounded step failed twice without new evidence.
- Prior rejection of a similar approach is recorded.

Do not quiz on every small reversible decision; record assumptions and continue.
