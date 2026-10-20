# Model and effort routing

Use at a phase/role change or a recovery decision, not every tool call. Keep the
user's active parent model and effort. The primary chooses a bounded child
configuration from the written rules below; nothing rewrites the parent session,
global config, or project policy. No external advisor service is consulted.

## Source of truth, in order

1. **User role line** in the pstack sheet when present
   (`~/.cursor/rules/pstack-models.mdc`, `~/.claude/pstack-models.md`,
   `~/.codex/pstack-models.md`). A role line, including `@<level>` and the
   `default effort` line, is final for that role.
2. **pstack skill defaults** (poteto-mode Models section / `models.json` tiers):
   worker model for feature and refactoring leaves, default model for bug-fix,
   perf, judgment and prose, strongest model for the hardest judgment, the
   diverse panel for `arena` / `architect` / `interrogate`.
3. **Parent model** (`inherit-parent` / omit `model`) when neither names a value
   or the host cannot pin a child model.

Read live model names from this session's `Agent` / spawn tool schema or the
host's model listing. A saved profile alone is not active-session status. Never
write or dispatch a slug you have not seen listed. Never start paid probes merely
to widen the catalog.

## Effort

Start from the role's `@level` or the sheet's `default effort` (`session` = no
effort passed). Then, per poteto-mode's Subagents rule: raise one step (up to
max) for the hardest or subtlest work; lower one step for judgment; lower two or
more for routine mechanical work. Raise effort after a concrete unresolved
observation, not for a missing server, credential, or tool. Lower it for a
bounded follow-up once the uncertainty is resolved. Keep the current adequate
choice on ties; no model churn on unchanged evidence. If the host rejects a
level, use the role's line or default and say so; do not try another level.

Current Codex defaults when no sheet exists: Sol `medium` for implementation
and coordination, Luna `high` for bounded mechanical work, Astra `low` for the
hardest or highest-risk reasoning. These are defaults, not overrides of user
choices. GPT-5.6 remains excluded on this machine.

## Dispatch per host

| Host | Model | Effort |
|------|-------|--------|
| Claude Code | `model` on the `Agent` call (family name: `opus`, `fable`, `sonnet`, `haiku`) | `subagent_type: "pstack:poteto-agent-<level>"` for code leaves, `pstack:effort-<level>` for readers/panels |
| Codex | `spawn_agent` `model` set to a slug the tool lists (never omitted: the host substitutes the parent slug and may reject it) | `reasoning_effort: <level>` |
| Cursor | Native `poteto-agent` with the sheet's role model | Host-native effort when exposed; otherwise record `unknown` |
| Grok Build | `spawn_subagent` with `subagent_type: "poteto-agent"` (user-level link from `install.sh --grok-agents`); `[subagents.models]` pins the model | Persona `reasoning_effort`; `/effort` for the session |

If dispatch is unavailable or its slots are exhausted, continue locally; do not
substitute another CLI to bypass a native-agent limit. A thread-limit error is
capacity, not a rejected slug.

## Apply and observe

Pass objective, owned paths, non-goals, acceptance, and return format. Receive
changed paths, commands/outcomes, remaining risks, and available execution
identity. Compare the returned model/effort to the requested pair when the host
exposes it; otherwise record `unknown`. An invocation string or `planned` result
is not runtime evidence. A routing decision is never proof a child ran.

Count actual escalation-class dispatches against the admitted budget, not
rejected picks. Slot exhaustion and provider failures do not consume an
unstarted pass. When the budget is exhausted, use the next capable permitted
path; do not invent budget or abandon the goal to use the strongest model.
Cost comes from actual usage telemetry when available; missing costs stay
unknown.

Record in `progress.md`:
`ROUTING: <role> → <model>@<level> (source: sheet|default|parent) observed: <model>@<level>|unknown`
