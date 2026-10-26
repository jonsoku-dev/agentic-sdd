---
description: Mandatory REA reverse-engineering closeout after Spec Kit converge / Final Goal finish. Includes install when missing.
---

# REA Closeout (Mandatory)

After a clean Spec Kit `converge` (or before writing bug `test` verdict
`verified`), and before declaring the feature or Final Goal finished, run a
**REA** analysis pass. Scores and chat review do not replace REA Evidence.

Do **not** treat REA as a Spec Kit phase command. Converge still only assesses
and appends tasks. Material REA findings get one bounded fix round: `implement` (features) or
`fix` (bugs) via recorded tasks/deviations, rerun the affected checks (no second
`converge`), then run REA again on the new code state. A further material
finding on the same spec carries over to the next small spec. Previous Evidence
IDs are stale after edits.

Installed `speckit-converge` reporting `converged` (review / PR / stop) is **not**
finish — run REA closeout on that code state first.

## When it is required

| Exit | REA required? |
|------|----------------|
| Feature `converge` clean (no new tasks) | **Yes** |
| Final Goal complete (no remaining admitted features) | **Yes** |
| Bug `test` before writing `verified` | **Yes** (scoped to the fix surface) |
| Light-path trivial-only exit | Same pass rule if a runnable/build artifact exists; else `not-applicable` with reason |
| Read-only audit / plan-only mode | Optional; **do not** install or mutate |

## Dispositions (finish rule)

| Disposition | Meaning | May finish Final Goal / feature / bug verified? |
|-------------|---------|--------------------------------------------------|
| `pass` | Real Evidence ID(s) present; required capture families for the artifact type; bound to current code state; no material findings | **Yes** |
| `not-applicable` | No runnable or build artifact exists (with recorded reason) | **Yes** |
| `tasks-appended` | Material findings queued for implement/fix | **No** — continue Spec Kit loop |
| `blocked-limitation` | Tooling failed after install/alternate path; command + exit + remediation recorded | **No** — stays open. A user dropping REA is a recorded scope change to `not-applicable` only when no runnable/build artifact exists, not a finish on this disposition |

**Material finding** means: acceptance miss, broken P1 path, page/runtime error
that violates acceptance, integrity contradiction, or user-visible wrong behavior.

`pass` requires at least one evidence id copied **verbatim** from the tool result
(not the placeholder string `ev_…`).

`scripts/progress_gate.py` is the only completion predicate. It accepts
`rea: <feature>|pass|ev_…` or
`rea: <feature>|not-applicable|<why there is no runnable artifact>`, and it
rejects `blocked-limitation` and `tasks-appended`. Every feature directory
under `specs/` or `.specify/specs/` is in scope except `overview` and
`000-overview`. A directory that predates this Final Goal stays out of scope
only with a column-1 line
`gate: exclude|<feature-directory>|<why it predates this Final Goal>`.
Do not write "Final Goal met" until the script prints `ok`.

## Ensure REA is available

Prefer the host MCP server (`user-rea` / `rea` tools) when already connected.
Otherwise install the CLI, then wire **only the active host**.

### Detect

```sh
command -v rea >/dev/null && rea --version
# or: MCP exposes capture_browser_scenario / inspect_web_page / analyze_javascript_application
```

### Install CLI (delivery/repair closeout only)

Authorized **without** extra user quiz **only when**:

- Mode is delivery or repair closeout (not read-only / plan / audit), **and**
- MCP tools and `rea` CLI are both missing, **or** CLI exists but this host’s
  MCP registration is missing/stale for the active client id

```sh
# Node 22.19+ / 24.11+ / 26+ required. Abort if outside that set.
node -p "process.versions.node"
# Pin a known good package; do not upgrade a working CLI
npm install -g rea-agents@6.7.0
rea --version
```

Do **not** use `curl | bash` for this skill. Do **not** use `--all-detected`.

Optional engines reported unhealthy by `rea doctor` (Ghidra, IDA, jadx, Swift
helper) are **not** blockers when an alternate REA path for this artifact works.

### Wire agent MCP (active host only)

| Host | `rea setup --client` value |
|------|----------------------------|
| Claude Code | `claude_code` |
| Codex | `codex` |
| Cursor | `cursor` |
| Grok Build | `grok_build` |

`--client claude` and `--client grok` are **invalid** (VALIDATION_ERROR).

```sh
rea setup --dry-run --yes --client <active-id> --format json
rea setup --yes --client <active-id>
```

If MCP was just registered, reload/reconnect the agent MCP session before
continuing. If tools remain invisible, fall back to CLI
`rea capture-browser-scenario` / `rea analyze-javascript-application` / etc.

## What to run

Pick the **smallest** REA path that covers the delivered artifact:

| Deliverable | Preferred REA operations |
|-------------|--------------------------|
| Web / SPA | See **Web / SPA** below |
| Node / Electron JS app | MCP `analyze_javascript_application` or CLI `rea analyze-javascript-application` on build output (`detail: summary`); UI scenario if present |
| Native / mobile package | `analyze` / package inspect appropriate to the format |
| Pure library (tests only) | Static REA on built artifact + record test Evidence; no fake UI scenario |

Always:

1. Bind analysis to **current** code state (HEAD + relevant dirty paths, or content identity).
2. Record verbatim Evidence IDs in `progress.md` and `converge.md` (or bug `test.md`).
3. After the one implement/fix round from REA findings: invalidate prior REA IDs; rerun affected checks (no second converge); run REA again. Still material → `closed-carryover` into the next spec.

### Web / SPA

1. Serve the existing preview/build URL (do not invent a second app).
2. Run MCP `capture_browser_scenario` or CLI `rea capture-browser-scenario`.
   - **Launch** mode: provide a local browser `executable_path`.
   - **Connect** mode: only if a loopback CDP endpoint is **already** up; then
     `list_browser_targets` → use that `target_id`. A Vite URL is **not** a CDP endpoint.
3. `actions` must include the P1 control (`click` / `fill` / `press`), not only a wait.
4. Set capture **explicitly**. Required `at_end`: `url` **plus** `accessibility` or `dom`;
   add `storage` when acceptance touches storage. Required `events`: `console`,
   `page-errors`, `network`.
5. A URL-only default capture is **not** a pass.
6. `inspect_web_page` / `rea inspect-web-page` is an optional passive follow-up.
   It cannot navigate or click and **cannot** alone satisfy P1.

### Failure handling

| Failure | Action |
|---------|--------|
| REA not installed | Install per above (closeout scope), retry once |
| MCP not visible after setup | Reconnect MCP; else CLI equivalents |
| Provider toolchain broken | Try alternate REA path (scenario vs static). If all fail → `blocked-limitation` (does **not** finish) |
| Material defect | One bounded fix round, affected checks, then REA again; still material → carry over to next spec |
| Flaky observation | One discriminating retry; then unresolved / tasks |
| `cleanup_incomplete` with `live candidates <pid>=environment_unavailable`, even on `/usr/bin/true`; intermittent | rea-agents ≤ 6.6 fails closed when an unrelated same-user process whose environment is withheld (`CS_RESTRICT` images such as Chrome Helper renderers) starts during the capture. Verified on macOS 26: 6.4.0 fails, 6.7.0 records those PIDs as `restricted_process_environment_withheld` and passes. Pin `rea-agents@6.7.0` or newer in the host MCP config (`~/.claude.json`, `~/.cursor/mcp.json`, `~/.codex/config.toml`, `~/.grok/config.toml`) and restart that server. Until then, retry through the CLI (`npx -y rea-agents@6.7.0 capture-process scenario.json --format json --full-output`, scenario keys `executable`, `arguments`, `working_directory`, `environment`, `timeout_ms`, `finalization_ms`) and record its Evidence. Reconnecting an old-version server does not fix it |
| `capture_process_failed` with `xcrun`/`swiftc` `redefinition of module 'SwiftBridging'` | Command Line Tools older than macOS (e.g. CLT 16.4 on macOS 26): `sudo softwareupdate -i "Command Line Tools for Xcode <os version>"` from a real terminal (sudo needs a TTY); verify with `xcrun swiftc` on the package's `bridge/process/*.swift` |
| Source-only interpreted script (no binary/bundle) | `open_binary` is n/a; use `capture_process_scenario` on the real command. If the host capture helper itself fails (toolchain error), that is `blocked-limitation` with the host fix named in `Next action`, not `not-applicable` |

Never mark Final Goal complete with a silent skipped REA when a runnable
artifact exists and REA could be installed under the rules above.

## Progress / converge recording template

```markdown
## REA closeout
- Tooling: MCP user-rea | CLI rea@x.y.z | installed-this-session: yes/no
- Host setup client: cursor | claude_code | codex | grok_build
- Artifact: <path or URL + revision/dirty binding>
- Evidence IDs: <paste verbatim ids from tool output>
- Findings: none | <short list>
- Disposition: pass | not-applicable | tasks-appended | blocked-limitation
- If blocked-limitation: command, exit, alternate tried, remediation
```

## Hard rules

- REA closeout is mandatory for Spec Kit delivery/repair exits in the table above.
- Install/setup authorization is **narrow**: delivery/repair closeout only; active
  host client id only; pinned package when installing; no remote-shell installer.
- Installing Spec Kit extensions/presets/integrations still requires confirmation.
- Do not weaken Spec Kit acceptance to satisfy REA; fix or task-track instead.
