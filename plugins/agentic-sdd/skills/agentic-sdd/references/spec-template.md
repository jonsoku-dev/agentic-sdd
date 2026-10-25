---
description: "Fallback spec shape when the project Spec Kit template is unavailable. Prefer .specify/templates/spec-template.md."
---

# Small Spec Template

Prefer the project's `.specify/templates/spec-template.md` (Given/When/Then).
Use this only when that template is missing. `criterion_gate.py` extracts
English Given/When/Then scenarios, so numbered-only criteria will not score.

```markdown
# [Feature Name]

## Goal
One or two sentences describing the user-facing outcome.

## User Stories
- As a [role], I want [capability] so that [benefit].

## Acceptance Scenarios
1. **Given** [state], **When** [action], **Then** [observable result]
2. **Given** [state], **When** [action], **Then** [observable result]
(Maximum 5. Prefer fewer, precise criteria.)

## Out of Scope
- Explicitly list what this spec will not cover.
- Link to sibling specs if the work was split.

## Notes
- Dependencies or assumptions
- Links to related specs
```

## Quality Checks Before Approving a Spec
- Each acceptance criterion can be turned into a concrete test or observable check.
- Out-of-scope is explicit.
- The spec does not contain implementation details unless they are hard constraints.
- Length stays within 1–3 pages / ≤7 criteria. If larger, split.

## Splitting Guidance
When a feature is large:
1. Identify independent user journeys or bounded capabilities.
2. Create a new numbered spec directory for each.
3. Cross-link them in the Notes section.
4. Implement one small spec at a time.
