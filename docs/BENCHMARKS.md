# Benchmarks

What was measured, how, and what each host actually did at every Spec Kit gate.
All numbers come from files and transcripts (`docs/evals/*/measure*.py`), never
from an agent's own summary. One run per cell (n=1); treat differences under
about 2× as noise.

- Machine: one Mac (macOS 26.6.2, Command Line Tools 26.6, Node 24, Python 3.14), 2026-10-19/20.
- Hosts: Claude Code 2.1.30x (`claude -p`), Codex CLI 0.162 (`codex exec -m gpt-6-luna`), Cursor Agent CLI 2026.10.18 (`agent -p`, composer), Grok Build 1.0.55 (`grok -p`, grok-4.7-build).
- Stack: Spec Kit 1.0.1 project scaffold, pstack-claude 0.9.92–0.9.94 / Cursor pstack 0.15.28, rea-agents 6.7.0, this skill at the commit under test.
- Cost mode: Economy (single-file `O-architect` is n/a, two-reviewer interrogate, prose obligations inline).
- Project: a stdlib Python `todo` CLI (add / list / done, JSON store) that feature 001 had already delivered and closed with REA.

Reproduce: `docs/evals/2026-10-20-host-matrix/tier1.sh`, `tier2.sh`, `tier3.sh`
run the prompts; `measure_tier1.py` and `measure_tier2.py` judge the results.
Raw transcripts are not committed; `artifacts/<host>/progress.md` and the
`converge.md` files are.

## 1. Routing: does the right thing fire at the right size?

Four plan-only prompts per host ("list what you would invoke, then stop").
✔ = matches the expected route, ✘ = does not.

| Prompt | Expected | Claude Code | Codex | Cursor (with project rule) | Grok Build (with home-rule handoffs) |
|---|---|---|---|---|---|
| T: fix a typo in one file | nothing | none ✔ | none ✔ | `agentic-sdd; surgical-patch`, no cycle (mild over-pick) | none ✔ |
| F: add `todo edit` with tests | agentic-sdd → Spec Kit phases, poteto only inside `O-poteto` | ✔ (recall/sharpen → how → specify → plan+architect → tasks → implement leaf → converge once → REA) | ✔ (skill-harness → poteto-mode → agentic-sdd → project playbook → phases) | ✔ (same chain, `tdd` inside the batch) | ✔ (skill-harness → agentic-sdd → phase map) |
| B: intermittent `done` bug | agentic-sdd bug path: assess (how, why) → fix → test → REA | ✔ | ✔ | ✔ (after the rule; before it, stalled in plan mode) | ✔ (after the handoffs; before them, poteto Bug fix only ✘) |
| D: replace JSON with SQLite? | investigate / how / architect, no implement | ✔ | ✔ | ✔ (after the rule; before it, other skill packs + a stale Jev rule ✘) | ✔ |

Reading: no host over-invoked on the trivial task, and all four put the
feature through Spec Kit with poteto inside `O-poteto`. The two misroutes were
both missing-mandate problems (Cursor has no mandate hook; Grok's rule lacked
the Spec Kit handoffs) and both were fixed by the installer's templates.

## 2. Gate by gate: one real feature (`todo edit <id> <text>`)

Each cell is what the host's own `progress.md` breadcrumb says it did at that
gate. "skill" means the named pstack skill or agent actually ran; "inline"
means the lead performed the obligation itself (Economy allows this for prose
and single-file gates); "n/a" is a recorded skip with a reason.

| Gate (obligation) | Claude Code | Codex | Cursor | Grok Build |
|---|---|---|---|---|
| Enter: probe + breadcrumbs | `harness: L1 gap, L4 gap, rest ok`, `hook-mandate → satisfied by O-poteto` | probe run, L1 gap, mandate satisfied inside Spec Kit | `harness: all ok`, `pstack: 0.15.28` | `harness: L1 gap, rest ok`, `pstack: 0.9.93` |
| `O-sharpen` | inline (sharpen + in-your-own-words), AC-6/7 pinned | skill gate 0.99 → Final Goal pinned | inline, AC pinned | `sharpen` skill, AC pinned |
| `O-specify` | inline (no technical-writing/unslop run), assumptions as assumptions | spec + requirements checklist reviewed | inline | `technical-writing` + `unslop` skills |
| `O-how` | inline file:line read → `plan.md §Context` | (folded into specify) | inline → `plan.md §Context` | `poteto-agent` explainer → `plan.md §Context` |
| `O-architect` | n/a single-file (Economy) | n/a single-file (Economy) | n/a single-file (Economy) | two `poteto-agent` runners, A base, B rejected |
| `O-sequence` | principle applied, each task ends in a check | 3 ordered tasks | principle applied, T001–T002 | principle applied, 5 tasks |
| `O-poteto` (implement) | `pstack:poteto-agent-low` on sonnet, worktree, cherry-picked; lead review | `spawn_agent` delegates; native reviewer role rejected `gpt-6.1-sol`, general agent used | leaf **unavailable (usage limit)** → parent implemented, recorded | `poteto-agent` in a worktree; parent integrated the diff |
| `O-blast` | inline: unknown-id edit leaves store byte-identical | inline: unknown id returns before `save`, bytes compared | inline: exit 1, bytes equal | `blast-radius` skill, level-4 proof incl. missing-file case |
| `O-hygiene` | inline: 0 comments | read-only deslop pass: no findings | inline: no narrating comments | (not recorded for 002) |
| `O-interrogate` | 2× `pstack:effort-low` (opus, haiku) → 1 act-on → T004 | 2 reviewers (`gpt-6-luna@low`, `gpt-5.6-terra@low`), no findings | 2 seats, both `inherit` (second family on limit) → 1 act-on → T003 | 2 `poteto-agent` reviewers, no findings |
| Converge | once; T004 implemented by the lead; no second converge | once; criterion gate `advance=true` 11/11 | once; T003 implemented; no second converge | once; tasks unchanged |
| `O-rea` | MCP 6.7.0 pass `ev_d529d796…` | 3 captures, pass, `evidence/rea.json` | MCP pass `ev_7c5263c4…` | MCP pass `ev_145d76d8…` |
| `O-reflect` | skipped (optional, no repeated mistake) | – | – | – |
| `ROUTING:` lines | 1 (requested vs observed per role) | 0 in line form (prose) | 2 | 3 (`model unpinned, observed unknown`) |

Outcome of the same feature on each host:

| Measure | Claude Code | Codex | Cursor | Grok Build |
|---|---|---|---|---|
| Tasks done | 4/4 | 3/3 | 3/3 | 5/5 |
| Black-box: edit / list shows new / unknown id fails | ✔ ✔ ✔ | ✔ ✔ ✔ | ✔ ✔ ✔ | ✔ ✔ ✔ |
| Own test suite | 18 OK | OK | 18 OK | 17 OK |
| Converge count | 1 | 1 | 1 | 1 |
| REA Evidence ids | 1 | 3 | 1 | 4 |
| Commits added | 6 | 10 | 9 | 6 |
| Wall | 519 s | 582 s | 521 s (453 s rerun) | 1997 s |
| Cost | $7.49 | subscription | subscription | $7.15 |
| Top-level turns | 11 | – | – | 77 |

## 3. Gate by gate: a three-part goal with the split rule

Goal: priorities, due dates, `list --sort due|priority`, `list --overdue`,
lossless migration of existing stores, tests. Rule: split when a task list
would exceed about twelve; one converge per spec; carry over instead of
reconverging.

| | Claude Code | Codex | Cursor | Grok Build |
|---|---|---|---|---|
| Split decision | 002 priority+due → 003 sort+overdue, "by dependency" | one spec, 7 tasks ("below the threshold") | 002 → 003, same split as Claude | 002 priority+migration → 003 due → 004 sort+overdue, "combined list would pass 12" |
| `O-architect` | n/a single-file, both specs | n/a | n/a | n/a, all three |
| `O-how` | lead read, file:line cited, both specs | (in plan) | (in plan) | `how` explainer, all three |
| `O-poteto` | `pstack:poteto-agent-medium` sonnet, worktree; lead fixed a date-validation gap after review | worker rejected `gpt-6.1-sol` → lead wrote in an isolated branch | leaf unavailable (usage limit) → parent | `poteto-agent` worktree leaves, 26 → 38 → 45 tests |
| `O-blast` | 002: cross-version store round trip proven by run; 003: ISO-order premise checked on 2000 dates | caller census + legacy-store tests against the real executable | – | `blast-radius` level-4 script per spec, `BLAST_OK` |
| `O-hygiene` | 0 comments, both specs | deslop pass clean | – | `comment-sicko`, 0 kills, all three |
| `O-interrogate` | 2× `effort-medium` (opus, haiku): 002 one must-fix (padded / non-ASCII dates) → T008; 003 test gap → T006 | 2 reviewers: one LOW coverage gap → T008 | 2 seats unavailable → lead dual-perspective, clean | 2 `poteto-agent` reviewers, no findings, all three |
| Converge | 1 + 1, fix rounds implemented, no reconverge | 1, "do not reconverge" | 1 + 1 clean | 1 + 1 + 1 clean |
| `O-rea` | pass ×2 (`ev_ae808042…`, `ev_3ee0707c…`) | pass ×2 (first capture excluded: `/bin/sh` digest did not bind to `todo`; direct capture passed) | pass ×2 | pass ×3 |
| Carryover | none | none | none | none |
| Tests / `todo` lines | 28 / 110 | OK / 116 | OK / 131 | OK / 141 |
| Black-box (same script) | all ✔, invalid input exit 2 | all ✔, legacy item gets default `[P3]` | all ✔, invalid priority exit 1 | all ✔, `--sort priority` ties by id |
| Wall / cost | 1151 s, $12.07 | 643 s | 426 s | 5113 s, $17.65, 123 turns |

Reading: every host met the goal with one converge per spec and real
Evidence; the split rule produced three valid shapes (one, two, three specs).
Each extra spec pays the whole gate overhead, which is why Grok's three-spec
run cost more than Claude's two-spec run. Split by dependency, not by count.

## 4. Spec Kit alone versus this stack (A/B, 2026-10-19)

Same brief (the original `todo` CLI, AC-1..AC-5), same scaffold, same model
(Claude Code, opus), both unattended. Arm A: Spec Kit commands only. Arm B:
this skill with pstack obligations and REA closeout.

| Measure | A: Spec Kit alone | B: Spec Kit + agentic-sdd + pstack |
|---|---|---|
| Black-box AC-1..4 | all pass | all pass |
| Own tests | 6 | 15 |
| Corrupt store `{"oops":1}` | Python traceback | `todo: cannot read …: not a todo store`, exit 1 |
| Unwritable path | traceback | `todo: cannot write …`, exit 1 |
| Independent review | none | 4-model interrogate → 4 act-on tasks; blast-radius level-4 proof; second-model re-review |
| Resumable `progress.md` | none | 8 sections, 16 breadcrumbs, `Next action` |
| REA closeout | not attempted | attempted; blocked by a host toolchain defect, later passed after the fix |
| Turns / wall / cost | 21 / 135 s / $0.96 | 24 / 582 s / $11.24 |

Reading: on a 60-line feature the stack found and fixed three defects A
shipped and left an audit trail, for roughly an order of magnitude more
money. The per-feature fixed cost (probe, sharpen, how, architect, interrogate,
REA) is about constant, so the trade improves as the feature grows.

## 5. What the numbers say about the design

1. **Gates are followed, not just listed.** On every host the `progress.md`
   breadcrumbs name the gate, the host, what ran (skill, agent, or inline),
   and the artifact it changed; the converge files and Evidence ids match.
2. **Economy mode is cheap in the right places.** Prose gates and single-file
   architecture went inline on Claude, Codex, and Cursor without losing the
   black-box result; Grok chose to run the skills and paid for it in wall time.
3. **Degradation is explicit.** Cursor's usage limit and Codex's rejected model
   slug both show up as `observed: unavailable` / substitution notes rather
   than as silent success.
4. **One converge is enough when the review is independent.** Every act-on
   finding came from a second reviewer; the fix rounds closed them; no run
   needed a carryover spec.
5. **REA is the only gate that produces evidence a reader can replay.** All
   eleven feature closures across the three tiers carry an `ev_…` id.

## 6. Known limits of these measurements

- n=1 per cell; wall time includes network and plugin cold starts.
- Subscription hosts report no dollar cost.
- Cursor ran under an account usage limit the whole day, so its non-default
  model seats never ran; its numbers are the degraded path.
- Codex wrote prose breadcrumbs rather than the line form, so its gate rows
  above were read from prose by hand.
- Grok ran with no model sheet, so every `ROUTING:` line reads `observed unknown`.
- REA closeouts were process captures of a source-only CLI; no compiled
  artifact was analysed.
