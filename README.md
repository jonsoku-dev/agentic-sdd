# agentic-sdd

Spec-Driven Development that finishes. One skill that drives
[GitHub Spec Kit](https://github.com/github/spec-kit) end to end on
**Claude Code, Codex, Cursor, and Grok Build**, runs
[pstack](https://github.com/cursor/plugins/tree/main/pstack) inside every phase
for rigor, and refuses to call a feature done without
[REA](https://github.com/morluto/rea) runtime evidence.

```text
specify → plan → tasks → implement → converge (once) → REA closeout → next spec
```

| Layer | Owner | What it contributes |
|---|---|---|
| Phase order and artifacts | Spec Kit | `.specify/`, `specs/NNN-*/{spec,plan,tasks,converge}.md` |
| Goal, contracts, continuity | agentic-sdd | Final Goal pinning, phase contracts, `progress.md` breadcrumbs, recovery, one converge per spec, small specs |
| How a phase executes | pstack | `sharpen`/`how` on entry, `architect`/`arena` at plan, poteto non-negotiables at implement (inline by default; `poteto-agent` leaves only for context bloat, parallel work, or review independence), `blast-radius` + `no-comments` + `interrogate` at converge |
| Proof | REA | `capture_process_scenario` and friends; a feature closes on an Evidence id, not a claim |
| Resilience | seven harness layers | workspace facts, procedure, source access, action rules, reviewer evidence, effort, completion goal, probed per host by `scripts/harness_probe.py` |

Unattended by default: `/agentic-sdd` advances every phase and every remaining
numbered feature without a phase quiz. It asks once only at hard boundaries
(destructive operations, secrets, scope beyond the Final Goal, plugin installs).

## Contents

- [Quick start](#quick-start)
- [How a run looks](#how-a-run-looks)
- [Plugins (Claude Code and Codex)](#plugins-claude-code-and-codex)
- [Per host: Claude Code](#claude-code)
- [Per host: Codex](#codex)
- [Per host: Cursor](#cursor)
- [Per host: Grok Build](#grok-build)
- [Keeping dependencies current](#keeping-dependencies-current)
- [Uninstall](#uninstall)
- [Evidence that it works](#evidence-that-it-works)
- [Repository layout](#repository-layout)
- [License and third-party notices](#license-and-third-party-notices)
- [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md)

## Quick start

Requirements: Python 3.11+, Node 20+ (for `npx` and REA), `uv` (for the Spec
Kit CLI), `git`, and at least one of the four host CLIs. `bun` is needed only
by pstack's own playbook checker. Anything missing that Homebrew can install is
part of the plan the installer shows you.

### npm mode (one command)

```sh
npx agentic-sdd            # detect → plan → "Proceed? [y/N]" → install and configure every host found → verify
npx agentic-sdd --dry-run  # plan only
```

The package is published from this repository's GitHub releases with
[npm provenance](https://docs.npmjs.com/generating-provenance-statements), so
`npm audit signatures` can verify that the tarball was built by the `publish`
workflow from the tagged commit. It copies the skill into
`~/.agents/skills/agentic-sdd` (or uses a git checkout already there) and runs
the same `npx agentic-sdd` as the other modes. Later: `npx agentic-sdd@latest` to
update, `npx agentic-sdd check-deps`, `npx agentic-sdd uninstall`.

### Agent mode

Open Claude Code, Codex, Cursor, or Grok Build on your machine and paste this.
The agent reads the docs, inspects your machine, shows you the plan, and asks
once before changing anything.

```text
Install agentic-sdd on this machine.
1. Read https://raw.githubusercontent.com/jonsoku-dev/agentic-sdd/main/llms.txt and the README it links.
2. Run `npx agentic-sdd --dry-run` and show me the detected state and the full plan, including the manual items.
3. Ask me once whether to proceed. Only on yes, run `npx agentic-sdd --yes`.
4. Show me the verify output, what I must restart, and what I must do inside an IDE. Change nothing the plan did not list.
```

### Manual mode

```sh
git clone https://github.com/jonsoku-dev/agentic-sdd ~/.agents/skills/agentic-sdd
npx agentic-sdd
```

Either way the work is done by `install.sh`, which with no flags runs
`scripts/setup.py`:

1. **detects** which hosts are on this machine (`claude`, `codex`, `agent`/`~/.cursor`,
   `grok`), which prerequisites exist (`uv`, `node`, `bun`, `gh`, Homebrew),
   what pstack, Spec Kit, and REA versions are installed, which MCP entries,
   mandates, hooks, links, and model sheets are already in place;
2. **prints the plan**: every command it is about to run, in order, plus the
   few things only you can do (install pstack in the Cursor IDE, run
   `/setup-pstack` once per host to pin models);
3. **asks once** (`Proceed? [y/N]`), then applies: Homebrew prerequisites,
   the Spec Kit CLI, pstack on Claude Code / Codex / Grok through the
   `pstack-claude` marketplace, REA MCP registration via `rea setup --client`,
   the skill symlinks, the Codex `AGENTS.md` mandate block, the Grok home rule
   and agent links, the Cursor Agent CLI skill links and `sdd-continue` hook;
4. **verifies** with `deps.py check` and the harness probe for each host and
   tells you what to restart.

It touches only hosts it found, writes only marked blocks and named entries in
files you own, and is idempotent: rerun it after a `git pull` or whenever the
plan shows something missing.

```sh
npx agentic-sdd --dry-run      # detect and plan, change nothing
npx agentic-sdd --yes          # no prompt (CI, dotfiles)
npx agentic-sdd check-deps   # later: what is behind, with the update command per row
npx agentic-sdd deps         # update everything that can be updated unattended
./install.sh --link-only      # only the symlinks (the old default)
```

Every host-specific step is also available as its own flag (listed in each
host section and in `./install.sh --help`) for people who prefer to apply them
one at a time.

Then, in a repository that already has Spec Kit (`specify init` is the
`setup-speckit-multi-agent` skill's job, not this one):

```sh
npx agentic-sdd --project /path/to/repo   # project playbook (pstack port) + Cursor rule
python3 ~/.agents/skills/agentic-sdd/scripts/harness_probe.py --host claude --project /path/to/repo
```

The probe prints the pstack version it found, missing core skills, the model
sheet, one `ok`/`gap` line per harness layer, and two breadcrumb lines to paste
into `progress.md`. Start the run by asking the host for the Final Goal in
plain words, or type the skill's name (`/agentic-sdd`, `$agentic-sdd`,
`/skill agentic-sdd` depending on the host).

## How a run looks

1. **Enter.** Resolve the nearest `.specify/`, the active numbered feature, and
   its phase from the artifacts and `progress.md`. Load
   `references/pstack-integration.md` and `references/harness-layers.md`, run
   the probe, record the breadcrumbs. `O-sharpen` pins the Final Goal and the
   acceptance criteria; nobody is quizzed.
2. **Specify, plan, tasks.** Spec Kit commands write the artifacts; the
   obligations run beside them: `technical-writing` + `unslop` on the spec,
   `how` for brownfield evidence, `architect` (or `arena` when shapes compete)
   when code crosses a function boundary, `principle-sequence-verifiable-units`
   so every task ends in a check. Tasks beyond about twelve mean a smaller spec.
3. **Implement.** The host's poteto agent takes one admitted task packet at a
   time, in its own worktree, with the model and effort the pstack sheet names.
   The lead reviews every diff and never claims a dispatch it did not observe.
4. **Converge, once.** `blast-radius`, `no-comments`, then a two-to-four model
   `interrogate` panel. Act-on findings are appended to `tasks.md` and
   implemented in one bounded fix round. There is no second converge: gaps
   that survive become the next, smaller spec (`closed-carryover`).
5. **REA closeout.** Run the real artifact under REA and record the Evidence
   id in `converge.md` and `progress.md`. Disposition is `pass`,
   `not-applicable`, or `blocked-limitation`; only `pass` closes the feature.
6. **Next spec or stop.** `progress.md` ends with `Final Goal status` and a
   `Next action` line a cold session can resume from.

Every obligation leaves one line in `progress.md`, for example
`pstack: O-interrogate|claude|2x pstack:effort-low (opus, haiku) -> 1 act-on -> T004 appended`,
plus `ROUTING:` lines that record requested versus observed model and effort.
The full phase → obligation map is in `references/pstack-integration.md`.

## Plugins (Claude Code and Codex)

The same skill also ships as plugins from this repository's marketplace, in two
editions. Pick one; do not enable both, and do not also link the standalone
skill, or the skill loads twice.

| Edition | Hosts | Hooks | Use when |
|---|---|---|---|
| `agentic-sdd` | Claude Code, Codex | none | Your organization blocks plugin hooks (`allowManagedHooksOnly`, `disableAllHooks`), or you want nothing to run outside the model's own tool calls |
| `agentic-sdd-guarded` | Claude Code | `Stop`, `PreToolUse` (`ScheduleWakeup`), `PostToolUse` (`Agent`/`Task`, async) | You want the harness, not the model, to enforce the completion gate |

```sh
claude plugin marketplace add jonsoku-dev/agentic-sdd
claude plugin install agentic-sdd@agentic-sdd            # hook-free
claude plugin install agentic-sdd-guarded@agentic-sdd    # or: guarded
```

```sh
codex plugin marketplace add jonsoku-dev/agentic-sdd
codex plugin add agentic-sdd@agentic-sdd
```

Both editions carry the skill plus three small skills, named after the edition
(`/agentic-sdd:gate` or `/agentic-sdd-guarded:gate`): `gate` (runs
`progress_gate.py`), `report` (writes a tracking report), and `dashboard`
(starts the local dashboard; user-invoked only). On
Claude Code the plugin's `bin/` puts `agentic-sdd-gate`, `agentic-sdd-report`
and `agentic-sdd-dashboard` on the Bash PATH.

What the guarded hooks do, all in Python with no network access:

- **Stop** blocks a turn whose `progress.md` says "Final Goal met" while
  `progress_gate.py` fails or no reviewer subagent was spawned, and tells the
  model what to fix. It blocks at most twice per session, then lets the turn
  end and records the release, so a gate that cannot clear never traps you.
- **PreToolUse** denies `ScheduleWakeup` inside an agentic-sdd project.
- **PostToolUse** (async) appends each subagent spawn (type and description,
  never the prompt) to `<project>/.agentic-sdd/ledger.jsonl`.

The hooks act only in a directory whose `progress.md` mentions a Final Goal.
Plugin hooks run with your user permissions outside the sandbox; read
`plugins/agentic-sdd-guarded/hooks/` before installing.

### Dashboard and reports

```sh
python3 visualizer/server.py --project /path/to/repo   # or agentic-sdd-dashboard from the repo root
python3 scripts/report.py --project /path/to/repo      # or agentic-sdd-report
```

The dashboard serves on 127.0.0.1 only, reads files only, and sends no CORS
header. Tabs: flow (phase per feature, breadcrumbs), gates (`progress_gate.py`,
REA evidence per feature, the hook ledger), tokens (Claude Code transcripts for
this project, token counts only), reports, and the Kanban board at `/kanban`.
`report.py` writes `<project>/.agentic-sdd/reports/<UTC stamp>.md` with a JSON
twin and lists what changed since the previous report; commit the reports to
track progress. Codex and Grok sessions are not read for tokens yet.

## Claude Code

`npx agentic-sdd` does all of this when it finds `claude`. The manual equivalents:

**Install pstack** (the `pstack-claude` port of the Cursor plugin):

```sh
claude plugin marketplace add michael-denyer/pstack-claude
claude plugin install pstack@pstack-claude --scope user
```

**What this skill adds.** Nothing beyond the symlink is required: the plugin's
`SessionStart` hook injects the poteto-mode mandate ("invoke `pstack:poteto-mode`
for multi-file, design, or unknown-cause work"), and `/agentic-sdd` satisfies
that mandate from inside the Spec Kit phases instead of opening a free-standing
playbook. The project playbook from `npx agentic-sdd --project` anchors three
handoffs on the port's Feature and Bug fix steps so a plain request in a Spec
Kit repo still resolves the phase first.

**Dispatch.** Implement runs inline by default. A leaf that meets a
[single-loop trigger](references/single-loop-default.md) is `subagent_type: "pstack:poteto-agent"`, or
`pstack:poteto-agent-<level>` when the sheet names an effort. Review panels use
`pstack:effort-<level>` with the `model` family (`opus`, `fable`, `sonnet`,
`haiku`) from `~/.claude/pstack-models.md`, written by `/pstack:setup-pstack`.
Delegates run in their own worktree.

**Completion.** `/goal` is Claude Code's own stop-hook goal; agentic-sdd's
Final Goal in `progress.md` is the durable copy a resumed session reads.

**Headless.** `claude -p --output-format stream-json --verbose --dangerously-skip-permissions "<Final Goal>"`
exposes every `Skill` and `Agent` call for measurement.

**Known limits.** A plugin update needs a Claude Code restart to load; the
sandbox has no `CLAUDE.md`, so the probe reports L1 as a gap until you add one.

## Codex

`npx agentic-sdd` does all of this when it finds `codex`. The manual equivalents:

**Install pstack:**

```sh
codex plugin marketplace add michael-denyer/pstack-claude
codex plugin add pstack@pstack-claude
# ~/.codex/config.toml: [features] multi_agent = true   (spawn_agent)
npx agentic-sdd setup --codex-mandate
```

**Why `--codex-mandate` exists.** Codex runs a plugin's `SessionStart` hook
only after you trust it in `/hooks`, and `codex exec` never trusts hooks. So
the mandate text goes into `~/.codex/AGENTS.md` between
`<!-- pstack-mandate:start -->` and `<!-- pstack-mandate:end -->`; the installer
writes and replaces that block only.

**Dispatch.** `spawn_agent` with instructions to read `poteto-mode/SKILL.md`
first. Pass `model` as a slug the tool actually lists; omitting it makes the
host inject the parent slug, which a ChatGPT account may reject
(`gpt-6.1-sol` on the machine this was built on). Effort goes through
`reasoning_effort`. The sheet is `~/.codex/pstack-models.md`; the one shipped
in the evals pins every role to `gpt-6-luna` and forbids `gpt-5.6-*`.

**Breadcrumbs.** Write the line form (`pstack: …`, `ROUTING: …`) at column 1.
Codex tends to write prose bullets instead, and the probe and the eval
measurers only count the line form.

**Headless.** `codex exec --json --skip-git-repo-check -m gpt-6-luna --dangerously-bypass-approvals-and-sandbox "<Final Goal>" < /dev/null`.
`--full-auto` does not exist in codex-cli 0.162; the stdin redirect matters
when the command runs in the background.

**Known limits.** Codex may rewrite `config.toml` (`model`, reasoning effort)
during a session; check it after a run that behaved unexpectedly.

## Cursor

`npx agentic-sdd` does everything below except the IDE plugin install, which Cursor only offers inside the editor. The manual equivalents:

**Install pstack** from the IDE: `/add-plugin pstack` (official plugin by
Lauren Tan). Then:

```sh
npx agentic-sdd --project /path/to/repo   # writes .cursor/rules/agentic-sdd.mdc
npx agentic-sdd setup --apply-cursor-hooks    # sdd-continue stop hook (dated backup of ~/.cursor/hooks.json)
npx agentic-sdd setup --cursor-cli-skills     # expose the plugin's skills to the Cursor Agent CLI
```

**Why Cursor needs the rule.** The official plugin has no hooks, no project
playbooks, and marks `poteto-mode` `disable-model-invocation: true`: the model
cannot open it on its own, only you can with `/poteto-mode`. Without a project
rule the Agent CLI routed bug and design prompts to whatever other skill packs
were installed. `.cursor/rules/agentic-sdd.mdc` (always applied) carries the
same three Spec Kit handoffs as the project playbook, plus a one-file exemption
so a typo fix does not open the whole cycle. The skill reads
`poteto-mode/SKILL.md` as a reference for the non-negotiables instead of
invoking it.

**Dispatch.** Native `subagent_type: "poteto-agent"` (the plugin's agent,
`is_background: true`). Model lines come from
`~/.cursor/rules/pstack-models.mdc` when `/setup-pstack` wrote one. When the
account's usage limit blocks a non-default model seat, the lead implements the
leaf itself and records `observed: unavailable|usage-limit`; review seats are
recorded as `inherit`.

**Continuation.** The `sdd-continue` stop hook re-prompts the agent with the
`Next action` line from `progress.md` until the Final Goal is met
(`references/cursor-continuation.md`).

**Headless.** `agent -p --output-format stream-json --force "<Final Goal>"`.
Plan-shaped prompts can switch the agent into Cursor's plan mode, which a
headless run cannot answer.

**Known limits.** The plugin cache path
`~/.cursor/plugins/cache/cursor-public/pstack/<hash>/` changes on every plugin
update, which silently breaks the `~/.cursor/skills` links; rerun
`npx agentic-sdd setup --cursor-cli-skills` (it prunes the dead links first).

## Grok Build

`npx agentic-sdd` does all of this when it finds `grok`. The manual equivalents:

**Install pstack** (the same port, through Grok's marketplace; Grok can also
read the Claude plugin cache through `[compat.claude]`):

```sh
grok plugin marketplace add michael-denyer/pstack-claude
grok plugin install pstack@pstack-claude --trust
npx agentic-sdd setup --grok-mandate --grok-agents
```

**Why the two flags exist.** Grok runs `SessionStart` hooks but never injects
their stdout, so `--grok-mandate` writes the mandate plus the three Spec Kit
handoffs as a home rule, `~/.grok/rules/pstack-mandate.md`, which Grok always
loads. Plugin agents are not in the `spawn_subagent` enum, so `--grok-agents`
links the port's `poteto-agent.md` and `comment-sicko.md` into
`~/.grok/agents/`, where they are.

**Dispatch.** `spawn_subagent` with `subagent_type: "poteto-agent"`; the
subagent reads `poteto-mode/SKILL.md` before working. `[subagents.models]` in
`~/.grok/config.toml` pins a model when you want one; without a sheet the
`ROUTING:` lines read `model unpinned, observed unknown`.

**MCP.** Grok loads `~/.cursor/mcp.json` through `[compat.cursor]`, so REA
configured for Cursor is already visible to Grok.

**Headless.** `grok --output-format json --always-approve -p "<Final Goal>" < /dev/null`.
Put `-p` last: `grok -p --output-format json` reads `--output-format` as the
prompt.

**Known limits.** Grok is the slowest host on the same brief (roughly four
times Claude's wall time on the three-spec eval) because every spec pays the
full phase overhead and the context grows to ~180k tokens; keep its specs
small.

## Keeping dependencies current

```sh
npx agentic-sdd check-deps            # table: installed vs latest; exit 1 when anything is behind
npx agentic-sdd deps                  # update unattended, then relink mandates, agents, and skill links
python3 scripts/deps.py update --yes --hosts   # also run claude/codex/grok/agent self-update
python3 scripts/deps.py check --json   # machine-readable
```

| Component | How it is read | How it is updated |
|---|---|---|
| Spec Kit CLI (`specify`) | `uv tool list` | `uv tool install --force --from git+https://github.com/github/spec-kit.git specify-cli` |
| pstack on Claude Code | plugin cache manifest | `claude plugin marketplace update pstack-claude && claude plugin update pstack@pstack-claude` (restart to load) |
| pstack on Codex | plugin cache manifest | `codex plugin marketplace upgrade && codex plugin add pstack@pstack-claude` |
| pstack on Grok | installed-plugins manifest | `grok plugin marketplace update pstack-claude && grok plugin update` |
| pstack on Cursor | plugin cache manifest | IDE only; reported, then `--cursor-cli-skills` relinks |
| `rea-agents` pins | every host MCP config (`~/.claude.json`, `~/.cursor/mcp.json`, `~/.codex/config.toml`, `~/.grok/config.toml`, Claude desktop, Antigravity, Hermes) | pins rewritten to the npm latest with a `.bak-rea-<version>` copy, npx cache warmed; restart hosts so MCP servers respawn |
| Host CLIs | `--version` | `claude update`, `codex update`, `grok update`, `agent update` (only with `--hosts`) |

Pin REA at **6.7.0 or newer**: older releases fail every process capture whenever
an unrelated restricted process (a browser renderer) starts mid-capture.

## Uninstall

`npx agentic-sdd` only ever creates symlinks, a few files it owns, and marked blocks
inside files you own. Uninstall is the exact inverse.

```sh
npx agentic-sdd uninstall                        # everything under $HOME this script created
npx agentic-sdd uninstall --project /path/to/repo   # + the two project files
npx agentic-sdd uninstall --purge-deps --yes        # + pstack plugins and the Spec Kit CLI
rm -rf ~/.agents/skills/agentic-sdd                                           # finally, the checkout itself
```

| Removed by `--uninstall` | Detail |
|---|---|
| Skill symlinks | `agentic-sdd` in `~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills`, `~/.cursor/skills`, `~/.grok/skills` (only when they are symlinks) |
| Grok files | `~/.grok/agents/poteto-agent.md`, `~/.grok/agents/comment-sicko.md`, `~/.grok/rules/pstack-mandate.md`, `~/.grok/hooks/pstack-session-start.json` |
| Codex block | the `<!-- pstack-mandate:start … end -->` block in `~/.codex/AGENTS.md`; the rest of the file is untouched |
| Cursor CLI links | every `~/.cursor/skills/*` symlink that points into a pstack plugin cache |
| Cursor hooks | `~/.cursor/hooks/agentic-sdd-continue/` and the `agentic-sdd-continue` entries in `~/.cursor/hooks.json`; other hooks stay |
| With `--project DIR` | `DIR/.agents/playbooks/agentic-sdd.md`, `DIR/.cursor/rules/agentic-sdd.mdc`, and the directories if they became empty |
| With `--purge-deps --yes` | `claude plugin uninstall pstack@pstack-claude`, `codex plugin remove pstack`, `grok plugin uninstall pstack-*`, `uv tool uninstall specify-cli`. Cursor's plugin is removed from the IDE. Without `--yes` it only prints what it would do. |

Kept on purpose, and printed at the end of every uninstall so you can remove
them by hand:

- the `rea` MCP server entries in each host config (this script only repins
  their version; you added the servers),
- the pstack model sheets (`pstack-models.md` / `.mdc`),
- backups the script wrote (`~/.cursor/hooks.json.bak-*`, `<config>.bak-rea-<version>`),
- your projects' `.specify/`, `specs/`, and `progress.md`.

Nothing is deleted from a project except the two files above, and nothing is
deleted from a host config except the marked block and the named hook entries.

## Evidence that it works

[`docs/BENCHMARKS.md`](docs/BENCHMARKS.md) has the full picture: method,
routing table, a gate-by-gate matrix of what each host actually invoked at
every Spec Kit gate, result comparisons, and the A/B against plain Spec Kit.
`docs/evals/` keeps the records; raw headless transcripts are gitignored.

- `2026-10-19-sandbox-ab/`: Spec Kit alone versus this stack on the same brief.
  The stack caught three shipped defects, left a resumable `progress.md`, and
  cost roughly ten times as much on a 60-line feature.
- `2026-10-20-host-matrix/`: four hosts × (routing prompts, a real feature, a
  three-part goal with the split rule). All four hosts delivered the feature
  with a black-box pass, exactly one converge, and a REA Evidence id; the
  trivial prompt invoked nothing on any host; the complex goal was split into
  two or three small specs with no reconverge and no carryover. Claude $7.49
  and $12.07; Grok $7.15 and $17.65; Codex and Cursor on subscriptions.
  `result.md` lists every confound.

## Repository layout

| Path | Role |
|---|---|
| `SKILL.md` | Entrypoint the hosts load |
| `references/` | Phase contracts, pstack map, harness layers, poteto-mode anatomy, model routing, recovery, REA closeout, per-host guides |
| `scripts/` | `harness_probe.py`, `deps.py`, verification evidence and guards, criterion gate, scaffold helpers |
| `templates/playbooks/` | pstack project playbook (port hosts) |
| `templates/cursor-rules/` | Cursor project rule |
| `hosts/cursor/` | `sdd-continue` hooks and the `hooks.json` snippet |
| `hosts/claude/` | Plugin sources: guarded hooks, the gate/report/dashboard skills, `bin/` wrappers |
| `plugins/`, `.claude-plugin/marketplace.json` | Generated plugin editions and marketplace; rebuild with `python3 scripts/build_plugins.py` (the tests fail when they are stale) |
| `npx agentic-sdd` | Link, configure, update, and uninstall per host |
| `tests/` | `python3 -m unittest discover -s tests -p 'test_*.py'` |
| `evals/` | Behavioral eval cases |
| `personas/` | Provider personas, loaded only when a host asks for one |
| `agents/openai.yaml` | Codex skill metadata |
| `visualizer/` | Local dashboard (flow, gates, tokens, reports) and Kanban: `python3 visualizer/server.py --project /path/to/repo` |
| `docs/evals/` | Measured runs and their artifacts |
| `llms.txt`, `llms-full.txt` | [llms.txt](https://llmstxt.org/) index and full inline copy of the docs for agents; regenerate with `python3 scripts/build_llms.py` (the test suite fails when they are stale) |

## Versioning and releases

Semantic Versioning, driven by [Conventional Commits](https://www.conventionalcommits.org/)
on `main` and automated with [release-please](https://github.com/googleapis/release-please):

1. Commit with `feat:`, `fix:`, `docs:`, `refactor:`, `perf:` (a `!` or a
   `BREAKING CHANGE:` footer bumps the major).
2. On every push to `main`, the `release-please` workflow opens or updates a
   release pull request that bumps `package.json`, rewrites `CHANGELOG.md`
   from the commits, and shows the next version.
   GitHub holds the pull request's own CI run for approval because the
   author is `github-actions[bot]`; approve it from the Actions tab or with
   `gh api -X POST repos/<owner>/<repo>/actions/runs/<id>/approve` (the same
   commits are already tested on `main`, and the publish job tests again).
3. Merging that pull request creates the git tag `vX.Y.Z` and the GitHub
   release; the same workflow then runs tests and `npm publish --provenance`.
   Authentication is npm **trusted publishing** only (OIDC from this
   repository's `release-please.yml`, registered on the package's npmjs.com
   settings page). The package disallows token publishing, so there is no
   secret to rotate or leak.

Current version: `package.json`; history: `CHANGELOG.md`.

## Automation

| What | Where | When |
|---|---|---|
| Shell syntax + shellcheck, Python compile, unit tests | `.github/workflows/ci.yml` | every push and pull request |
| `llms.txt` / `llms-full.txt` regenerated and committed when stale | `ci.yml` (push to `main`); fails a pull request instead | every push |
| Release pull request with version bump and changelog | `.github/workflows/release-please.yml` | every push to `main` |
| npm publish with provenance (trusted publishing, no token) | `publish` job in `release-please.yml` | when the release pull request is merged |
| Upstream watch: pstack, Spec Kit, rea-agents latest vs `pins.json`; bumps every `rea-agents@X.Y.Z` pin and opens `fix(deps)` pull request | `.github/workflows/upstream.yml`, `scripts/upstream_watch.py` | weekly (Monday) and on demand |
| GitHub Actions version bumps, auto-merged when minor/patch and CI is green | `.github/dependabot.yml`, `.github/workflows/dependabot-automerge.yml` | weekly |
| Contributor hooks: regenerate `llms.txt` and run the tests before each commit | `scripts/dev-setup.sh` → `scripts/githooks/pre-commit` | on every local commit |
| Dependency freshness on your machine | `npx agentic-sdd check-deps` / `deps` | whenever you run it |

## License and third-party notices

This repository is MIT (`LICENSE`). Everything here is original to this
project; it integrates, but does not bundle, the tools below. Install each from
its own source under its own license.

| Component | Role here | Author / license |
|---|---|---|
| [pstack](https://github.com/cursor/plugins/tree/main/pstack) (Cursor plugin) | execution style inside Spec Kit phases | Lauren Tan (poteto), MIT |
| [pstack-claude](https://github.com/michael-denyer/pstack-claude) (Claude Code / Codex / Grok port) | same, on the other hosts | Michael Denyer, MIT (port of the above) |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | the phase sequence and artifacts | GitHub, MIT |
| [rea-agents](https://github.com/morluto/rea) (REA) | mandatory closeout evidence | morluto, MIT |
| @beamnxw, "Make Opus 5.5 Finish Long Tasks: A Reusable Harness Engineering Setup" (X, 2026-10-07) | the seven-layer model in `references/harness-layers.md` | idea credited; no text reproduced |

`templates/playbooks/agentic-sdd.md` quotes a few words of pstack playbook step
text only as anchors, as the pstack project-playbook format requires.
Evaluation records under `docs/evals/` come from the maintainers' own runs on
their machine.
