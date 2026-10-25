---
description: Cursor stop-hook resume for an open agentic-sdd Final Goal.
---

# Cursor continuation

Cursor ends a turn when the assistant reply has no further tool call. Prompt rules cannot reopen that turn. A user-level stop hook submits the next user message while the Final Goal is still running.

This file is for Cursor only. Claude Code, Codex, and Grok keep their own loops.

## Machine line

Update this single line in the workspace root `progress.md` before any user-visible status:

```html
<!-- sdd-continue: {"status":"running","stop_reason":null,"next_action":"implement T012"} -->
```

| Field | Values |
|-------|--------|
| `status` | `running`, `delivered`, `blocked` |
| `stop_reason` | `null`, `destructive`, `secret`, `missing_goal`, `contradiction`, `evidence` |
| `next_action` | One concrete Spec Kit step |

Keep the JSON valid and inside one comment. `next_action` is a JSON string.

- While work remains, `status` is `running` and `stop_reason` is `null`.
- When the Final Goal is delivered, set `status` to `delivered` and stop.
- For a destructive action, a secret, a missing or contradictory goal, or an evidence or authority boundary, set `status` to `blocked`, set `stop_reason` to the matching value, and ask once.

`delivered` or `blocked` makes the hook stay silent. A hard `stop_reason` on a `running` line does too.

## What the hook does

Scripts live in `~/.cursor/hooks/agentic-sdd-continue/`. The stop script is last in `~/.cursor/hooks.json` and uses `loop_limit: null`. The script itself allows 80 automatic follow-ups per arm.

- A prompt containing `agentic-sdd` arms the session and clears hold, the follow-up count, and a stuck latch.
- A short resume phrase (`계속`, `이어서 진행`, `continue`, `keep going`, and the close variants in the script) does the same only when the session is already armed.
- Any other human prompt sets hold. The hook does not continue after that answer.
- A follow-up contains the marker `sdd-continue-followup`. That marker clears hold and does not reset the budget. It is the same Final Goal, not a new task.
- Ask mode and background agents are never resumed. Aborted and error stops are never resumed.
- A missing machine line still continues once. The follow-up tells the agent to write the line, then do the next action.
- The same `next_action` and the same `progress.md` modification time on two consecutive stops latches stuck. Only a later human arm clears it.
- Follow-up 80 tells the agent to say the continuation budget is spent if the goal is still open. Follow-up 81 is not sent. A later human `/agentic-sdd` or resume phrase resets the count.

The hook does not approve shell or MCP calls. Those cards still wait for the human.

Cursor has no Skill tool. If `/speckit.*` is not invocable, execute the phase contract against the feature files. Do not hand the critical path to a background subagent and end the turn. The hook is the backup when a turn ends anyway.

## Follow-up shape

The injected message starts with `<!-- sdd-continue-followup -->` and tells the agent to read `progress.md`, do `next_action`, and avoid spending the turn on a status report.
