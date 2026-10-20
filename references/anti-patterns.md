---
description: Anti-patterns for Spec Kit Agentic SDD.
---

# Anti-Patterns

## Scope & specification

- **Silent expansion**: Adding features or edge cases outside the current feature
  without a new numbered feature or explicit authorization.
- **Inventing requirements**: Filling missing acceptance criteria instead of
  recording an assumption or entering `clarify`.
- **One giant feature**: Combining independent journeys into one feature directory.
- **Second spec store**: Copying specs into agent-specific folders (Claude-only,
  Codex-only, etc.) instead of shared Spec Kit roots.
- **Chat-only phases**: Planning or tasking only in conversation without writing
  `plan.md` / `tasks.md`.

## Verification

- **Over-verification loop**: Full acceptance suite after every tiny edit mid-implement.
- **Test masking**: Skipping or weakening tests to get green.
- **Done without evidence**: Declaring complete when required checks were not run
  on the relevant code state.
- **Converge edits code**: Using converge to patch source instead of appending tasks.
## Handoff & hosts

- **Chat memory reliance**: Decisions never written to feature artifacts / `progress.md`.
- **Stale progress.md**: Stage finished without Overall + next action.
- **Ignoring host bootstrap**: Assuming `/speckit.*` exists on Grok, or inventing
  Grok-only directories.
- **Multi-writer checkout**: Two hosts editing the same feature without handoff.

## Process

- **Skipping Spec Kit by default**: Using light-path for non-trivial work.
- **Self-approving reviewer checklists**: Implementation ticking reviewer-owned markers.
- **Destructive action without confirmation**: Force push, drop tables, secret handling.
- **Blind retry**: Same failing check twice with no new diagnosis or inputs.
- **Setup from delivery skill**: Initializing Spec Kit from this skill instead of
  `setup-speckit-multi-agent`.
- **Skipping or faking REA:** Feature/Final Goal/bug `verified` without a real
  evidence id; URL-only capture counted as pass; `blocked-limitation` used to
  finish; placeholder `ev_…`; refusing to install `rea-agents` when closeout is
  in scope; using `--client claude`/`grok` or `--all-detected`/`curl|bash` against
  the closeout install rules.

## Recovery

When an anti-pattern is detected:

1. Stop the current mutating step if ownership/authority is unclear.
2. Record the anti-pattern under Open issues in `progress.md`.
3. Reverse unsafe changes when safe, or open a bug/feature for correction.
4. Set one concrete next Spec Kit phase action before continuing.
