---
description: Host-specific bootstrap for Spec Kit Agentic SDD on Claude Code, Codex, Cursor, and Grok Build.
---

# Starting Tool Considerations

**Default process is Spec Kit** (`specify → plan → tasks → implement → converge → REA closeout`).
Artifacts and phase contracts do not change by host. Only bootstrap and
invocation syntax change.

Greenfield vs brownfield procedures (with copy/paste prompts): 
[host-guide-greenfield-brownfield.md](host-guide-greenfield-brownfield.md).

Canonical skill path on this machine:

```text
~/.agents/skills/agentic-sdd/
```

Symlinked into Claude, Codex, Cursor, and Grok skill roots. Prefer that shared
copy; do not fork per-agent skill trees.

## Claude Code

| Item | Value |
|------|--------|
| Skill | `~/.claude/skills/agentic-sdd` (symlink) or project `.claude/skills/agentic-sdd` |
| Project rules | `CLAUDE.md` |
| Spec Kit key | `claude` via `setup-speckit-multi-agent` |
| Phase invoke | `/speckit.specify`, `/speckit.plan`, … (installed surface) |
| Compact | `/compact` after flushing `progress.md` |
| Subagents | Native Agent/Task; prefer port poteto agent for implement leaves when pstack is installed |
| pstack | Install port e.g. `michael-denyer/pstack-claude` → `/pstack:<skill>`; map in [pstack-integration.md](pstack-integration.md) |

**First actions**

1. Confirm Spec Kit is installed for this project (`specify` / `.specify/` present).
2. If missing, stop and use `setup-speckit-multi-agent` — do not invent phases.
3. Detect whether Claude pstack plugin is installed (`/pstack:poteto-mode` / plugin list). If yes, use `/pstack:*` per the phase map; if no, obligations-only and record `pstack: unavailable|claude` once.
4. Read active feature + `progress.md`, then run the owning phase command.
5. After each phase stage, update feature artifacts and `progress.md`.
6. Advance to the next Spec Kit phase without a human quiz while Final Goal work remains.
7. Inside `implement` / bug `fix`, apply poteto non-negotiables without replacing Spec Kit order (`/pstack:architect`, `/pstack:arena`, `/pstack:swarm`, `/pstack:interrogate`, …).

## Codex

| Item | Value |
|------|--------|
| Skill | `~/.codex/skills/agentic-sdd` → `~/.agents/skills/agentic-sdd` |
| Project rules | `AGENTS.md` |
| Spec Kit key | `codex` |
| Phase invoke | `$speckit-specify`, `$speckit-plan`, … |
| Agents meta | `agents/openai.yaml` in this skill (`$agentic-sdd`) |
| pstack | Codex plugin from same ports as Claude when installed; else obligations ([pstack-integration.md](pstack-integration.md)) |

**First actions**

1. Load `$agentic-sdd` or follow this `SKILL.md`.
2. Resolve feature via `.specify/feature.json` / inspect report.
3. Prefer `$speckit-*` over free-form chat for phase work.
4. If a Codex pstack port is installed, use its skill names inside phases; otherwise obligations-only.
5. Keep handoffs in files; do not rely on long chat history.

## Cursor

| Item | Value |
|------|--------|
| Skill | `~/.cursor/skills/agentic-sdd` → `~/.agents/skills/agentic-sdd` |
| Project rules | `.cursor/rules/` and/or `AGENTS.md` |
| Spec Kit key | `cursor-agent` |
| Phase invoke | `/speckit.*` or Cursor skill commands as installed |
| Subagents | Task tool; prefer `poteto-agent` for implement leaves when pstack is installed |
| pstack | Marketplace plugin `pstack` — phase map in [pstack-integration.md](pstack-integration.md) |

**First actions**

1. Ensure the agent can see this skill (user/global skills) and detect whether pstack skills are loaded.
2. Run inspect/`sdd` when `setup-speckit-multi-agent` is available.
3. Enter the owning Spec Kit phase; do not recreate plan/tasks as chat-only docs.
4. Parent model stays as the user selected; route Spec Kit phase children from `~/.cursor/rules/pstack-models.mdc` when present, else pstack defaults.
5. A Cursor turn ends when the assistant stops. Do not stop after a status report. A completion notice for one shell or subagent is not a new goal; resume the parent Final Goal. Host compaction resumes from `progress.md`. Before any user-visible status, update the `sdd-continue` line in that file. See [cursor continuation](cursor-continuation.md).
6. If Spec Kit slash commands are not invocable, execute the phase contract against the feature files.
7. Keep the critical path in this turn. Do not hand it to a background subagent and end the turn. A stop-hook follow-up that contains `sdd-continue-followup` is the same Final Goal, not a new task.
8. Inside `implement` / bug `fix`, apply poteto-mode non-negotiables without replacing Spec Kit phase order. Use `/architect`, `/arena`, `/swarm`, `/interrogate`, `/blast-radius` per the obligation table.

## Grok Build

| Item | Value |
|------|--------|
| Skill | `~/.grok/skills/agentic-sdd` → `~/.agents/skills/agentic-sdd` |
| Project rules | Grok project instructions / system prompt |
| Spec Kit key | **None native** — use file-based Spec Kit layout |
| Phase invoke | Follow Spec Kit artifact contracts manually using this skill; `/goal` for the completion condition |
| Models | `grok models` (read-only listing; not a paid probe) |

**First actions**

1. Confirm `.specify/` and the canonical spec root exist (same layout as other hosts).
2. If the project was set up only for Codex/Cursor/Claude, still honor shared
   `.specify/` + `specs/` (or `.specify/specs/`) — do not create a Grok-only fork.
3. Execute phase contracts from [phase-contract.md](phase-contract.md) against
   those files when slash/`$speckit-*` commands are unavailable.
4. Route per `model-routing.md`. pstack loads on Grok through `pstack@pstack-claude` (`grok plugin install pstack@pstack-claude --trust`) or Claude compat scanning; see `pstack-integration.md`. Prefer file handoff over chat memory.

When Spec Kit CLI or agent integrations are missing on Grok, do **not** invent
alternate directories. Either ask the user to run `setup-speckit-multi-agent`
from a supported host, or continue on the existing shared artifacts only.

## Switching hosts mid-feature

1. Flush `progress.md` and feature artifacts (handoff block from phase-contract).
2. Capture HEAD + dirty ownership (`inspect --full` when available).
3. On Codex/Cursor/Claude: `setup-speckit-multi-agent activate <agent>`.
4. Receiving host: verify snapshot before writing; one writer per checkout.

## Universal first steps (any of the four)

1. Detect host → use the table above.
2. Resolve project + active feature + phase (Spec Kit metadata).
3. Read constitution / project instructions + current feature artifacts.
4. Pin Final Goal + verification contract.
5. Run the owning Spec Kit phase (or file-equivalent on Grok).
6. Update `progress.md` after meaningful stages; compact only after flush.

## REA closeout (all four hosts)

After clean converge, run REA before finish. Prefer MCP tools named `rea` /
`user-rea`. If unavailable in delivery/repair closeout only:

```sh
npm install -g rea-agents@6.7.0   # do not upgrade a working CLI
# Pick ONE active-id: cursor | claude_code | codex | grok_build
rea setup --dry-run --yes --client <active-id> --format json
rea setup --yes --client <active-id>
```

`--client claude` / `--client grok` are invalid. Do not use `--all-detected` or
`curl | bash`. Reconnect MCP if needed. Full rules: [rea-closeout.md](rea-closeout.md).

## What does not change

- Spec Kit default workflow and phase ownership
- Shared `.specify/` + canonical spec root
- Hard boundaries for destructive actions, secrets, Spec Kit extension installs
- Narrow REA install/setup for delivery/repair closeout only (see rea-closeout.md)
- Evidence and authorization decide; reviewers advise
- Light path remains opt-in trivial-only
