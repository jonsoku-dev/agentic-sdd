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
- When `scripts/progress_gate.py` prints `ok`, set `status` to `delivered` and stop. `delivered` while the gate is open is refused: the hook follow-up quotes the script's lines and the Final Goal stays unmet.
- For a destructive action, a secret, a missing or contradictory goal, or an evidence or authority boundary, set `status` to `blocked`, set `stop_reason` to the matching value, and ask once.

`blocked`, or `delivered` after `progress_gate.py` prints `ok`, makes the hook stay silent. A hard `stop_reason` on a `running` line does too. `delivered` with an open gate does not.

## What the hook does

Scripts live in `~/.cursor/hooks/agentic-sdd-continue/`. The stop script is last in `~/.cursor/hooks.json` and uses `loop_limit: null`. The script itself allows 80 automatic follow-ups per arm.

- A prompt containing `agentic-sdd` arms the session and clears hold, the follow-up count, the running stuck latch, and the completion-refusal latch.
- A short resume phrase (`계속`, `이어서 진행`, `continue`, `keep going`, and the close variants in the script) does the same only when the session is already armed.
- Any other human prompt sets hold. The hook does not continue after that answer.
- A follow-up contains the marker `sdd-continue-followup`. That marker clears hold and does not reset the budget. It is the same Final Goal, not a new task.
- Ask mode and background agents are never resumed. Aborted and error stops are never resumed.
- A missing machine line still continues once. The follow-up tells the agent to write the line, then do the next action.
- The same `next_action` and the same `progress.md` modification time on two consecutive stops latches stuck. Only a later human arm clears it.
- A `delivered` line, or progress text that claims the Final Goal is met, is checked with `scripts/progress_gate.py`. The first open-gate refusal is a follow-up that quotes the script. The second identical refusal, with no change to `progress.md` or the git state (`HEAD` and `git worktree list --porcelain`), allows the stop. That message starts with `NOT complete / blocked:` and says the Final Goal is not met. It is a `user_message`, so the agent is not resumed, and it does not contain `Final Goal met`. The hook rewrites the claim in `progress.md` the same way. A later stop with that same file is allowed. A change to `progress.md` or the git state starts the count again. The 80-follow-up budget still applies to a running goal; a spent budget does not close the gate.
- Follow-up 80 tells the agent the continuation budget is spent and that this does not mean the Final Goal is met. Follow-up 81 is not sent. A later human `/agentic-sdd` or resume phrase resets the count.

The hook does not approve shell or MCP calls. Those cards still wait for the human.

Cursor has no Skill tool. If `/speckit.*` is not invocable, execute the phase contract against the feature files. Do not hand the critical path to a background subagent and end the turn. The hook is the backup when a turn ends anyway.

## Follow-up shape

The injected message starts with `<!-- sdd-continue-followup -->` and tells the agent to read `progress.md`, do `next_action`, and avoid spending the turn on a status report.
