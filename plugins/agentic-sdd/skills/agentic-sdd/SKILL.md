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

**Completion gate (every model, every cost mode).** Do not write "Final Goal
met" or close a feature until `progress.md` holds, at column 1, for each
feature:

```text
pstack: O-interrogate|<host>|<reviewer subagent_type> → <n> findings
rea: <feature>|pass|<ev_… id>
```

The review line names a reviewer you actually spawned at `converge` (a separate
subagent, not your own reading of the diff); when no reviewer can run, write
`pstack: O-interrogate|<host>|BLOCKED: independent review` and leave the Final
Goal open. A missing line means the feature is not done. Before writing
"Final Goal met", run `python3 <this skill>/scripts/progress_gate.py progress.md`
and fix what it prints until it prints `ok`.

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

1. Resolve project (nearest `.specify/`), active feature, phase, revision/dirty owners.
2. Prefer read-only `setup-speckit-multi-agent` `inspect` / `sdd` when available.
3. Use installed Spec Kit phase commands — do not re-implement phases in chat.
4. Update feature artifacts and a root `progress.md` at every meaningful stage.
5. Compact only after flushing durable state (see [compaction](references/compaction-timing.md)).
6. Load the [phase card](references/phase-card.md) once per feature (or on host change); open the longer references only for the cases its last table lists. Run `python scripts/harness_probe.py --host <host> --project .` and record its two breadcrumbs in `progress.md`; apply the phase→obligation map for every phase entered. Every breadcrumb is one line starting at column 1 with `pstack:`, `harness:`, `ROUTING:`, or `rea:` (for example `pstack: O-poteto|claude|inline → T001–T004 verified`); a bulleted `- pstack:` line is not counted.
7. While a host goal (`/goal` on Claude, Cursor, Grok) is active, echo each check command and its decisive output line into the conversation after every verification; the evaluator reads the transcript, not files.

## Establish the working contract

1. Identify mode: delivery, repair, assessment, or read-only review.
   An investigation or plan is not permission to implement. Use installed project
   commands; do not initialize, upgrade, or install extensions just to run a phase.
2. Resolve the project and active feature from Spec Kit metadata, nearest
   instructions, and constitution. Record revision (if Git), dirty/untracked
   ownership, feature directory, canonical spec root (`specs/` or
   `.specify/specs/`), and phase. One writer per checkout.
3. Pin the Final Goal and verification contract in existing feature artifacts:
   acceptance conditions, admitted paths, required checks, non-goals.
   Use repository mandatory checks plus the narrowest additional proof.
   Do not add a generic verification framework by default.

Read [Spec Kit alignment](references/spec-kit-alignment.md) for project/feature
resolution, installed overrides, command syntax, or non-SDD entry points.

## Default workflow (Spec Kit)

```text
specify → plan → tasks → implement → converge → REA closeout
```

Add `clarify`, checklist, and `analyze` when ambiguity/risk warrants it or the
repository requires them. Preserve already admitted gates. Never silently
self-approve reviewer-owned checklists.

**REA closeout is mandatory** after a clean converge (and before Final Goal
finish). If REA CLI/MCP is missing, install and wire it, then analyze. The
[phase card](references/phase-card.md) has the common path;
[REA closeout](references/rea-closeout.md) covers install failures and web capture.

Read [phase contracts](references/phase-contract.md) when entering a phase or
handing off. The [phase card](references/phase-card.md) says *how* to execute
inside each phase; [pstack integration](references/pstack-integration.md) holds
the per-host dispatch detail.

### Unattended continuity

- Do not ask which Spec Kit phase to run next. After a phase succeeds, enter the
  next unfinished admitted phase in the same turn.
- Do not end a turn only to report progress. After a commit, test, or artifact
  write, start the next unfinished admitted task in the same turn. A host notice
  about one finished subagent or shell resumes the parent Final Goal after that
  notice's follow-up. Flush `progress.md` instead of a long chat report.
- Preference or approach forks solvable by repository evidence, a prototype, or
  constitution defaults: decide, record the default in `progress.md`, continue.
  Do not offer shorthand tokens for the human to type back.
- When the feature is complete and the Final Goal still has admitted work,
  specify the next numbered feature and continue without a human phase quiz.
- **Keep specs small, but split only past the threshold.** Plan the whole
  Final Goal as one numbered spec, even when it names several commands or
  behaviours. Decide at `tasks`, not before: split when
  `tasks.md` exceeds about 12 tasks or the work would span more than two
  compactions (`O-sequence`). A happy path and its error cases are one spec.
  Each extra spec costs a full converge, review, and REA round. A `closed-carryover`
  feature's gaps become the next spec's scope; the Final Goal stays open until
  the last spec reaches REA `pass`.

### Advance, recover, finish

- Carry out admitted tasks, then run the agreed checks. Clear in-scope failure →
  fix and rerun the affected check. Missing obtainable receipt → obtain evidence.
- For approved CLI checks, use [verification execution](references/verification-execution.md)
  before another run.
- After two unchanged attempts of the same check without new acceptance evidence,
  a concrete defect, or a narrowed diagnosis, use
  [verification_guard.py](scripts/verification_guard.py) and a recovery progress
  checkpoint. A real repair still gets its first verification.
- On repeated failure, conflicting diagnoses, or verification-driven scope drift,
  use [collaborative recovery](references/recovery.md). Retry thresholds change
  the approach, not the Final Goal. Prefer pstack `O-fio` / `O-correct` /
  attack-the-premise style changes of method when available
  ([pstack integration](references/pstack-integration.md)).
- **One converge per spec.** `converge` runs once per numbered feature. If it
  appends gap tasks, do one `implement` round for exactly those tasks, rerun
  only the affected checks, then go to REA closeout. Never run `converge` a
  second time on the same spec. If the affected checks still fail after that
  round, mark the feature `closed-carryover`, write the remaining gaps
  (acceptance ID → defect → evidence) as the scope of the next, smaller numbered
  spec, and `specify` it. Context stays small; the gap is not lost.
- `converge` only assesses and appends missing in-scope tasks. Return to
  `implement` for fixes. Do not relax acceptance to get green. Prefer
  `/interrogate` (or `O-interrogate` fallback) plus
  [multi-perspective review](references/multi-perspective-review.md). With
  pstack present, a required review with no independent reviewer stays
  `BLOCKED: independent review`; self-review never closes it.
- Installed `speckit-converge` reporting `converged` is not finish. After a clean
  converge (no new tasks), run **REA closeout** before marking the feature closed
  or advancing. Prefer MCP `user-rea` / `rea` tools; if absent in delivery/repair
  closeout, install pinned `rea-agents` and `rea setup --yes --client <active-id>` for the
  **active** host only (`cursor`, `claude_code`, `codex`, or `grok_build`), then analyze.
  Record verbatim Evidence IDs in `progress.md` / `converge.md` (or bug `test.md`).
  Material findings: features → one bounded fix round (append tasks → `implement`
  once → rerun affected checks) → REA again, no second `converge`; a further
  material finding on the same spec carries over to the next small spec.
  Bugs → return to `fix` → `test` → REA again (do not append feature tasks unless
  the defect is new scope). Prior Evidence IDs are stale after the edit.
  Details: [REA closeout](references/rea-closeout.md).
- Before the next feature, review every acceptance condition with
  [direction keeping](references/direction-keeper.md).
- Finish only when Spec Kit evidence is current and REA disposition is `pass`
  or `not-applicable`. `blocked-limitation`, `tasks-appended`, or a missing
  record leave the Final Goal / feature open.

### Repair (bugs)

Use the installed Spec Kit bug extension when present:
`assess → fix → test` under `.specify/bugs/<slug>/`.
See [bug workflow](references/bug-workflow.md). Assessment and test are evidence;
only fix edits source. On Cursor, prefer `/tdd` when a cheap local test exists
(`O-tdd`).

## Execution style (pstack)

Spec Kit remains the process. pstack (when present) is the execution engine
inside admitted phases — not a second SDD.

| Priority | Action |
|----------|--------|
| 1 | Run the owning Spec Kit phase command / artifact contract |
| 2 | Apply the matching obligation from the [phase card](references/phase-card.md) |
| 3 | On **Cursor**: official `pstack` skills (`/architect`, `/arena`, `/swarm`, `/interrogate`, poteto non-negotiables, `poteto-agent`) |
| 4 | On **Claude Code** with `pstack@pstack-claude`: same map via `/pstack:<skill>`; leaves (on a trigger) via `pstack:poteto-agent[-<level>]` |
| 5 | On **Codex** with `pstack@pstack-claude`: skills load by name; leaves (on a trigger) via the session spawn tool + `reasoning_effort` (port's `codex-tools.md`) |
| 6 | If pstack is absent: native Agent/Task + obligations; record `pstack: unavailable|<host>` once — do not stop Spec Kit |

Never start a free-standing `/poteto-mode` or `/pstack:poteto-mode` playbook that
reorders or replaces Spec Kit phases. Apply poteto non-negotiables *inside*
`implement` / `fix` batches only. The pstack SessionStart hook mandate on
Claude / Codex is satisfied by that `O-poteto` row, not by a second playbook.
Required rows in the phase map (`O-how`, `O-architect`, `O-hygiene`,
`O-interrogate`, `O-pause`, …) run as skill or obligation every time the phase
is entered; only common-core skills may be required on all hosts.

Long unattended or multi-phase runs: keep a decision trail
(`/show-me-your-work` or `/pstack:show-me-your-work`, or a feature-local TSV)
linked from `progress.md`.

## Route capabilities, not authority

Use [model routing](references/model-routing.md) for phase/role changes and
recovery turns. Keep the user's parent model. Child model and effort come, in
order, from the pstack sheet role line (`pstack-models.md` / `.mdc` after
`/setup-pstack`), the pstack skill defaults, then the parent model. The primary
decides from the written rules; no external advisor is consulted. A routing
decision is not proof a child actually ran. Dispatch the level as
`pstack:poteto-agent-<level>` on Claude and `reasoning_effort` on Codex.

Run each phase in one loop by default: the primary plans, edits, checks, and
revises in its own context. Spawn a subagent only for `bloat` (the work would
crowd the parent's context), `parallel` (independent, disposable fresh-context
work), or `conflict` (tool or instruction collision, including independent
review), and name the trigger in the breadcrumb. Never split by role
(write/test/review) or hand the conversation over. When a trigger holds, prefer
the host poteto agent (`poteto-agent` on Cursor; port equivalent on Claude);
the parent verifies its returned claims against the real artifacts. Leaves do
not delegate. When the parent needs a reviewer's or leaf's result before its
next step, launch them together in one message in the foreground (on Claude
pass `run_in_background: false`); never park the critical path behind
`ScheduleWakeup`, a sleep, or a poll, including a "fallback heartbeat" wakeup:
in a headless run it keeps the session alive until it fires. To wait for an
agent already in the background, end the turn; its completion notice resumes
you. Never spawn a placeholder agent to block. If unavailable, do explicit self-review and record the limit —
never claim independent consensus. See [single loop](references/single-loop-default.md).

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

## Kanban (optional)

```sh
python /path/to/agentic-sdd/visualizer/server.py --project /path/to/repo
```

See [kanban board](references/kanban-board.md).

## Hard boundaries

Require explicit confirmation before:

- Destructive operations (delete data, drop tables, force push, etc.)
- Handling secrets or credentials
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

Load only when needed — see [references/INDEX.md](references/INDEX.md).

Core: `spec-kit-alignment`, `phase-contract`, `pstack-integration`,
`host-guide-greenfield-brownfield`, `verification-execution`, `recovery`,
`direction-keeper`, `model-routing`, `starting-tool-considerations`,
`agent-compatibility`, `rea-closeout`, `single-loop-default` (when to spawn), `poteto-mode-anatomy` (how each host
reaches poteto-mode), `cursor-continuation` (Cursor only).
