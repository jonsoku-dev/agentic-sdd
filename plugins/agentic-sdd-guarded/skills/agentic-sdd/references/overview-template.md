---
description: "Human-readable overview spec that maps all child specs so neither agent nor user loses context."
connections: [spec-template, progress-template]
---

# Overview Spec Template

Keep `specs/000-overview/spec.md` short (under 1 page). It is the map, not a detailed spec.

```markdown
# Project Overview

## Overall Goal
[1–2 sentences]

## Child Specs
- [001-auth](../001-auth/spec.md) — Login and session handling
- [002-dashboard](../002-dashboard/spec.md) — Main dashboard after login
- [003-notifications](../003-notifications/spec.md) — In-app notifications

## Current Status
See root `progress.md` Overall line.

## Notes
- Split from original large spec on YYYY-MM-DD
```

## Rules
- Update this file whenever a new child spec is created or a split happens.
- Every child spec must start with a parent link:
  ```markdown
  > Parent: [000-overview](../000-overview/spec.md) | Purpose: [one line]
  ```
- Do not put detailed acceptance criteria here.
