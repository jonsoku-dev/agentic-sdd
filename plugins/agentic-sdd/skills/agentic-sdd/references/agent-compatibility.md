---
description: Compatibility matrix for Spec Kit Agentic SDD across Claude Code, Codex, Cursor, and Grok Build.
---

# Agent Compatibility

This skill is **Spec Kit–first** and **agent-agnostic on artifacts**. One
`.specify/` tree and one canonical spec root are the source of truth. Hosts are
invocation surfaces only.

## Matrix

| Capability | Claude Code | Codex | Cursor | Grok Build |
|------------|-------------|-------|--------|------------|
| Skill install path | `~/.claude/skills/agentic-sdd` | `~/.codex/skills/agentic-sdd` | `~/.cursor/skills/agentic-sdd` | `~/.grok/skills/agentic-sdd` |
| Shared canon | → `~/.agents/skills/agentic-sdd` | same | same | same |
| Spec Kit `specify` key | `claude` | `codex` | `cursor-agent` | — (file-based) |
| Multi-agent setup helper | yes | yes | yes | consume shared artifacts; activate N/A |
| Phase slash / `$` commands | `/speckit.*` | `$speckit-*` | `/speckit.*` / skills | emulate via files + this skill |
| Subagent model pin | Agent/Task when available | Codex child agents | Cursor Task | Grok subagent / `grok -m` |
| Compaction | `/compact` | host context mgmt + `progress.md` | host context mgmt + `progress.md` | `progress.md` flush + short resume |
| REA closeout | MCP/CLI; `rea setup --yes --client claude_code` | `--client codex` | `--client cursor` | `--client grok_build`; CLI `capture-browser-scenario` if MCP down |
| pstack execution style | `pstack@pstack-claude`: `/pstack:*`, `pstack:poteto-agent[-<level>]` | `pstack@pstack-claude`: skills by name, `spawn_agent` + `reasoning_effort` | Official marketplace `pstack`: `/architect`, `poteto-agent` | `pstack@pstack-claude` (or Claude compat scan): skills by name, `spawn_subagent` |
| Completion goal | `/goal` (transcript-judged Stop-hook evaluator; headless via `claude -p "/goal …"`) | none native → `AGENTS.md` continuity + `progress.md` | `/goal` (`CreateGoal`/`UpdateGoal`, no budget) + `sdd-continue` stop hook | `/goal [--budget <tokens>]` with independent evidence review |

## Requirements for “works”

On every host the agent must be able to:

1. **Read/write** the project workspace (feature specs, plans, tasks, `.specify/`).
2. **Discover** this skill's `SKILL.md` and `references/`.
3. **Run** Python 3.10+ helpers under `scripts/` (stdlib only).
4. **Honor** phase ownership — do not edit code in `converge`, do not tick
   reviewer checklists in `implement`, etc.
5. **Refuse** to create a second per-agent spec tree.

Optional but preferred for delivery mid-flight:

- Spec Kit CLI `specify` ≥ 1.0.1
- `setup-speckit-multi-agent` for setup/inspect/activate/sdd

**Required at closeout:** REA (`user-rea` MCP and/or `rea` CLI from `rea-agents`).
If missing in delivery/repair closeout, install pinned package and
`rea setup --yes --client <active-id>` — see [rea-closeout.md](rea-closeout.md).
`--client claude` / `grok` are invalid; use `claude_code` / `grok_build`.

Missing mid-flight optional tools: continue on shared files with explicit recorded
limits. Do not fake Spec Kit command success. Do not fake REA success.

## Grok-specific notes

- There is no Spec Kit integration key for Grok today. Treat Grok as a first-class
  **consumer** of the same Spec Kit project other hosts set up.
- Point Grok Build project instructions at this skill and the project's
  constitution / `AGENTS.md` / `CLAUDE.md` equivalents.
- Use `grok models` only as a read-only catalog source for routing.
- If slash commands are absent, execute the same phase contracts against files
  and name the phase explicitly in `progress.md`.

## Codex agents metadata

`agents/openai.yaml` enables Codex `$agentic-sdd` invocation. Keep
`allow_implicit_invocation: true` so Spec Kit delivery can attach without a
manual skill quiz when relevant.

## Universal practices

- Prefer updating `spec.md` / `plan.md` / `tasks.md` / `progress.md` / checks
  over chat memory.
- Mid-project host switch: flush handoff → capture dirty owners → activate
  (when supported) → verify snapshot → continue.
- Do not assume vendor slash commands exist; fall back to plain-language phase
  steps that still write Spec Kit artifacts.
- Never lower acceptance to match a defective implementation.
- Delivery/repair via this skill is unattended inside the Final Goal: no phase
  quiz; reversible forks get a recorded default. See [pstack-integration.md](pstack-integration.md).
- pstack never owns Spec Kit artifacts. Cursor uses official `pstack`; Claude/Codex
  use a `/pstack:*` port when installed, else obligations — never claim a skill ran
  that the host cannot invoke.
