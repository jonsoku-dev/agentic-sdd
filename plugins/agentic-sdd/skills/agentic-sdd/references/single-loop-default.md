---
description: >
  Single agent loop as the default inside every Spec Kit phase; spawn a
  subagent only for context bloat, parallel disposable work, or tool/prompt
  conflict. How to fold leaves back and how to measure the change.
---

# Single loop by default

The primary runs each admitted phase in one loop: one model, one context, an
open-ended tool loop where the model writes the plan, sees results, and revises
mid-turn. The harness sets the limits; the model decides the next step.
Subagents are a tool for three named problems, not the shape of the run.

Source: Diane Sarkis, "Building agents: When to fold subagents into your main
agent loop", Anthropic Applied AI, 2026-10-22
(<https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop>),
migration kit <https://github.com/anthropics/single-agent-loop-kit>. The
article reports about 2× faster runs than a multi-agent harness for one
customer and a Claude Code system prompt cut by more than 80% through skills
and tool progressive disclosure. Those are the source's measurements, not
numbers measured on agentic-sdd.

## When a subagent is allowed

Spawn only when at least one trigger holds, and name it in the breadcrumb:

| Trigger | Means | agentic-sdd examples |
|---------|-------|----------------------|
| `bloat` | Keeping the work in the parent would push the parent's context past what it can use well: large reads, logs, or a packet the parent would have to page through | `O-guard` bulk reads; a cross-cutting `O-fio` survey |
| `parallel` | Independent work that runs at the same time in a fresh context and is thrown away after it returns | `O-swarm` disjoint packets; `O-architect` / `O-arena` design runners |
| `conflict` | One loop picks tools badly or its instructions collide, including the anchoring a reviewer must not share with the author | one `O-interrogate` verifier; the independent review gate |

Everything else runs inline in the parent: a packet that fits the parent's
context, a mechanical edit, a sequential task chain over the same files.

Split by context, never by role or org chart. Write → test → review as three
agents loses context at every handoff; one loop that writes, runs the check,
and fixes keeps it. An independent reviewer is the exception because its value
is the fresh context (`conflict`), and it returns findings, not a takeover.

## Call as tools, never full handoff

A spawned agent is a tool call. The parent keeps the conversation, the Final
Goal, `progress.md`, and `tasks.md`. Hand the conversation over only when a
human must talk to that agent directly, which agentic-sdd never needs.

Every packet returns the same schema, which the parent checks against real
artifacts before acting:

```text
changed paths | commands run → decisive output line | acceptance IDs → met/unmet/blocked | open risks | observed model@effort or unknown
```

The parent opens the changed files and reruns or reads the decisive check. A
summary is a claim; the artifact is the evidence (see
[harness-layers.md](harness-layers.md) L5).

## Folding leaves back

When a run keeps spawning the same kinds of leaf, fold them, one at a time:

1. **Merge.** Leaves that chain into each other or touch the same data become
   one packet, or go inline.
2. **Call as tools.** A leaf that took over a whole phase becomes a bounded
   call with the return schema above.
3. **Fold into skills and tools.** A leaf's standing prompt becomes a skill
   loaded on demand; its API calls become tools. The parent loads the skill
   only in the phase that needs it.

After each fold, compare the same cases before and after (`evals/evals.json`,
a feature's acceptance checks, or a `docs/evals/` run). Look at the cases that
flipped, not only the total, and run more than once. Keep the fold when the
score holds; otherwise restore the leaf or fix the skill. Change one thing per
comparison.

## Harness limits that actually run

The single loop is open-ended inside the limits this repository enforces. Anything not in this table is guidance for the model, not a gate.

| Limit | Where it runs |
|-------|----------------|
| Completion | [progress_gate.py](../scripts/progress_gate.py) is the only completion predicate. Claude Stop (`hosts/claude/hooks/stop_gate.py`) and Cursor stop (`hosts/cursor/hooks/agentic-sdd-continue/common.py`) both call it. While `progress.md` claims the Final Goal is met, or Cursor `status` is `delivered`, an open gate refuses the stop. |
| Task count, one converge, leftover worktrees | The same script. More than 12 tasks or a second `Convergence` header in `tasks.md` is a refusal. A leftover is only a `gate: worktree|<absolute-path>` this run recorded that is still checked out, and is neither the main checkout nor the current checkout. |
| Write gates | Claude guarded `hosts/claude/hooks/git_guard.py` denies `git push`, `git merge` (not `--abort`), `reset --hard`, `clean -f`, `branch -D`, `stash`, a checkout/restore that discards the tree, and the deploy/publish commands in `why_deploy` (`npm publish`, `vercel --prod`, `fly deploy`, `kubectl apply`, `terraform apply`, `gh release create`, and the same family). Codex, Grok, Cursor, and the hook-free edition have no write hook. |
| Stuck completion | Both hosts share `STUCK_LIMIT` (2) in `progress_gate.py`. A refusal is identical when the `progress.md` text, the problem list, and the git state are unchanged. The git state is `HEAD` plus `git worktree list --porcelain`, or `nogit` when git fails. The first identical refusal stays a block (Claude `decision: block`) or a follow-up (Cursor). The second allows the stop. The message starts with `NOT complete / blocked:` and includes `The Final Goal is not met.` The words `Final Goal met` are absent from that message. The hook rewrites those claims in `progress.md` to `Final Goal is not met` and appends the same message. A later stop with that same file is allowed. A change to `progress.md` or the git state resets the count, and the next refusal blocks or follows up again. `stop_hook_active` does not release the block. This ending is not completion. |
| Turn budget | Cursor continuation only, for a goal that is still running: 80 follow-ups (`BUDGET`) and a separate stuck latch after the same `next_action` and the same `progress.md` modification time twice. Spending the budget does not close the gate and does not write `Final Goal met`. Claude, Codex, and Grok have no turn cap. The stuck-completion row is the only shared escape from a repeated open gate. |
| Repeated identical checks | [verification_guard.py](../scripts/verification_guard.py) recommends stopping after two unchanged attempts, and only when the model passes it a state file. It does not end the session. |
| Cost | No cost gate. [cost-modes.md](cost-modes.md) and the escalation notes in [model-routing.md](model-routing.md) are guidance. |

## Progressive disclosure

- `SKILL.md` stays the short always-loaded prompt; detail lives in
  `references/` and loads from [INDEX.md](INDEX.md) when a step needs it.
- An output style applies to the parent conversation and its forks. It does not apply to an ordinary subagent. Paste the [spawn brief](phase-card.md#spawn-brief).
- pstack skills load per obligation row, not all at once.
- Knowledge (specs, logs, prior evidence) is read on demand by path, never
  pasted into a prompt or a leaf's brief. Leaves get file pointers.

## Waiting on a subagent

A verifier or leaf whose result gates the parent's next step is on the critical
path. Launch the batch in one message in the foreground; the calls run in
parallel and return together. Background only while the parent has other
admitted work, and the harness notifies on completion. To wait for an agent
already in the background, end the turn; the completion notice resumes you.
Never `ScheduleWakeup`, sleep, poll, or spawn a placeholder ("reply ok") agent
to block on your own agents: in the 2026-10-24 A/B one run parked two
background reviewers behind a 1200 s wakeup and idled about 19 minutes
(`docs/evals/2026-10-24-single-loop-ab/result.md`).

## Breadcrumbs

Use the existing `pstack:` line form so `scripts/harness_probe.py` L7 counts it:

```text
pstack: O-poteto|claude|inline → T010–T012 verified
pstack: O-swarm|claude|pstack:poteto-agent-medium (parallel) → T013, T014 verified (worktrees wt-013, wt-014)
pstack: O-interrogate|codex|interrogate (conflict) → 2 gaps appended
```

`inline` means the parent did the packet itself. A spawn without a named
trigger is an anti-pattern ([anti-patterns.md](anti-patterns.md)).
