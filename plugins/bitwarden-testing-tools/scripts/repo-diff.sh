#!/usr/bin/env bash
#
# repo-diff.sh — list the files a branch changed in one repo, relative to origin/main.
#
# The web-test planning skills (scoping-playwright-application-context and
# mapping-services-under-test) call this instead of invoking git directly, so their
# Bash grant can be scoped to this one script rather than to git. Keeping `git -C`
# inside the script means no open-ended git subcommand is ever exposed to the
# permission layer.
#
# Usage: repo-diff.sh <repo-path>
#   <repo-path>  path to the repo to diff (absolute, or relative to the cwd)
#
# Prints the changed file paths (repo-relative, one per line) on stdout. Exits
# non-zero when the argument is missing or the diff base cannot be resolved, so
# callers keep their stop-on-failure behavior.
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: repo-diff.sh <repo-path>" >&2
  exit 2
fi

git -C "$1" diff --name-only origin/main...HEAD
