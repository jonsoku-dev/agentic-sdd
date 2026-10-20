---
description: >
  How Agentic SDD consumes pstack without replacing Spec Kit phase authority.
  Cursor uses the official marketplace plugin; Claude Code and Codex use the
  pstack-claude port (/pstack:* on Claude, native skills on Codex).
---

# pstack integration (under Spec Kit authority)

**Spec Kit owns the sequence and artifacts.** pstack owns *how* a phase is
executed when the host can load it. Never let a pstack playbook reorder, skip,
or re-invent `specify → plan → tasks → implement → converge → REA`.

For greenfield vs brownfield host playbooks (Claude / Codex / Cursor), see
[host-guide-greenfield-brownfield.md](host-guide-greenfield-brownfield.md).

```text
agentic-sdd  = phase owner + Final Goal + progress.md continuity
Spec Kit     = commands + specs/plan/tasks authority
pstack       = execution style inside an admitted phase (when available)
```

## Detection

Probe once per feature (or on host change). Prefer the live skill/plugin list
over guessing. Resolve plugin paths by glob and take the highest version; never
hardcode a version.

| Host | pstack available when | Skill invoke | Plugin root (highest version) |
|------|----------------------|--------------|-------------------------------|
| **Cursor** | Official plugin `pstack` (`/add-plugin pstack`); `poteto-mode`, `architect` listed | `/architect`, `/arena`, … | `~/.cursor/plugins/cache/cursor-public/pstack/<hash>/` |
| **Claude Code** | Plugin `pstack@pstack-claude` enabled; `pstack:poteto-mode` listed | `/pstack:<skill>` | `~/.claude/plugins/cache/pstack-claude/pstack/<ver>/` |
| **Codex** | Plugin `pstack@pstack-claude` enabled (`codex plugin add pstack@pstack-claude`) | Skill loads natively by name; follow its text | `~/.codex/plugins/cache/pstack-claude/pstack/<ver>/` |
| **Grok Build** | Plugin `pstack@pstack-claude` (`grok plugin marketplace add michael-denyer/pstack-claude` + `grok plugin install pstack@pstack-claude --trust`), or Claude compat scan of an installed Claude plugin; `grok inspect --json` lists `plugin: pstack` | Skill loads by name; `/skills` shows it | `~/.grok/marketplace-cache/*/plugins/pstack/` or the Claude marketplace path via compat |
| **Other** | Only if the user linked a port into `~/.agents/skills` | Obligation table + native children | — |

Record the probe once in `progress.md`:
`pstack: <version>|<host>` or `pstack: unavailable|<host>`.

**Fallback (any host):** if no pstack skills are visible, apply the obligation
table with native Agent/Task + self-review, record `pstack: unavailable|<host>`
once per feature, and continue Spec Kit. Do not claim poteto-mode ran.

Do not fork specs into a pstack-only tree. Do not block Spec Kit delivery on
missing pstack.

### Common core vs host-only skills

The Cursor plugin and the pstack-claude port ship different skill sets.
Obligations below may **require** only the common core. Everything else is
"use if present, else perform the obligation with native tools".

- **Common core (all four hosts):** `poteto-mode`, `architect`, `arena`,
  `swarm`, `interrogate`, `how`, `why`, `blast-radius`, `tdd`, `sharpen`,
  `in-your-own-words`, `unslop`, `technical-writing`, `no-comments`,
  `show-me-your-work`, `figure-it-out`, `correct`, `reflect`, `recall`,
  `benchmark-checklist`, `create-verification-skill`,
  `maintain-verification-skill`, every `principle-*` leaf, `setup-pstack`.
- **Claude / Codex port only:** `deslop`, `thermos`, `thermo-nuclear-review`,
  `thermo-nuclear-code-quality-review`, `babysit`, `fix-ci`,
  `fix-merge-conflicts`, `get-pr-comments`, `make-pr-easy-to-review`,
  `what-did-i-get-done`, `poteto-mode/scripts/resume.mjs` (pause / pickup store).
- **Cursor only:** `create-formal-verification-skill`,
  `maintain-formal-verification-skill`, `make-bot-ui`.

Re-check this split when a plugin upgrades; the live skill list wins over this file.

### Install (user or prior session)

Install at user scope so every project gets pstack:

```text
# Claude Code
claude plugin install pstack --marketplace michael-denyer/pstack-claude --scope user
#   or in-session: /plugin marketplace add michael-denyer/pstack-claude
#                  /plugin install pstack@pstack-claude

# Codex (same port; ships a .codex-plugin manifest and a SessionStart hook)
codex plugin marketplace add michael-denyer/pstack-claude
codex plugin add pstack@pstack-claude
#   The plugin's SessionStart hook runs only after /hooks trust (never under
#   `codex exec`), so also keep the mandate text in ~/.codex/AGENTS.md between
#   <!-- pstack-mandate:start --> and <!-- pstack-mandate:end --> (copy of the
#   plugin's hooks/session-start-context.md). Enable spawn_agent:
#   [features] multi_agent = true   (or the host's current multi-agent feature block)

# Cursor
/add-plugin pstack        # official cursor/plugins marketplace

# Grok Build (same port; Claude plugin layout loads natively)
grok plugin marketplace add michael-denyer/pstack-claude
grok plugin install pstack@pstack-claude --trust
#   with Claude Code + pstack already installed, [compat.claude] scanning finds it without this
```

After install, optionally run `/setup-pstack` (`/pstack:setup-pstack` on Claude)
once to write the role→model sheet. **`/agentic-sdd` never runs setup-pstack
itself**; it only honors a sheet that already exists.

**This skill does not auto-install pstack.** If delivery needs pstack and it is
missing, record `pstack: unavailable|<host>`, use obligations, and tell the user
the install commands above once. Do not stop the Spec Kit loop for a plugin
install quiz unless the user asked to set up pstack.

## Hook precedence (Claude Code / Codex / Grok)

The pstack mandate ("invoke poteto-mode for any multi-file, design, or
unknown-cause task") reaches the model through the plugin's SessionStart hook on
Claude Code, the `<!-- pstack-mandate -->` block in `~/.codex/AGENTS.md` on
Codex, and `~/.grok/rules/pstack-mandate.md` on Grok; Cursor has no mandate
(see [poteto-mode-anatomy.md](poteto-mode-anatomy.md)). While `/agentic-sdd` is the
active Final Goal driver, that mandate is **satisfied by `O-poteto` inside
`implement` / `fix`** and by the phase map below. The hook text itself says
direct user requests take precedence; `/agentic-sdd` is that request. Do not
open a second, free-standing poteto-mode playbook or todolist. Record once:
`pstack: hook-mandate → satisfied by O-poteto`.

## Full-autonomy grant (default for `/agentic-sdd`)

Invoking this skill for delivery/repair is a **full-autonomy grant** inside the
admitted Final Goal:

1. **No phase quiz.** Advance `specify → plan → tasks → implement → converge →
   REA` (and next numbered feature while Final Goal work remains) without asking
   which phase to run next.
2. **Never block on the human** for reversible work, approach forks solvable by
   evidence/prototype, or preference calls covered by constitution + Final Goal.
   Decide, record the default in `progress.md`, continue. An empirical fork
   (behavior, timing, output) is settled by a prototype, not a question
   (`principle-never-block-on-the-human`, poteto Prototype playbook).
3. **Ask once and set `blocked` only for:** destructive ops, secrets/credentials,
   scope beyond the Final Goal, missing Spec Kit project with no authorized
   setup, or two incompatible Final Goal interpretations with no dominant
   reading from artifacts/user text.
4. Flush `progress.md` instead of status-only chat. On Cursor, keep
   `sdd-continue` current ([cursor-continuation.md](cursor-continuation.md)).

Hard boundaries in `SKILL.md` still win over autonomy.

## Phase → pstack map

Each row serves one of the seven harness layers in
[harness-layers.md](harness-layers.md) (L2 procedure, L3 sources, L5 reviewer,
L6 effort, L7 goal); that file says what each layer needs per host.
`scripts/harness_probe.py --check-map references/pstack-integration.md`
fails when the Common core list drifts from the installed plugin.

Load the named skill when the host has it (`/pstack:` prefix on Claude; bare
name on Cursor; native skill load on Codex). Otherwise perform the **obligation**
with native tools and cite the obligation id in `progress.md`. **Required**
rows must run (skill or obligation) every time the phase is entered;
**Optional** rows run when their trigger applies.

| Spec Kit phase | Obligation | Skill (common core unless noted) | Required? | All hosts must still |
|----------------|------------|----------------------------------|-----------|----------------------|
| Enter / resume | `O-sharpen` | `sharpen` · `in-your-own-words`; `recall` when resuming cold | Required | Pin Final Goal + AC; no human quiz |
| Enter (brownfield) | `O-how` | `how` over the affected subsystem | Required when existing code is touched | Cite file:line evidence in `plan.md` |
| `specify` / `clarify` | `O-specify` | `technical-writing` + `unslop` on spec prose | Required | Spec Kit specify/clarify; assumptions as assumptions |
| `plan` | `O-architect` | `architect` (parallel design runners); `arena` when shapes compete | Required when code crosses a function boundary | Plan + verification contract in `plan.md` |
| `plan` (brief asserts a fact about existing code) | `O-blast` | `blast-radius` | Required when the brief asserts "X already handles Y" | Prove or task-track the assertion |
| `tasks` | `O-sequence` | `principle-sequence-verifiable-units` | Required | Dependency-ordered `tasks.md`; each task ends in a check |
| `implement` (default) | `O-poteto` | poteto-mode non-negotiables + Principles; leaves via the host poteto agent (see Leaf dispatch) | Required | Admitted task IDs only; verify real artifacts |
| `implement` (fan-out) | `O-swarm` | `swarm` | Optional: independent packets | Disjoint files; writers in own worktree |
| `implement` (bakeoff) | `O-arena` | `arena` | Optional: ≥2 valid shapes | Pick base, graft, delete losers |
| `implement` (large) | `O-fio` | `figure-it-out` + `show-me-your-work` | Optional: cross-cutting change | Spec Kit `tasks.md` stays authority |
| `implement` (perf AC) | `O-bench` | `benchmark-checklist` + `principle-explain-the-number` | Required when an AC is a number | Baseline first; name the limiter |
| Bug `assess` | `O-why` | `why` (regression history) + `how` | Required for regressions | Assessment stays read-only |
| Bug `fix` | `O-tdd` | `tdd` when a cheap local test exists | Optional | Failing repro lands before the fix |
| Pre-converge | `O-blast` | `blast-radius` | Required | Prove or task-track external risk |
| Pre-converge | `O-hygiene` | `no-comments`; `deslop` (port only) | Required | No narrating comments; no slop in the diff |
| `converge` / bug `test` | `O-interrogate` | `interrogate` + [multi-perspective review](multi-perspective-review.md); `thermos` (port only) for auth/payment/schema/public-API risk | Required | Append gaps; no AC relaxation; see Review gate |
| Post-converge | `O-rea` | REA closeout | Required | [rea-closeout.md](rea-closeout.md) |
| Post-REA (feature close) | `O-reflect` | `reflect` → route lessons; `correct` when the same mistake repeated ≥2× this feature | Optional | Encode in structure (lint/test/type) before docs |
| Context pressure | `O-guard` | `principle-guard-the-context-window` | Required | Bulk to subagents; summaries in parent |
| Pause / compact / handoff | `O-pause` | poteto `pause-safely` (+ `resume.mjs` on port) · `session-pickup` on resume | Required before `/compact` or host switch | `progress.md` stays authoritative |
| No app harness | `O-verify-skill` | `create-verification-skill` | Optional | Repo checks first |

Exact slash names may vary by plugin version; use the installed plugin's listed
commands when they differ.

**Panel size by cost mode** ([cost-modes.md](cost-modes.md)). The fixed
per-feature cost of the map (probe, sharpen, how, architect, interrogate, REA)
is roughly constant while the defects it catches grow with surface area; one
measured sandbox run (n = 1, asymmetric prompts) put the full map at roughly an
order of magnitude more cost than bare Spec Kit on a 60-line feature while
catching three shipped defects; see
`docs/evals/2026-10-19-sandbox-ab/result.md`. Size the panels:

| Mode | `O-architect` | `O-interrogate` panel | `O-poteto` leaves |
|------|---------------|-----------------------|-------------------|
| Economy | skip for single-file specs (record `O-architect: n/a single-file`) | 2 reviewers, different families | 1 leaf, worker model |
| Balanced | run when code crosses a function boundary | sheet default (4) | per packet |
| Thorough | always | sheet default + `thermos` on the port | per packet + re-review by a second model |

### Poteto-mode under Spec Kit (critical)

**Do not** start a free-standing poteto-mode playbook that replaces Spec Kit
phases (neither `/poteto-mode` on Cursor nor `/pstack:poteto-mode` on Claude,
nor the native `poteto-mode` skill on Codex).

On the pstack-claude port, install `templates/playbooks/agentic-sdd.md` as
`.agents/playbooks/agentic-sdd.md` (`install.sh --project DIR`); a poteto-mode
run then resolves the Spec Kit phase first and stops where Spec Kit takes over.
Validate with the plugin's `check-playbooks.mjs` after a pstack upgrade.

On Cursor the official plugin (0.15.28) has no project playbooks and marks
`poteto-mode` `disable-model-invocation: true`, so the model can never open it
by itself; only the user's `/poteto-mode` does. `install.sh --project DIR` also
writes `.cursor/rules/agentic-sdd.mdc` (from `templates/cursor-rules/`) with the
same three handoffs as an always-applied rule, and the agentic-sdd skill reads
`poteto-mode/SKILL.md` as a reference for the non-negotiables instead of
invoking it. How each host reaches poteto-mode, and what the skill does once
it runs, is in [poteto-mode-anatomy.md](poteto-mode-anatomy.md).

Instead:

1. Stay on the owning Spec Kit phase command / artifact contract.
2. For each implement (or fix) batch, **read** the poteto-mode skill and apply its
   non-negotiables and principles to *how* you execute that batch. Name each
   principle leaf you actually read when it changed a decision.
3. Spawn implement leaves with the host's poteto agent (see Leaf dispatch).
4. Keep Spec Kit `tasks.md` IDs as the todo source of truth; poteto playbook todos
   must not reorder or drop Spec Kit phases.

If the user invokes poteto-mode mid-feature, Final Goal + active feature
artifacts outrank the playbook's default phase list.

## Leaf dispatch per host

One implement leaf = one admitted task packet (task IDs, owned paths, named
data shape, acceptance check, return format). Rules that hold everywhere:

- **Fresh agent per packet.** Resume an existing agent only when the new work
  needs state that lives there (its worktree, uncommitted edits, a running
  process). Stop an abandoned agent first and confirm it stopped.
- **Writers get their own worktree or exclusive branch.** This is the same
  rule as agentic-sdd's "one writer per checkout": each worktree is a checkout.
  The parent never writes a leaf's worktree while the leaf holds it.
- **Leaves do not delegate.** File pointers, not inlined context.
- **Model and effort:** role line from the pstack sheet when present, else the
  skill's default; the chosen level becomes the leaf's effort (see
  [model-routing.md](model-routing.md#pstack-bridge)).
- **You own the leaf's diff.** Review it; write your own summary.

| Host | Dispatch | Effort level | Notes |
|------|----------|--------------|-------|
| **Claude Code** | `Agent` with `subagent_type: "pstack:poteto-agent"`, `run_in_background: true`, `isolation: "worktree"` for writers; put the resolved absolute `skills/poteto-mode/SKILL.md` path in the prompt | `subagent_type: "pstack:poteto-agent-<level>"` (`low`…`max`); panels/readers use `pstack:effort-<level>` | Bare `poteto-agent` errors. Verified live on this machine. |
| **Cursor** | Native `poteto-agent` subagent (plugin `agents/poteto-agent.md`); own worktree for writers | Model line from `~/.cursor/rules/pstack-models.mdc` when present | `/architect`, `/arena`, `/swarm` spawn their own panels. The **Cursor Agent CLI** (`agent -p`) lists `poteto-agent` and `/goal`, and does not put marketplace plugin skills in the session catalog. `install.sh --cursor-cli-skills` links them into `~/.cursor/skills`. On 2026-10-19 an `agent -p --mode ask` session reported `poteto-mode` and `architect` absent from that catalog, then opened the linked `~/.cursor/skills/poteto-mode/SKILL.md` by path (heading `# Poteto mode`). |
| **Codex** | The session's spawn tool (`spawn_agent` under the configured namespace, e.g. `agents`) with instructions to read `poteto-mode/SKILL.md` in full first; `wait_agent` / `close_agent` to drain | Pass the level as `reasoning_effort`; `session` passes none | No `poteto-agent` type exists. **Always pass a model the spawn tool lists**: omitting `model` makes the host inject the parent slug, which `spawn_agent` can reject (`Unknown model gpt-6.1-sol`, verified live 2026-10-19). Listed that day: `gpt-6-luna`, `gpt-5.6-terra`, `gpt-5.6-luna`. The same day, `spawn_agent` with `model=gpt-6-luna` and `reasoning_effort=low` started and the child replied OK. `inherit-parent` in the Codex sheet is therefore unsafe — write explicit host-listed slugs. A thread-limit error is capacity, not a bad slug: stop spawning, close a finished agent, continue locally. See the port's `references/codex-tools.md`. |
| **Grok Build** | `spawn_subagent` with `subagent_type: "poteto-agent"` after `install.sh --grok-agents` (links the port's `poteto-agent.md` / `comment-sicko.md` into `~/.grok/agents/`; plugin agents such as `pstack:poteto-agent` are **not** in the enum). Without that link: `general-purpose` + read `poteto-mode/SKILL.md` first. `isolation: worktree` for writers | Persona `reasoning_effort`, `[subagents.models]` pins, `/effort low|medium|high|xhigh` | Verified live: the linked `poteto-agent` spawns and reads the plugin's SKILL.md. Grok runs SessionStart hooks but never injects their stdout, so the pstack mandate is installed as a home rule by `install.sh --grok-mandate` (`~/.grok/rules/pstack-mandate.md`), verified loaded. On 2026-10-19 a `grok -p` debug log loaded the pstack hooks file (1 hook, 0 warnings) and did not execute `session-start.sh` (`session_start=0`; `CLAUDE_PLUGIN_ROOT` unset). That script exits 1 with `CLAUDE_PLUGIN_ROOT: unbound variable` when the variable is missing, and prints the mandate when it is set. Scope precedence keeps the Claude marketplace copy (0.9.92) over the installed Grok copy (0.9.93); `harness_probe` still reports the highest version on disk. `grok models` while logged in listed `grok-4.7` (default), `grok-4.7-build-fast`, `grok-4.6`, `grok-4.5`. |

### Review gate (converge)

pstack's rule wins when pstack is present: **a required independent review
stays closed when no independent reviewer can run.** Record
`BLOCKED: independent review` in `progress.md`, keep the feature open, and
continue work that does not depend on the review. Your own review, passing
tests, or CI never count as the independent verdict. Only when pstack is
**absent** does the single-model self-review fallback in
[multi-perspective-review.md](multi-perspective-review.md) apply, with the
limit recorded.

## Model routing coexistence

1. **Parent model:** keep the user's selection (unchanged).
2. **Child roles:** the host's setup-pstack sheet when present
   (`~/.cursor/rules/pstack-models.mdc`; `~/.claude/pstack-models.md`;
   `~/.codex/pstack-models.md`), else pstack skill defaults, else parent model.
3. Effort: sheet `@level` / `default effort`, adjusted per
   [model-routing.md](model-routing.md#effort).
4. A routing suggestion is never proof a child ran.

## progress.md breadcrumbs

```text
pstack: 0.9.93|codex
pstack: hook-mandate → satisfied by O-poteto
pstack: O-how|claude|/pstack:how → plan.md §Context cites src/auth/*.ts
pstack: O-architect|cursor|/architect → plan.md updated
pstack: O-poteto|claude|pstack:poteto-agent-high → T012–T015 verified (worktree wt-012)
pstack: O-interrogate|codex|interrogate → converge gaps appended
pstack: O-pause|claude|resume.mjs → checkpoint 2026-10-19T14:02
pstack: unavailable|grok → obligations-only
```

This line form is the contract on every host, Codex and Grok included: one
line per obligation, starting at column 1 with `pstack:`, `harness:`,
`ROUTING:`, or `rea:`. Prose bullets ("- O-blast: …") are not counted by
`scripts/harness_probe.py` L7 or the eval `measure.py`, so a run that wrote
only bullets looks like it skipped the obligations.

Long unattended runs: `show-me-your-work` TSV, linked from `progress.md`.

## Anti-patterns

- Running arena/swarm *instead of* Spec Kit specify / plan / tasks.
- Running `converge` twice on one spec; carry remaining gaps into the next small spec.
- Opening a poteto playbook todolist beside the Spec Kit `tasks.md`.
- Asking "should I continue to plan?" after specify succeeds.
- Claiming multi-model consensus when only one model reviewed.
- Stopping Spec Kit because pstack is not installed (use obligations).
- Requiring a port-only skill (`deslop`, `thermos`) on Cursor.
- Hardcoding a plugin version in a path.
- Running `/setup-pstack` as part of `/agentic-sdd`.
- Auto-installing marketplace plugins without user request (except the narrow
  REA closeout install already authorized in `SKILL.md`).
- Adding a generic verification framework when repo checks already suffice.
