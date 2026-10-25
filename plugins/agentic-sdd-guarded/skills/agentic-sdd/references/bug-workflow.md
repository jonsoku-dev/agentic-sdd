---
description: Spec Kit bug workflow — assess → fix → test.
---

# Bug Fix Workflow

Use when existing behavior is broken. Do not run the full feature delivery cycle
first unless the "bug" is actually new scope.

Artifacts live in `.specify/bugs/<slug>/`.

Prefer installed commands when present (`speckit.bug.assess` / `.fix` / `.test`
or the project's equivalent). This document is the file contract when those
commands are unavailable (including Grok Build file-based mode).

## Stages

### 1. Assess (no code changes)

With pstack: `how` over the affected subsystem and `why` for regression history
(`O-why`); reproduce on the real surface first. Assessment stays read-only.

- Input: symptom, reproduction, expected vs actual, issue URL / stack trace.
- Output: `.specify/bugs/<slug>/assessment.md`
- Content: verdict (`real` / `invalid` / `needs-clarification`), suspected paths,
  proposed remediation, scope.

### 2. Fix (only stage that edits code)

- Apply only the assessed remediation.
- Stay within listed files unless new evidence requires expansion (log under Deviations).
- Output: `.specify/bugs/<slug>/fix.md`
- Include exact file changes and any added tests.

### 3. Test (no code changes to force pass)

- Re-run original reproduction and relevant tests.
- Output: `.specify/bugs/<slug>/test.md`
- Verdict: `verified` | `partial` | `failed`
- Missing verification is not success. Failed tests return to diagnosis/fix.

## Scaffold helper

```bash
scripts/init-bug-dir.sh <slug> --project /path/to/repo
```

Prefer `specify extension add bug` (user-authorized) via
`setup-speckit-multi-agent --with-bug` when setting up a project.

## Templates

**assessment.md**
```markdown
# Bug Assessment: <slug>

- **Verdict**: real | invalid | needs-clarification
- **Symptom**: 
- **Suspected paths**: 
- **Proposed remediation**: 
- **Scope**: 
```

**fix.md**
```markdown
# Bug Fix: <slug>

- **Status**: applied | partial | not-applied
- **Changes**:
  | File | Change |
  |------|--------|
- **Deviations from Assessment**: 
```

**test.md**
```markdown
# Bug Test: <slug>

- **Verdict**: verified | partial | failed
- **Reproduction result**: 
- **Tests run**: 
- **Evidence**: 
```

## Rules

- Assessment and test are evidence, not permission to edit unrelated files.
- Intermediate checks stay light during Fix; strong verification belongs in Test.
- Update root `progress.md` when a bug is opened or closed.
- Apply [phase-contract](phase-contract.md) verification evidence classes on Test.
- Use [recovery](recovery.md) after two failed Test cycles without new evidence.
- Do **not** write verdict `verified` until REA closeout on the fix surface is
  `pass` or `not-applicable` ([rea-closeout.md](rea-closeout.md)). A material
  REA finding returns to Fix, then Test, then REA on the new code state. Record
  the REA block in `test.md`. Do not append feature `tasks.md` unless the defect
  is new out-of-bug scope.
