---
description: "Optimal timing for context compaction to reduce token cost without losing critical state."
---

# Compaction Timing Guide

## Core Rule

**Compact at logical task boundaries, not only when the context window is almost full.**

Waiting until 80–95% capacity means the model is already working with degraded context. The summary it produces will be based on a partially compressed view.

## Recommended Triggers

| Trigger | When | Why |
|---------|------|-----|
| **Spec Kit phase boundary** (preferred) | After specify/plan/tasks/implement/converge stage, or bug assess/fix/test | State is clean and easy to summarize accurately |
| **~150k–250k tokens** | Mid-session when context has grown but work is still coherent | Avoids quality drop before the hard limit |
| **Before high-risk step** | Before auth changes, schema migrations, or irreversible actions | Ensures the model has a clear, focused context |
| **Idle / session end** | After ~50–60 min idle (Claude Code idle compaction) | Prevents full re-processing when resuming |

## How to Compact Well

1. **Flush durable state first**  
   With pstack present, run the poteto `pause-safely` step first (`O-pause`; `resume.mjs publish` on the Claude/Codex port). Then:  
   Update `progress.md` (Overall status, current scope, completed, next action) and any relevant spec files before compacting.

2. **Give explicit instructions**  
   Do not use a bare `/compact`. Examples:
   - `/compact keep the current goal, acceptance criteria, progress.md summary, and next action`
   - `/compact focus on the auth fix; drop exploration notes`

3. **Prefer short progress.md over long history**  
   After compaction, the next turn should start from the updated `progress.md` rather than relying on the summary alone.

## What to Avoid

- Compacting mid-derivation or mid-search (partial results are lost and must be recomputed).
- Compacting only when the window is nearly full.
- Compacting without first writing key decisions and next actions to disk.
- Using compaction as a substitute for routing simple work to light models (Haiku 5.5 / Luna).

## Interaction with Cost Mode

- **Economy**: Compact earlier and more aggressively. Prefer task-boundary compaction.
- **Balanced**: Compact at logical milestones or around 200k tokens.
- **Thorough**: Compact less frequently, but still at clear stage boundaries. Preserve more intermediate reasoning if it is material.

## Practical Default for This Skill

After every Spec Kit phase stage (or bug stage):

1. Update feature artifacts, then `progress.md` (Overall + next phase action).
2. Compact with an instruction that preserves Final Goal, feature/phase, and next action.
   - Claude Code: `/compact ...`
   - Codex / Cursor / Grok: use host context management; always rely on `progress.md` as the resume surface.
3. Continue from compacted state + `progress.md` + current feature paths.
