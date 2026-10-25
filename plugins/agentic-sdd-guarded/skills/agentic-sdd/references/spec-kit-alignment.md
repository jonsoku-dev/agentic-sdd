# Spec Kit alignment

Use installed commands and artifacts as execution authority. The public docs are
reference evidence, not permission to replace repository policy or upgrade tools.
This mapping was checked against the official documentation on 2026-09-25.

## Project, feature, and integration

- Resolve the nearest `.specify/`, including monorepo member projects. When set,
  `SPECIFY_INIT_DIR` selects the project; `SPECIFY_FEATURE_DIRECTORY` overrides
  `.specify/feature.json` for the active feature. Verify installed-version support.
- A Git branch is not the active-feature selector. Enforce branch alignment when
  the repository's Git workflow requires it, but do not invent that requirement
  for Git-free projects. Preserve revision and dirty ownership where Git exists.
- Read-only inspection can still encounter scripts that persist the feature
  pointer. With supported core scripts, use `SPECIFY_FEATURE_NO_PERSIST=1` for
  concurrent/read-only inspections and explicitly pin the correct feature.
- Discover the installed invocation surface: Codex commonly uses `$speckit-*`,
  other integrations use `/speckit.*`, `/speckit-*`, or their own skill syntax.
  These are agent invocations, not shell commands.
- For composition uncertainty, inspect `specify artifact list --json` and
  `specify artifact info ... --json` when the installed CLI supports them. Resolve
  project overrides, presets, and extensions before treating a bundled template
  as effective. Do not copy commands into an alternate spec store.

## Choose the process already admitted

- Feature delivery: specify → plan → tasks → implement → converge → REA closeout.
  Installed `speckit-converge` reporting converged is not finish; only REA
  disposition `pass` or `not-applicable` finishes. Add clarify, requirements
  checklists, and analyze when useful or required. Existing full production gates
  remain in force; shorter work does not need ritual artifacts.
- Repair: installed bug extension, assess → fix → test → REA closeout before
  `verified`. Assessment and testing record evidence; only fix changes source.
  Failed tests return to diagnosis/fix.
- Idea assessment: installed assess extension, intake → research → define → shape
  → decide. A go verdict is not authorization to implement; a justified no-go can
  complete an assessment request.
- Existing code: specify the bounded requested change; do not retroactively
  specify or rewrite the whole application. Reuse its architecture and tests.

The local numbered-feature continuation is a user convention, not a Spec Kit
requirement. For remaining Final Goal slices, use the next feature without asking.
Within each feature preserve the project's living, flow-back, or flow-forward
artifact rules. Reconcile accepted changes at their owning artifact; never lower
requirements just to match an implementation defect.

## Native workflows and trust

Reuse an installed workflow's status/resume state if one owns this run. The native
engine already supports loops, conditional steps, fan-out/fan-in, overlays, and
checkpointed runs; do not build another scheduler to reproduce it. Inspect its
resolved steps before choosing it. Its human gates are not silently bypassed by
forged verdict inputs. Runtime `requires` is not a sandbox.

Presets customize existing behavior; extensions add capabilities; bundles package
components. Catalog presence is not a security audit. No automatic installs,
remote shell execution, forced refresh, or global profile changes are implied by
SDD. Preserve local modifications during any separately authorized upgrade.

For cross-component work, link the authoritative contract and consumer version.
Do not edit a consumer copy to invent provider support. Local contract checks,
actual integration, merged code, and deployed readiness are distinct evidence.

## Source entry points

- [Core phases](https://github.github.com/spec-kit/reference/agentic-sdd.html)
- [Core CLI and environment](https://github.github.com/spec-kit/reference/core.html)
- [Artifacts](https://github.github.com/spec-kit/reference/artifacts.html)
- [Workflows](https://github.github.com/spec-kit/reference/workflows.html)
- [Existing projects](https://github.github.com/spec-kit/guides/existing-projects.html)
- [Spec persistence](https://github.github.com/spec-kit/concepts/spec-persistence.html)
- [Monorepos](https://github.github.com/spec-kit/guides/monorepo.html)
- [Contracts](https://github.github.com/spec-kit/guides/contract-driven-development.html)
- [Bug fixing](https://github.github.com/spec-kit/guides/bugfix.html)
- [Assessment](https://github.github.com/spec-kit/guides/assessment.html)

The entrypoint stays short and references load conditionally, following the
[Agent Skills format](https://agentskills.io/specification) and
[authoring guidance](https://agentskills.io/skill-creation/best-practices).
