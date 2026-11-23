#!/usr/bin/env bash
# Runs Bitwarden.TestmoValidator find-cases against origin's default branch of a bitwarden/test clone.
# Usage: find-cases.sh <clone> <worktree> <case-id>...
set -euo pipefail

fail() {
  echo "Code not checked: $1" >&2
  exit 1
}

[[ $# -ge 3 ]] || fail "usage: find-cases.sh <clone> <worktree> <case-id>..."
clone=$1
worktree=$2
shift 2

for id in "$@"; do
  [[ $id =~ ^[0-9]+$ ]] || fail "case ID '$id' is not a number"
done
[[ $worktree != -* && $(basename "$worktree") == test-origin-head ]] || fail "worktree must be a path ending in test-origin-head"
command -v dotnet >/dev/null || fail "dotnet is not installed"

origin=$(git -C "$clone" remote get-url origin 2>/dev/null) || fail "$clone is not a git clone"
[[ $origin =~ ^(https://github\.com/|git@github\.com:|ssh://git@github\.com/)bitwarden/test(\.git)?/?$ ]] ||
  fail "$clone is not bitwarden/test"

git -C "$clone" fetch --quiet origin || fail "git fetch origin failed in $clone"
if [[ -e $worktree ]]; then
  clone_git_dir=$(git -C "$clone" rev-parse --path-format=absolute --git-common-dir)
  worktree_git_dir=$(git -C "$worktree" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || true
  [[ $worktree_git_dir == "$clone_git_dir" ]] || fail "$worktree is not a worktree of $clone"
  git -C "$worktree" checkout --quiet --detach origin/HEAD || fail "could not check out origin/HEAD in $worktree"
else
  # Clears a record git keeps after the worktree folder is deleted.
  git -C "$clone" worktree remove --force "$worktree" 2>/dev/null || true
  git -C "$clone" worktree add --quiet --detach "$worktree" origin/HEAD || fail "could not create $worktree"
fi

dotnet run --project "$worktree/Bitwarden.TestmoValidator" -- find-cases --repo "$worktree" "$@"
