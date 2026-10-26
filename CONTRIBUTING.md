# Contributing

Thanks for helping. This file is the short version; the long one is the
README's "Versioning and releases" and "Automation" sections.

## Set up

```sh
git clone git@github.com:jonsoku-dev/agentic-sdd.git
cd agentic-sdd
sh scripts/dev-setup.sh      # git hooks: regenerate llms.txt and run the tests before each commit
npm test                     # tests/ plus the Cursor hook tests
shellcheck -S error install.sh scripts/*.sh
```

Requirements: Python 3.12+, bash, Node 20+ (only for `bin/agentic-sdd.js`),
shellcheck. To try your checkout on your own hosts, run `./install.sh --dry-run`
and then `./install.sh`; it links `~/.agents/skills/agentic-sdd` to the checkout.

## Make a change

- One concern per pull request. Keep the diff small enough to review in one
  sitting.
- `SKILL.md` is what the hosts read; `references/` holds the detail it points
  at. Change the reference, then the pointer, not both texts.
- Host-specific behaviour goes under `hosts/`, `templates/`, or the matching
  README section. Say which hosts you ran it on.
- Anything that changes installer, dependency, or uninstall behaviour needs a
  test under `tests/` (they run on every pull request).
- `llms.txt` and `llms-full.txt` are generated: run
  `python3 scripts/build_llms.py` and commit the result, or let the hook do it.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/). The type drives
the changelog and the version:

| Type | Effect |
|---|---|
| `feat:` | minor bump, "Features" |
| `fix:` | patch bump, "Bug fixes" |
| `perf:`, `docs:`, `refactor:` | listed in the changelog |
| `test:`, `chore:` | hidden |
| `!` or a `BREAKING CHANGE:` footer | major bump |

## Releases

Maintainers do not tag by hand. release-please opens a release pull request
from `main`; merging it tags, publishes the GitHub release, and publishes to
npm through trusted publishing. Contributors never need npm credentials.

## Reporting problems

Bugs and ideas: [GitHub issues](https://github.com/jonsoku-dev/agentic-sdd/issues).
Security: see [SECURITY.md](SECURITY.md).
