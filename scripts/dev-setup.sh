#!/bin/sh
# Contributor setup: git hooks that keep llms.txt current and run the tests before every commit.
set -e
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath scripts/githooks
echo "hooks enabled (core.hooksPath=scripts/githooks)"
