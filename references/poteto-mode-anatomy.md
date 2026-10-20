# poteto-mode anatomy: when it is called, how, and what it does

Read this before relying on pstack inside a Spec Kit phase. It describes the
pstack `poteto-mode` skill as shipped in the Cursor official plugin (0.15.28)
and the `pstack-claude` port (0.9.92–0.9.94), verified on this machine on
2026-10-20. Nothing here duplicates the skill text; it maps the call chain and
the host differences that decide whether the skill ever runs.

## 1. What poteto-mode is

One skill file (`skills/poteto-mode/SKILL.md`, ~170 lines) plus 23 playbooks
(`playbooks/*.md`), 24 one-principle leaf skills (`principle-*`), a delegate
agent (`agents/poteto-agent.md`), effort variants (`effort-agents/`), and a
model sheet mechanism (`/setup-pstack` → `pstack-models.md` / `.mdc`).

When it runs it does four things, in this order:

1. **Routes.** The Non-negotiables table maps the task shape to another pstack
   skill: `how` for any nontrivial change, `architect` when code crosses a
   function boundary, `arena` / `swarm` for fan-out, `interrogate` for contested
   design, `unslop` / `technical-writing` for prose, `deslop` before commit,
   `no-comments` before review, `benchmark-checklist` for any measured number,
   `show-me-your-work` for long autonomous work.
2. **Opens a playbook todolist.** It matches the task to one of the playbooks
   (Feature, Bug fix, Investigation, Refactoring, Prototype, Perf, …), copies
   that playbook's numbered steps verbatim into the session's task list, and
   requires a `skip: <reason>` line for any step it does not do. A repository
   can extend a playbook with `.agents/playbooks/<name>.md` (port only, see §4).
3. **Delegates leaves.** Every code-writing step inside a playbook goes to a
   `poteto-agent` subagent (fresh per task, own worktree, explicit model and
   effort from the sheet or the Models defaults). The chat that received the
   request keeps the playbook, reviews every diff, and writes the reply.
4. **Verifies and replies.** "Prove it works" on the real artifact, then a
   reply in the Writing-the-reply shape (short declarative sentences, evidence
   or label on every claim, no long-dash).

## 2. When it is called, per host

| Host | What makes the model call it | Who can invoke | Delegate type | Verified how |
|------|------------------------------|----------------|---------------|--------------|
| Claude Code | Plugin `SessionStart` hook (`hooks/hooks.json` → `session-start.sh claude`) prints `session-start-context.md`: "You have pstack. Invoke `pstack:poteto-mode` when a task touches more than one file / is a design choice / is an unknown bug or perf issue." | Model via the `Skill` tool, or user `/pstack:poteto-mode` | `subagent_type: "pstack:poteto-agent[-<level>]"` | Headless `claude -p` quoted "You have pstack." |
| Codex | `~/.codex/AGENTS.md` block `<!-- pstack-mandate:start -->` carrying the same text. The plugin's `codex-hooks.json` `SessionStart` hook exists but runs only after the user trusts it in `/hooks`; `codex exec` never trusts it, so the AGENTS.md block is the reliable path. | Native skill load (`$poteto-mode`), or the mandate | `spawn_agent` with a prompt that reads `poteto-mode/SKILL.md` first; `model` must be a slug the tool lists (`gpt-6-luna` here) | Headless `codex exec -m gpt-6-luna` quoted the three conditions after the AGENTS.md block was added; before that, only AGENTS.md routing text was seen |
| Grok Build | `~/.grok/rules/pstack-mandate.md` (written by `install.sh --grok-mandate`). Grok never injects hook stdout, so the rule is the only path. Skills come through `[compat.claude]` from the Claude plugin cache. | Model, or user `/poteto-mode` | `spawn_subagent` `subagent_type: "poteto-agent"` via `~/.grok/agents/poteto-agent.md` link (`install.sh --grok-agents`); plugin agents are not in the enum | Headless `grok -p` quoted "You have pstack." and listed `poteto-agent` |
| Cursor | **Nothing automatic.** The official plugin has no hooks, and `poteto-mode`'s frontmatter sets `disable-model-invocation: true`, so the model cannot open it on its own. | User `/poteto-mode` only. Other pstack skills (`architect`, `how`, `interrogate`, …) stay model-invocable. | Native `subagent_type: "poteto-agent"` (plugin `agents/poteto-agent.md`, `is_background: true`) | Plugin files read on disk; `agent -p` headless answers `ok`; invocation under quota not yet exercised |

Consequence for agentic-sdd: on Claude, Codex, and Grok a plain multi-file
request in a Spec Kit repo reaches poteto-mode through the mandate, and the
project playbook (port) or the agentic-sdd skill hands the phase back to Spec
Kit. On Cursor the agentic-sdd skill must **read** `poteto-mode/SKILL.md` as a
reference and apply its non-negotiables itself, because it cannot invoke the
skill; the user can still type `/poteto-mode`. `pstack-integration.md`
("Poteto-mode under Spec Kit") states the resulting rule.

## 3. What each call does to the session

- **Context cost.** The skill body (~170 lines), the matched playbook, every
  `principle-*` leaf it cites, and the Models/Reasoning-effort sections load into
  the parent. Leaves are read in full before they are cited. This is why
  agentic-sdd loads it once per feature and names principle leaves only when
  they changed a decision.
- **Todolist takeover.** The playbook steps become the first items in the task
  list. Under Spec Kit, `tasks.md` stays the authority; the project playbook
  (port) anchors `**Before**` changes on Feature step 1, Bug fix step 1, and
  Feature step 8 ("Run **Opening a PR**") so the playbook stops where Spec Kit
  resumes (`converge`, REA closeout).
- **Subagent policy.** Fresh `poteto-agent` per task, `run_in_background: true`,
  own worktree, explicit `model` per role from the sheet (Claude families
  `opus/fable/sonnet/haiku`; Codex slugs; Cursor `grok-4.7-xhigh-fast` for code,
  `claude-opus-5-5-xhigh` for prose and judgment by default), effort via
  `-<level>` agent variants on Claude, `reasoning_effort` on Codex, persona
  effort on Grok, speed tier on Cursor. A review gate with no independent
  reviewer stays `BLOCKED`.
- **Autonomy.** "Just do it" for reversible work; always pause on force-push,
  deploys, deletion, customer messages. Full-autonomy grants ("run until done")
  remove the question step for calls the grant covers.
- **Reply shape.** Every playbook ends in a reply with evidence labels; that is
  also the shape agentic-sdd's `progress.md` breadcrumbs follow.

## 4. Port vs Cursor plugin differences that matter here

| Topic | pstack-claude port (0.9.9x) | Cursor official (0.15.28) |
|-------|-----------------------------|---------------------------|
| Model invocation of poteto-mode | allowed (mandate) | `disable-model-invocation: true` |
| Session mandate hook | Claude hook, Codex hook (needs `/hooks` trust), Copilot | none |
| Project playbooks (`.agents/playbooks/*.md`, `check-playbooks.mjs`) | yes | **no** (no section, no script) |
| Bug fix step 1 wording | "via the driver skill" | "via the control skill" |
| Feature step 4 model text | "default in poteto-mode's Models section" | "default `grok-4.7-xhigh-fast`" plus "fast or standard speed" |
| Models section + Reasoning effort section | present (`models.json` stamped) | absent; `/setup-pstack` budget sets levels, `xhigh` default |
| `deslop` | bundled | from `cursor-team-kit` |
| Driver skill | `run` / project `verify` | `control-cli` / `control-ui` from `cursor-team-kit` |
| Review-gate rule ("stays closed when no independent reviewer can run") | present | absent |
| Delegate type name | `pstack:poteto-agent` | `poteto-agent` |

`templates/playbooks/agentic-sdd.md` quotes the port's step text, so it applies
on the port only. On Cursor, use `templates/cursor-rules/agentic-sdd.mdc`
(installed by `install.sh --project DIR`), which carries the same three
handoffs as an always-applied project rule.

## 5. Checklist agentic-sdd runs against this

1. `scripts/harness_probe.py --host <host>` L2 shows the pstack root and no
   missing core skills.
2. The mandate is visible to the model (Claude hook text, Codex AGENTS.md
   block, Grok home rule); on Cursor record `mandate: n/a (user /poteto-mode)`.
3. Port only: `node <root>/skills/poteto-mode/scripts/check-playbooks.mjs` from
   the repository root passes after any pstack upgrade.
4. The delegate type the host accepts is the one in `pstack-integration.md`
   Leaf dispatch; a rejected name is not a capacity error.
5. Breadcrumb `pstack: O-poteto|<host>|<delegate> -> <task ids> verified` lands
   in `progress.md` before Spec Kit `converge` starts.
