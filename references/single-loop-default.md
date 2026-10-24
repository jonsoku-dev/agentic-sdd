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
| `conflict` | One loop picks tools badly or its instructions collide, including the anchoring a reviewer must not share with the author | `O-interrogate` panel; the independent review gate; recovery reviewers |

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

## Harness limits stay in the harness

The single loop is open-ended inside fixed limits that agentic-sdd already has:

| Limit | Where |
|-------|-------|
| Turn budget | two unchanged attempts → [verification_guard.py](../scripts/verification_guard.py) and [recovery](recovery.md) |
| Cost budget | [cost modes](cost-modes.md); escalation budget in [model-routing](model-routing.md) |
| Write gates | one writer per checkout; hard boundaries in `SKILL.md`; admitted paths in the feature contract |
| Scope | Final Goal, `tasks.md` IDs, one converge per spec |

## Progressive disclosure

- `SKILL.md` stays the short always-loaded prompt; detail lives in
  `references/` and loads from [INDEX.md](INDEX.md) when a step needs it.
- pstack skills load per obligation row, not all at once.
- Knowledge (specs, logs, prior evidence) is read on demand by path, never
  pasted into a prompt or a leaf's brief. Leaves get file pointers.

## Waiting on a subagent

A reviewer or leaf whose result gates the parent's next step is on the critical
path. Launch the batch in one message in the foreground; the calls run in
parallel and return together. Background only while the parent has other
admitted work, and the harness notifies on completion. Never `ScheduleWakeup`,
sleep, or poll for your own agents: in the 2026-10-24 A/B one run parked two
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
