# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/). From 1.0.0 on, entries are generated
by [release-please](https://github.com/googleapis/release-please) from
[Conventional Commits](https://www.conventionalcommits.org/) on `main`.

## [1.2.3](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.2.2...v1.2.3) (2026-10-24)


### Bug fixes

* end the turn to wait for a background agent, never a placeholder agent ([05f2f36](https://github.com/jonsoku-dev/agentic-sdd/commit/05f2f36212c257ac159db1a0148d339126231367))


### Documentation

* **evals:** round 3 — gate n=8 on sonnet, second repo, Codex and Grok isolated ([0995832](https://github.com/jonsoku-dev/agentic-sdd/commit/0995832c47229a279065f0c48a9401ebeda07bd6))

## [1.2.2](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.2.1...v1.2.2) (2026-10-24)


### Bug fixes

* completion gate so cheaper parents cannot skip the independent review ([a9d5b89](https://github.com/jonsoku-dev/agentic-sdd/commit/a9d5b897b0d2a04b74e381077036225b9c968983))


### Documentation

* **evals:** scorer classifies poteto-agent leaves as work, sums usage per segment, runner takes cost mode and model ([42e5dab](https://github.com/jonsoku-dev/agentic-sdd/commit/42e5dab06d7450c9f7a3196184a52154eaebd4a7))

## [1.2.1](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.2.0...v1.2.1) (2026-10-24)


### Bug fixes

* foreground gating reviewers and column-1 breadcrumbs, from an isolated A/B ([27d75b3](https://github.com/jonsoku-dev/agentic-sdd/commit/27d75b30596cafb33ec8b5aaa8a3f8f040b4cbc0))


### Documentation

* **evals:** pre-register single-loop A/B (1.1.6 vs 1.2.0, isolated) ([756bbb9](https://github.com/jonsoku-dev/agentic-sdd/commit/756bbb989248402df7a70d0efdbfe1b80d378207))
* **evals:** single-loop A/B scorer (transcript + black-box checks) ([c48166e](https://github.com/jonsoku-dev/agentic-sdd/commit/c48166e7e15e7c0f8594c5d753ab3a01994f7e14))

## [1.2.0](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.1.6...v1.2.0) (2026-10-24)


### Features

* single agent loop by default, subagents only on a named trigger ([f3702ac](https://github.com/jonsoku-dev/agentic-sdd/commit/f3702ac82f8b4e96cff640a2d22a0d356afcebaa))

## [1.1.6](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.1.5...v1.1.6) (2026-10-20)


### Documentation

* CONTRIBUTING.md and SECURITY.md ([c95a5c7](https://github.com/jonsoku-dev/agentic-sdd/commit/c95a5c741f17c6eb9a53a64f31986cc9c8c2d037))

## [1.1.5](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.1.4...v1.1.5) (2026-10-20)


### Bug fixes

* keep Python bytecode out of the npm tarball, trusted publishing only ([1b85b8d](https://github.com/jonsoku-dev/agentic-sdd/commit/1b85b8d50a3e95b0875da0ec2f9d4f88747b1041))


### Documentation

* release pull request CI needs a one-time run approval ([cd831a0](https://github.com/jonsoku-dev/agentic-sdd/commit/cd831a0f79da902b72700c13b0280700fd1cd488))

## [1.1.4](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.1.3...v1.1.4) (2026-10-20)


### Bug fixes

* **cli:** do not require git on PATH; it is only used to recognise an existing checkout ([0c2e766](https://github.com/jonsoku-dev/agentic-sdd/commit/0c2e766bf69f420eb7ae8363b9452d74a282b8b3))

## [1.1.3](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.1.2...v1.1.3) (2026-10-20)


### Bug fixes

* **cli:** keep install notices off stdout so 'where' prints only the path ([4f7c7f6](https://github.com/jonsoku-dev/agentic-sdd/commit/4f7c7f644b67084ba2c5304ff574098adc60b289))

## [1.1.2](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.1.1...v1.1.2) (2026-10-20)


### Bug fixes

* **cli:** copy the package when npx runs it from node_modules ([1a95342](https://github.com/jonsoku-dev/agentic-sdd/commit/1a953425dd22b9d773d2424a4a6f0f47b97bf5a9))

## [1.1.1](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.1.0...v1.1.1) (2026-10-20)


### Documentation

* npx-first documentation; publish job chained after release-please ([ad45921](https://github.com/jonsoku-dev/agentic-sdd/commit/ad4592156eadffd1e67d0a4ff29f7fb75dd2cba2))

## [1.1.0](https://github.com/jonsoku-dev/agentic-sdd/compare/v1.0.0...v1.1.0) (2026-10-20)


### Features

* npx agentic-sdd installer package, weekly upstream watch, CI hardening ([33f4c3f](https://github.com/jonsoku-dev/agentic-sdd/commit/33f4c3f9999946fd9964ec6937b8e2196c387589))

## [1.0.0](https://github.com/jonsoku-dev/agentic-sdd/releases/tag/v1.0.0) (2026-10-20)

First public release.

### Features

- Spec Kit delivery driver for Claude Code, Codex, Cursor, and Grok Build: Final Goal pinning, phase contracts, `progress.md` breadcrumbs, recovery, one converge per spec, small specs with carryover.
- pstack inside every phase: phase → obligation map (`O-sharpen` … `O-rea`), per-host leaf dispatch (`pstack:poteto-agent[-level]`, `spawn_agent`, native `poteto-agent`, `spawn_subagent`), model and effort routing from the pstack sheet.
- Seven harness layers mapped per host with `scripts/harness_probe.py` and its `--check-map` guard.
- Mandatory REA closeout with Evidence ids; failure table incl. the rea-agents ≥ 6.7.0 requirement.
- One-shot installer: `install.sh` detects the machine, prints the plan, asks once, applies (prerequisites, Spec Kit CLI, pstack per host, REA MCP registration, mandates, hooks, links), verifies.
- Dependency tooling: `scripts/deps.py check|update` and `install.sh --check-deps|--deps`.
- Exact-inverse uninstall: `install.sh --uninstall [--project DIR] [--purge-deps --yes]` with a printed kept-on-purpose list.
- Host wiring: Codex `AGENTS.md` mandate block, Grok home rule with Spec Kit handoffs and agent links, Cursor project rule and Agent CLI skill links, Cursor `sdd-continue` stop hook.
- Templates: pstack project playbook (`.agents/playbooks/agentic-sdd.md`) and Cursor rule (`.cursor/rules/agentic-sdd.mdc`).
- `llms.txt` / `llms-full.txt` generated by `scripts/build_llms.py`.

### Documentation

- Per-host README (install, mandate path, dispatch, headless driver, known limits).
- `references/poteto-mode-anatomy.md`: how each host reaches pstack's poteto-mode and what it does.
- `docs/BENCHMARKS.md`: routing table, gate-by-gate invocation matrices, result comparisons, A/B against plain Spec Kit.
- Evaluation records under `docs/evals/`.

### Bug fixes

- `install.sh` resolves its physical path so a symlinked checkout never links to itself.
- `install.sh --cursor-cli-skills` prunes links left dangling by a Cursor plugin-cache rotation.
