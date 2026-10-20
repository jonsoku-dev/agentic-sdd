# Security policy

## What this project does on your machine

`npx agentic-sdd` copies this package into `~/.agents/skills/agentic-sdd`,
symlinks it from each host's skill directory, and, after showing the plan and
asking once, installs or updates GitHub Spec Kit, pstack, and rea-agents and
edits host configuration files (`~/.codex/AGENTS.md`, `~/.grok/rules/`,
`~/.cursor/`, MCP config). `--dry-run` shows every step without changing
anything; `uninstall` reverses them. The package itself runs no network code;
dependency installs call the upstream projects' own installers.

Every npm release is published from GitHub Actions through npm trusted
publishing with a provenance attestation, and the package disallows token
publishing. Verify a tarball with:

```sh
npm audit signatures
```

## Supported versions

Only the latest release on npm receives fixes.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting:
<https://github.com/jonsoku-dev/agentic-sdd/security/advisories/new>.
Please do not open a public issue for security problems. You should hear back
within a week; fixes ship as a normal patch release with a changelog entry.
