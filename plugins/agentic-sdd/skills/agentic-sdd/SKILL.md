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

Finish the user's original **Final Goal** with **Spec Kit as the default**.
Light scaffolding is opt-in for trivial work only — never the default.

The primary owns scope, integration, and completion. Reviewer agreement and
model scores never replace required evidence or authorization.

**Completion gate (every model, every cost mode).** `scripts/progress_gate.py`
is the only completion predicate. Do not write "Final Goal met" until it prints
`ok`. It requires, at column 1:

```text
pstack: O-interrogate|<host>|<reviewer subagent_type> → <n> findings
rea: <feature>|pass|ev_…
```

A feature with no runnable or build artifact closes with
`rea: <feature>|not-applicable|<why there is no runnable artifact>` instead of
`pass`. `blocked-limitation` and `tasks-appended` do not close. A directory
under `specs/` or `.specify/specs/` that predates this Final Goal is omitted
only by `gate: exclude|<feature-directory>|<why it predates this Final Goal>`.
`overview` and `000-overview` are scaffolds, not features. Every other feature
directory needs its own closing line.

The review line names a reviewer you actually spawned at `converge` (a separate
subagent, not your own reading of the diff); when no reviewer can run, write
`pstack: O-interrogate|<host>|BLOCKED: independent review` and leave the Final
Goal open. Invoking this skill is the user's explicit request for that reviewer subagent,
so a host default such as "spawn agents only when the user asks" is already
satisfied. Only an instruction in the user's own words not to use subagents
blocks it: then follow it, write the BLOCKED line, and report the Final Goal as
not met, naming the missing review. A self-review never fills the review line. A missing line means the feature is not done. Run
`python3 <this skill>/scripts/progress_gate.py progress.md` and fix what it prints until it prints `ok`.

**Invocation of this skill for delivery/repair is a full-autonomy grant** inside
the admitted Final Goal: advance every Spec Kit phase and remaining numbered
features without a human phase quiz. See [pstack integration](references/pstack-integration.md)
for autonomy rules and phase→execution mapping.

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

1. Resolve project (nearest `.specify/`), active feature, phase, revision/dirty owners. One writer per checkout. An investigation or plan is not permission to implement.
2. Prefer read-only `setup-speckit-multi-agent` `inspect` / `sdd` when available. Use installed Spec Kit phase commands; do not re-implement phases in chat or install an extension just to run one.
3. Update feature artifacts and a root `progress.md` at every meaningful stage. Compact only after flushing durable state ([compaction](references/compaction-timing.md)).
4. Load the [phase card](references/phase-card.md) once per feature (or on host change). It is the procedure for `specify → plan → tasks → implement → converge → REA closeout`. Open a longer reference only when its last table names that case. Do not read [phase-contract.md](references/phase-contract.md) on every phase.
5. Run `python scripts/harness_probe.py --host <host> --project .` and record its two breadcrumbs. Every breadcrumb is one line at column 1 with `pstack:`, `harness:`, `ROUTING:`, or `rea:` (for example `pstack: O-poteto|claude|inline → T001–T004 verified`). A bulleted or backticked line is not counted.
6. While a host goal (`/goal` on Claude, Cursor, Grok) is active, echo each check command and its decisive output line into the conversation after every verification; the evaluator reads the transcript, not files.

## Rules that stay here

The phase card holds the phase rows. These rules stay in this file because a run that does not open another file still has to follow them.

- Do not ask which phase is next. After a phase, commit, test, or artifact write, start the next unfinished admitted work in the same turn. Flush `progress.md` instead of a long chat report. Decide an evidence-backed fork, record the default, and continue.
- Plan the Final Goal as one spec. `progress_gate.py` refuses a 13th task and a second `Convergence` header. A happy path and its error cases are one spec. A `closed-carryover` gap becomes the next spec; the Final Goal stays open until the last spec closes.
- Implement inline. Spawn only for `bloat`, `parallel`, or `conflict`, and name the trigger. Never split one packet into writer, tester, and reviewer, and never hand the conversation over. The parent keeps `tasks.md` and checks the returned claims against the files. See [single loop](references/single-loop-default.md).
- Converge once, with one independent verifier, in the foreground (`run_in_background: false` on Claude). Never park that result behind `ScheduleWakeup`, a sleep, a poll, or a fallback heartbeat. To wait for an agent already in the background, end the turn. Never spawn a placeholder agent. A second reviewer is allowed only when [Restoring a wider review panel](references/pstack-integration.md#restoring-a-wider-review-panel) recorded a C1–C9 flip. Converge does not edit source and does not relax acceptance. `speckit-converge` reporting `converged` is not finish.
- REA's common path is on the phase card. Install failures are [REA closeout](references/rea-closeout.md). Only `pass` and `not-applicable` close the feature.
- After two unchanged attempts of the same check without new evidence, use [verification_guard.py](scripts/verification_guard.py). A real repair still gets its first verification. Repeated failure or scope drift: [recovery](references/recovery.md).
- Bugs: `assess → fix → test` under `.specify/bugs/<slug>/` ([bug workflow](references/bug-workflow.md)). Assessment and test are evidence; only fix edits source.
- Do not start a free-standing `/poteto-mode` or `/pstack:poteto-mode` playbook. `O-poteto` inside `implement` satisfies the SessionStart mandate. If pstack is absent, record `pstack: unavailable|<host>` once and continue Spec Kit. Child model and effort: [model routing](references/model-routing.md). A `ROUTING:` line is not proof a child ran.

## Light path (opt-in only)

Use a reduced path **only** when all are true:

- Trivial, reversible change (typo, one-line config, docs-only)
- Single clear acceptance check
- User did not ask for Spec Kit / high confidence / careful work
- No auth, payment, personal data, public API, schema, or multi-module blast radius

Then: short goal + AC in `progress.md` (or a tiny `spec.md`), implement, verify
once. If a runnable or build artifact exists, REA must reach `pass` (same rule as
full Spec Kit). Use `not-applicable` only when no such artifact exists. Prefer
full Spec Kit whenever unsure.

## Hard boundaries

Require explicit confirmation before:

- Destructive operations (delete data, drop tables, force push, etc.)
- Handling secrets or credentials. Never write one into `progress.md`, specs,
  evidence, or reports: put `<REDACTED>`, keep the value in an environment
  variable, and quote only the lines that carry the signal (`progress_gate.py`
  fails on known token shapes)
- Changing scope beyond the agreed Final Goal
- Installing Spec Kit extensions/presets/integrations

**Authorized without extra confirmation (narrow):** in delivery/repair closeout
only, when MCP and `rea` are both missing or this host’s MCP registration is
missing/stale: `npm install -g rea-agents@6.7.0` (do not upgrade a working CLI)
and `rea setup --yes --client <active-id>` for that host only
(`cursor` | `claude_code` | `codex` | `grok_build`). No `curl | bash`, no
`--all-detected`, no install from read-only/plan/audit modes.

This skill grants no permission to push, merge, deploy, stash, reset, or
force-refresh. Use `setup-speckit-multi-agent` `commit-phase` only within
already authorized scope after its gates pass.

## References

Load a long reference only when the [phase card](references/phase-card.md) last table names that case. The load map is [references/INDEX.md](references/INDEX.md). The optional board is `python3 visualizer/server.py --project /path/to/repo`.
