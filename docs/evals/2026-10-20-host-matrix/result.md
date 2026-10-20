# Host matrix result: agentic-sdd + pstack + seven layers on Claude Code, Codex, Cursor, Grok

Run 2026-10-20 on one Mac (macOS 26.6.2, CLT 26.6, rea-agents 6.7.0). Judged from
transcripts and files (`measure_tier1.py`, `measure_tier2.py`), never from the
agent's own summary. n=1 per cell; headless drivers only, so interactive-only
behaviour (Cursor plan mode, Codex `/hooks` trust) is reported as a limit.

## Tier 0, static

| Check | Claude | Codex | Cursor | Grok |
|---|---|---|---|---|
| `harness_probe.py` (sandbox) | L1 gap, L4 gap, rest ok | all ok except L1 | all ok except L1 | all ok except L1 |
| pstack root found | port 0.9.92 | port 0.9.94 | official 0.15.28 | port 0.9.93 via `[compat.claude]` |
| Mandate visible to the model (headless quote) | yes, "You have pstack." (hook) | yes after the `AGENTS.md` block; the plugin hook never ran under `codex exec` (untrusted) | **no mechanism**; `poteto-mode` is `disable-model-invocation: true` | yes (home rule) |
| Project playbook validates (`check-playbooks.mjs`) | yes | yes | script absent; plugin has no project playbooks; Bug fix step 1 text differs ("control skill") | yes (port) |
| REA MCP 6.7.0 capture | pass `ev_05f218af…`, `ev_7cd25a9a…` | server spawns 6.7.0 (`codex exec`) | server spawns 6.7.0 after restart | server spawns 6.7.0 (`grok -p`) |

Fixes landed from Tier 0: Codex mandate moved into `~/.codex/AGENTS.md`;
`templates/cursor-rules/agentic-sdd.mdc` + `install.sh --project` for Cursor;
`references/poteto-mode-anatomy.md` documents the per-host call chain. L1 gap is
the sandbox (no CLAUDE.md/AGENTS.md), L4 gap on Claude is no permission rules in
the sandbox; both are outside the Final Goal of the test project.

## Tier 1, routing (plan only, 4 prompts × 4 hosts)

Prompts: T typo in one file; F multi-file feature (`todo edit`); B intermittent
unknown-cause bug; D design question (JSON vs SQLite). Expected: T → nothing;
F → agentic-sdd + Spec Kit phases, poteto via `O-poteto`; B → agentic-sdd bug
path (assess → how/why → fix) or poteto Bug fix; D → investigation / how /
architect, no implement.

| Host | T | F | B | D |
|---|---|---|---|---|
| Claude | none ✔ | agentic-sdd → recall/sharpen → how → specify (technical-writing+unslop) → plan+architect → tasks+sequence → implement O-poteto (`poteto-agent-medium`, worktree) → converge once → REA ✔; opened `agentic-sdd.md`, `pstack-integration.md`, `rea-closeout.md`, `cost-modes.md` | agentic-sdd repair mode, bug extension absent → file-contract scaffold, assess: how + why + reproduce, then fix stage ✔ | memory → agentic-sdd → poteto-mode router → sharpen/why/how/attack-the-premise/blast-radius; architect/interrogate only if "yes" ✔ |
| Codex | none ✔ | skill-harness → poteto-mode → agentic-sdd → project playbook → specify…converge ✔ | agentic-sdd → playbook bug path → assess (how, why) → fix → converge → REA ✔ | skill-harness → poteto-mode Investigation → how → unslop ✔ |
| Cursor (no project rule) | `surgical-patch`/`cavecrew-builder` "or none" (mild over-pick) | agentic-sdd → playbook → sharpen → specify → how → plan+architect → tasks → implement poteto-agent+tdd → blast-radius → no-comments → converge+interrogate ✔ (read `agentic-sdd/SKILL.md`) | switched to Cursor plan mode and stalled on an interactive plan request; opened `diagnosing-bugs`, `investigate-first`, `agentic-sdd` (headless limit) | superpowers/caveman skills, no pstack, and a stale `jev_ask` line from an ai-memory global rule ✘ |
| Cursor (with `.cursor/rules/agentic-sdd.mdc`) | see rerun table below | – | see rerun | see rerun |
| Grok | none ✔ ("pstack mandate covers one-line edits directly") | skill-harness → agentic-sdd → phase map ✔ | poteto-mode Bug fix playbook + superpowers debugging, did **not** name agentic-sdd ✘ (project playbook not consulted). Rerun after `install.sh --grok-mandate` added the Spec Kit handoffs to the home rule (`tier1-grok-rule/`): agentic-sdd → bug stages `assess` (how, why, `assessment.md`) → `fix` (poteto Bug fix, `poteto-agent` leaf, tdd) → `test` (interrogate) → REA ✔ | poteto-mode Investigation → how → why → principles → unslop ✔ |

Findings:

1. No host over-invoked on the trivial task. The mandate's "smaller tasks, work
   directly" clause holds on all four.
2. The multi-file feature routed into Spec Kit phases on all four hosts, and all
   four kept poteto inside `O-poteto` instead of opening a free-standing playbook.
3. The bug and design cases separate hosts with a mandate from Cursor: Claude,
   Codex, and Grok reach pstack skills; Cursor without a project rule reaches
   other installed skill packs. Grok's bug answer skipped the project playbook.
4. A deleted ai-memory global rule (`_rules/agentic-sdd-jev-steer.md`) was still
   steering Cursor toward `jev_ask`; removed along with every other Jev artefact.
5. Cursor headless cannot answer a "plan" prompt that triggers its plan mode.

## Tier 1 rerun, Cursor with the project rule

Same prompts in the sandbox after `install.sh --project` wrote
`.cursor/rules/agentic-sdd.mdc` (`tier1-cursor-rule/`).

| Case | Before the rule | With the rule |
|---|---|---|
| T | `surgical-patch`/`cavecrew-builder` or none | `agentic-sdd; surgical-patch`, "no Spec Kit/pstack cycle" (over-pick: the typo sits in `specs/001-*`, and the rule's "names a numbered feature" trigger fired). The rule now carries a one-file exemption line. |
| B | stalled in plan mode, named only agentic-sdd | agentic-sdd → bug path `assess` (sharpen, how, why, repro) → `fix` (poteto-mode read as reference, Bug fix steps, tdd, architect if boundary) → `test` (interrogate, blast-radius, no-comments) → REA → PR only on policy ✔; explicitly "jev_* 없음" |
| D | superpowers/caveman skills + stale `jev_ask` | agentic-sdd read-only assessment → sharpen → how → specify/plan → architect/arena → blast-radius; poteto-mode read, not invoked ✔ |

The project rule closes the Cursor gap for bug and design routing. The
remaining Cursor-specific limit is that `poteto-mode` itself can only be opened
by the user.

## Tier 2, real feature end to end

One prompt, four hosts, same base clone: deliver `todo edit <id> <new text>` as
a new numbered feature through agentic-sdd, Economy mode, converge once, REA
closeout, unattended. Measured by `measure_tier2.py` (files + transcript).

| Measure | Claude Code | Codex (`gpt-6-luna`) | Cursor (`composer`) | Grok |
|---|---|---|---|---|
| New spec | `002-todo-edit`, 4 tasks done | `002-todo-edit`, 3 tasks done | `002-todo-edit`, 3 tasks done | `002-todo-edit`, 5 tasks done |
| Black-box: edit works / list shows new text / unknown id fails | ✔ ✔ ✔ | ✔ ✔ ✔ | ✔ ✔ ✔ | ✔ ✔ ✔ |
| Own tests | OK (18) | OK | OK (18) | OK (17) |
| Converge count | 1 (T004 appended from interrogate, implemented, **no second converge**) | 1 (zero findings, criterion gate `advance=true`) | 1 (T003 appended, implemented, no second converge) | 1 (converged, zero findings; "Do not run converge again" recorded) |
| REA Evidence | `ev_d529d796…` pass (MCP 6.7.0) | 3 ids (`ev_176462a0…`, `ev_96797c5c…`, `ev_a46d7dc9…`) in `converge.md` + `evidence/rea.json` | `ev_7c5263c4…` pass (MCP) | `ev_145d76d8…` pass (MCP) + 3 more ids in the bundle |
| Breadcrumbs added | `harness:`, `pstack: hook-mandate`, O-sharpen, O-specify, O-how, O-architect n/a, O-sequence, `ROUTING:`, O-poteto ×2, O-blast, O-hygiene, O-interrogate ×2, O-rea, O-reflect skipped | prose bullets per obligation (Skill gate, Harness, Specify, O-hygiene, O-blast, O-interrogate, Converge, criterion gate, O-rea); no `pstack:` prefix form | `pstack: 0.15.28`, `harness:` all ok, O-sharpen…O-rea, `ROUTING:` ×2 | full line form: `pstack: 0.9.93|grok`, `harness:`, O-sharpen, O-specify (technical-writing + unslop), O-how (poteto-agent explainer), O-architect (2 poteto-agent runners), O-sequence, O-poteto (worktree leaf), O-blast, O-interrogate (2 reviewers), O-converge, O-rea, `ROUTING:` ×3 |
| Implement leaf | `pstack:poteto-agent-low` on `sonnet` in a worktree, cherry-picked by the lead | `spawn_agent` delegates (35 dispatch events); native `reviewer` role rejected `gpt-6.1-sol` under the ChatGPT account, fell back to a general read-only agent | `poteto-agent` dispatch **failed on usage limit**; parent implemented locally and recorded `observed: unavailable` | `spawn_subagent` `poteto-agent` in a worktree (T002–T004), parent copied the diff and verified; model unpinned (no Grok sheet), observed unknown |
| Review | 2× `pstack:effort-low` (opus, haiku) → 1 act-on | 2 reviewers requested `gpt-6-luna@low` and `gpt-5.6-terra@low`, observed unknown | 2 seats, both `inherit` (second family unavailable on limit) → 1 act-on | 2 reviewer subagents, no findings |
| Commits added / dirty | 6 / 0 | 10 / 0 | 9 / 0 | 6 / 1 (untracked `decisions.tsv`) |
| Wall / cost | 519 s, $7.49, 11 top-level turns | 582 s (subscription) | 521 s (subscription) | 1997 s, $7.15, 77 turns (grok-4.7-build) |

Observations:

1. All four hosts delivered the feature with a passing black-box check, exactly
   one converge, a REA Evidence id, and a resumable `progress.md`. The
   one-converge rule held on every host: the act-on item from interrogate was
   appended to `tasks.md` and implemented without a second converge.
2. Routing breadcrumbs differ in shape. Claude and Cursor use the `pstack:` /
   `ROUTING:` line form; Codex wrote prose bullets. The probe's L7 check and
   `measure.py` only count the line form, so the Codex phase contract should
   name the line form explicitly (fixed below).
3. Codex's `AGENTS.md` native role table still pins `gpt-6.1-sol` / Astra,
   which the ChatGPT-account `spawn_agent` rejects; the pstack sheet
   (`gpt-6-luna`) is what made dispatch work. One reviewer seat was requested as
   `gpt-5.6-terra`, a model the user excluded; the sheet must pin the panel.
4. Cursor's Agent CLI hit its usage limit mid-run; the skill degraded correctly
   (parent implemented, `observed: unavailable|usage-limit`, review seats
   recorded as `inherit`) instead of claiming a dispatch.
5. Economy mode behaved as written: `O-architect` marked n/a for a single-file
   change, two-reviewer panel, `technical-writing`/`unslop` as inline obligations.

Cursor rerun alone (`tier2-cursor-rerun/`, fresh clone, nothing else on the
Cursor account): same outcome, 453 s, 5 tasks, one converge (T004 appended),
REA `ev_35fc5c18…` pass, black-box ✔, and still `non-inherit second family
unavailable (usage limit)`. So the limit is the account's standing state for
non-default model seats, not a parallel-run artefact; the degradation path
(parent-implemented leaf, `inherit` review seats, recorded as such) is what the
skill does under it. Grok ran with no `pstack-models.md`
sheet, so every `ROUTING:` line reads `model unpinned, observed unknown` (L6 is
defaults-only on Grok until `/setup-pstack` writes a sheet). Commit counts are
commits after the shared base `3ff57a9`, excluding the Cursor rule commit.

## Tier 3, complex goal with the split rule (all hosts)

Prompt: priorities, due dates, `list --sort due|priority`, `list --overdue`,
migration of existing stores, tests; Economy; split when tasks exceed ~12;
carryover instead of reconverge. Same black-box script on every result:
`add --priority 1 --due …`, invalid priority rejected, `--sort due`,
`--sort priority`, `--overdue`, legacy store entry preserved.

| Measure | Claude Code | Codex | Cursor | Grok |
|---|---|---|---|---|
| Specs | `002-priority-due` (8) → `003-sort-overdue` (6); split up front by dependency | one spec `002-todo-priority-dates`, 7 tasks ("below the 12-task threshold"); no split | `002-priority-due` (7) → `003-sort-overdue` (5); split 002/003 | `002-add-priority` (7) → `003-add-due-date` (7) → `004-list-sort` (7); three specs declared up front |
| Converge per spec | 1 + 1, each appended one interrogate task; no reconverge | 1 | 1 + 1 | 1 + 1 + 1 |
| REA | `ev_ae808042…`, `ev_3ee0707c…` pass | `ev_064ed609…`, `ev_4e85e0ee…` pass | `ev_fafe77f2…`, `ev_18de17b2…` pass | `ev_b505f7e4…`, `ev_ac1063c2…`, `ev_05bd7810…` pass |
| Tests / `todo` lines | 28 OK / 110 | OK / 116 | OK / 131 | OK / 141 |
| Black-box | all ✔ (invalid input exit 2) | all ✔ (legacy item shown as `[P3]`: migration fills a default priority, text kept) | all ✔ (invalid priority exit 1) | all ✔ (legacy item shown as `p3`; `--sort priority` ties broken by id) |
| Carryover | none needed | none needed | none needed | none needed |
| Wall / cost | 1151 s, $12.07 | 643 s | 426 s (leaf `unavailable|usage-limit`, parent implemented) | 5113 s, $17.65, 123 turns |

The split rule produced different but valid shapes: Claude and Cursor split by
dependency into two specs, Codex kept one 7-task spec, Grok planned three. The
one-converge rule held everywhere, and no host needed a carryover spec because
the single fix round closed every interrogate finding.

## Cursor `/poteto-mode` under agentic-sdd

`agent -p "/poteto-mode <feature, plan only>"` in the base sandbox with the
project rule installed (`tier1-cursor-rule/cursor-slash-poteto.jsonl`): the
session opened `agentic-sdd/SKILL.md` and the Feature playbook, judged that 001
is closed and `edit` needs a new numbered feature, listed the Spec Kit phases
with their obligations (sharpen → how → specify → plan+architect → tasks →
implement as `O-poteto` with `poteto-agent` leaves → blast/no-comments →
converge+interrogate → REA), and stated it would not open a free-standing
Feature todolist. The user-invoked path hands off to Spec Kit as designed.

## Judgment

**Does agentic-sdd + pstack + the seven layers produce synergy on every host?**
Yes on all four hosts for the real feature, with measurable evidence (black-box
pass, one converge, REA Evidence, breadcrumbs), and yes for proportional
routing on the four plan-only prompts. The parts reinforce each other in a specific way:

- Spec Kit supplies the phase order and the artifacts (L2 procedure, L7 goal);
  pstack supplies the per-phase rigor (how/architect/interrogate/poteto leaves,
  L5 reviewer evidence, L6 effort routing); the harness probe and `progress.md`
  breadcrumbs make the whole thing resumable and auditable (L1, L7). Where one
  layer was missing the others compensated visibly: Cursor's dispatch limit
  degraded to a recorded parent-implemented leaf, Codex's untrusted hook was
  replaced by the AGENTS.md mandate, the REA closeout caught nothing on these
  small features but ran on every host with real Evidence ids.
- Invocation is proportional. The trivial task invoked nothing on all four
  hosts; the feature invoked the full phase map; the bug and the design question
  routed to assess/investigate paths without implementing.
- Cost is the price: $7.49 for a 30-line feature on Claude (Economy, 2
  reviewers), $12.07 for the two-spec Tier 3. Subscription hosts hide the
  dollar figure but spent 7–33 minutes of wall time per feature. On the same
  Tier 3 brief, wall time ran about 1× (Claude, Cursor) / 0.6× (Codex, one spec)
  / 4.4× (Grok, three specs, $17.65, 123 turns, 184k-token context at the end).
  Every extra spec pays the full phase overhead (probe, sharpen, how, specify,
  plan, tasks, converge, REA), so "keep specs small" trades per-spec context
  size for more fixed cost; the split should follow dependencies, not a count.

What this run changed in the skill: `install.sh --codex-mandate` (mandate block
in `~/.codex/AGENTS.md`); `--grok-mandate` now appends the three Spec Kit
handoffs; Cursor project rule template and `--project` installer step;
`poteto-mode-anatomy.md`; the breadcrumb line-form contract made explicit for
Codex; GPT-5.6 exclusion written into the Codex sheet; the stale Jev global
memory rule deleted; raw headless transcripts gitignored (`*.jsonl`, `*.err`).

Not exercised: Cursor with a non-default model seat available (account usage
limit throughout this day); Codex `/hooks`-trusted plugin hook (the AGENTS.md
block covers it); REA on a compiled artifact (all runs were source-only
scripts captured with `capture_process_scenario`).
