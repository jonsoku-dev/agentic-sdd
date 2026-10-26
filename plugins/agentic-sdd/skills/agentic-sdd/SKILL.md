---
name: agentic-sdd
description: >
  Coordinate or resume GitHub Spec Kit delivery through the user's Final Goal,
  unattended end-to-end by default (no phase quiz), with phase contracts, scoped
  verification, collaborative recovery, pstack-sheet model/effort routing,
  pstack execution style when available (Cursor plugin; pstack-claude port on
  Claude Code, Codex, and Grok Build),
  and a mandatory REA reverse-engineering closeout (install REA if missing).
  Default is full Spec Kit (specify → plan → tasks → implement → converge → REA),
  not light-first. Use for numbered feature cycles and SDD phase handoffs on
  Claude Code, Codex, Cursor, and Grok Build. Preserve read-only scope for
  audits and planning. Repository setup belongs to setup-speckit-multi-agent.
---

# Agentic SDD

Finish the user's **Final Goal** with Spec Kit.
A light path is opt-in for trivial work only.

The parent keeps scope, integration, and completion.
A verifier's agreement does not replace evidence.

**Completion gate.** `scripts/progress_gate.py` is the only completion predicate.
Do not write "Final Goal met" until it prints `ok`.
These lines start at column 1:

```text
pstack: O-interrogate|<host>|<reviewer subagent_type> → <n> findings
rea: <feature>|pass|ev_…
```

- No runnable artifact: `rea: <feature>|not-applicable|<why there is no runnable artifact>`. `n/a` and other placeholders do not count.
- `tasks-appended` does not close. A later `pass` can.
- `blocked-limitation` stays open. A later `pass` does not clear it. Remove that line once the limitation is gone.
- `gate: exclude|<feature-directory>|<why>` drops an older directory. It does not drop the active feature, the last directory name in sorted order.
- `overview` and `000-overview` are not features.
- Every other feature directory needs its own closing line.

The review line names the verifier you spawned.
Your own reading of the diff does not count.
If no verifier can run, write `pstack: O-interrogate|<host>|BLOCKED: independent review` and leave the Final Goal open.
Invoking this skill is the user's request for that verifier.
If the user says not to use subagents, write the BLOCKED line and stop.
Run `python3 <this skill>/scripts/progress_gate.py progress.md` and fix every line it prints.

This file does not block a command.
The script, Claude Stop, the Cursor stop hook, and guarded `git_guard.py` do.
The same open-gate refusal twice, with no change to `progress.md` or the git state, ends the turn as `NOT complete / blocked`.
That ending says the Final Goal is not met.
It leaves the words "Final Goal met" out of the message and out of `progress.md`.
The one-verifier default is an instruction.
The gate checks that one real verifier line exists.
It does not count seats.

On delivery or repair, advance every admitted phase.
Do not quiz the user about the next phase.
See [pstack integration](references/pstack-integration.md).

## Host bootstrap (required)

Detect the host once, then follow that host's invocation surface. Do not invent
a second spec store. Setup/init belongs to `setup-speckit-multi-agent`.

| Host | Skill load | Spec Kit surface | Persist handoff |
|------|------------|------------------|-----------------|
| **Claude Code** | `~/.claude/skills/agentic-sdd` or project `.claude/skills/` | `/speckit.*` (or installed skill syntax) | `CLAUDE.md` + feature artifacts + `progress.md` |
| **Codex** | `~/.codex/skills/agentic-sdd` → shared `.agents/skills` | `$speckit-*` | `AGENTS.md` + feature artifacts |
| **Cursor** | `~/.cursor/skills/agentic-sdd` → shared `.agents/skills` | `/speckit.*` / Cursor skills | `.cursor/rules/` or `AGENTS.md` + feature artifacts. Resume via [cursor-continuation](references/cursor-continuation.md) |
| **Grok Build** | `~/.grok/skills/agentic-sdd` → shared `.agents/skills` | File-based `.specify/` + this skill (no native Spec Kit key yet) | Project instructions + feature artifacts |

For **greenfield vs brownfield** procedures on Claude / Codex / Cursor (human +
agent), load [host guide](references/host-guide-greenfield-brownfield.md) once
per feature when field type or host is unclear.

Read [starting-tool considerations](references/starting-tool-considerations.md)
and [agent compatibility](references/agent-compatibility.md) when the host or
invocation syntax is unclear.

Universal first actions on every host:

1. Resolve the nearest `.specify/`, the active feature, and its phase. One writer per checkout. An investigation is not permission to implement.
2. Prefer read-only `setup-speckit-multi-agent` `inspect` / `sdd`. Use the installed Spec Kit commands. Do not re-implement a phase in chat.
3. Update the feature artifacts and root `progress.md` at each meaningful stage. Compact only after that flush ([compaction](references/compaction-timing.md)).
4. Load the [phase card](references/phase-card.md) once per feature, or on a host change. Open a longer reference only when its last table names that case. Do not read [phase-contract.md](references/phase-contract.md) on every phase.
5. Run `python scripts/harness_probe.py --host <host> --project .` and record its two breadcrumbs. Each breadcrumb is one line at column 1, prefixed `pstack:`, `harness:`, `ROUTING:`, or `rea:`. A bullet or backtick does not count.
6. While a host goal is active, echo each check command and its decisive output line. The evaluator reads the transcript, not only the files.

## Rules that stay here

The phase card holds the phase rows.
These rules stay here because a run may not open another file.

- Do not ask which phase is next.
- After a phase, commit, test, or artifact write, start the next admitted work in the same turn.
- Flush `progress.md`. Do not send a long chat report.
- Plan the Final Goal as one spec. A happy path and its error cases stay together.
- `progress_gate.py` refuses a 13th task and a second `Convergence` header.
- A `closed-carryover` gap becomes the next spec. The Final Goal stays open until the last spec closes.
- Implement inline. Spawn only for `bloat`, `parallel`, or `conflict`, and name the trigger.
- Do not split one packet into writer, tester, and verifier. The parent keeps `tasks.md`.
- Converge once, with one independent verifier, in the foreground (`run_in_background: false` on Claude).
- Do not park that result behind `ScheduleWakeup`, sleep, a poll, or a fallback heartbeat.
- To wait for a subagent already in the background, end the turn.
- A second verifier needs a recorded C1–C9 flip. See [Restoring a wider review panel](references/pstack-integration.md#restoring-a-wider-review-panel).
- Converge does not edit source and does not relax acceptance. `speckit-converge` saying `converged` is not finish.
- REA's common path is on the phase card. Install failures are [REA closeout](references/rea-closeout.md). Only `pass` and `not-applicable` close a feature.
- After two unchanged attempts of the same check with no new evidence, use [verification_guard.py](scripts/verification_guard.py). A real repair still gets its first check.
- Bugs follow `assess → fix → test` ([bug workflow](references/bug-workflow.md)). Only `fix` edits source.
- Do not start a free-standing `/poteto-mode` playbook. If pstack is absent, record `pstack: unavailable|<host>` once and continue.
- A `ROUTING:` line is not proof a child ran. See [model routing](references/model-routing.md) and [single loop](references/single-loop-default.md).

## What reaches a subagent

An output style applies to the parent conversation and its forks.
It does not apply to an ordinary subagent.
This file is the same.
Paste the [spawn brief](references/phase-card.md#spawn-brief) into the leaf or verifier prompt.
A file path is not a substitute for that brief.

## Light path (opt-in only)

Use a reduced path **only** when all are true:

- Trivial, reversible change (typo, one-line config, docs-only)
- Single clear acceptance check
- User did not ask for Spec Kit / high confidence / careful work
- No auth, payment, personal data, public API, schema, or multi-module blast radius

Then write a short goal and acceptance check in `progress.md`, implement, and verify once.
If a runnable artifact exists, REA must reach `pass`.
Use `not-applicable` only when no such artifact exists.
Prefer full Spec Kit when unsure.

## Hard boundaries

Require explicit confirmation before:

- Destructive operations (delete data, drop tables, force push, etc.)
- Handling secrets or credentials.
  Write `<REDACTED>` in `progress.md`, specs, evidence, and reports.
  Keep the value in an environment variable.
  `progress_gate.py` fails on known token shapes.
- Changing scope beyond the agreed Final Goal
- Installing Spec Kit extensions/presets/integrations

**Allowed without a second confirmation,** and only on delivery or repair closeout, when MCP and `rea` are missing or stale:

- `npm install -g rea-agents@6.7.0` (do not upgrade a working CLI)
- `rea setup --yes --client <active-id>` for the active host only (`cursor`, `claude_code`, `codex`, or `grok_build`)

No `curl | bash`. No `--all-detected`. No install from a read-only, plan, or audit run.

This skill grants no permission to push, merge, deploy, stash, reset, or force-refresh.
Guarded Claude denies those commands in `git_guard.py`.
The other hosts have the instruction only.

## References

Load a long reference only when the [phase card](references/phase-card.md) names that case.
The load map is [references/INDEX.md](references/INDEX.md).
The optional board is `python3 visualizer/server.py --project /path/to/repo`.
