#!/usr/bin/env bash
# Prepares the read-only context the owning-team classifier works from, so the agent itself needs no
# shell, git, or gh access. Every caller uses it: the CI workflow, the classify-owning-team-review
# skill, and the evals.
#
# Usage:
#   prepare-context.sh pr <number> [<owner>/<repo>]
#   prepare-context.sh local [<base-ref>]
# Run from the root of a checkout of the repository. Prints the new context directory's path.
#
# The context directory holds:
#   pr.json          mode, number (null in local mode), base_sha, head_sha
#   files.txt        changed paths, one per line
#   pr.diff          the diff from base_sha to head_sha
#   CODEOWNERS.base  CODEOWNERS at base_sha, when one exists
#   CODEOWNERS.head  CODEOWNERS at head_sha, when one exists
#   base/            an export of base_sha, with no .git directory
#
# The PR title and body are never fetched: the classifier judges the change, not its description.
set -euo pipefail

fail() { echo "prepare-context: $*" >&2; exit 1; }

mode="${1:-}"
case "$mode" in
  pr)
    number="${2:-}"
    expected_repo="${3:-}"
    [[ "$number" =~ ^[0-9]+$ ]] || fail "pr number must match ^[0-9]+$"
    if [[ -n "$expected_repo" ]]; then
      [[ "$expected_repo" =~ ^[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+$ ]] || fail "repository must look like owner/name"
      origin="$(git remote get-url origin)"
      origin="${origin%.git}"
      shopt -s nocasematch
      [[ "$origin" == */"$expected_repo" || "$origin" == *:"$expected_repo" ]] \
        || fail "this checkout's origin is $origin, not $expected_repo. Run from a checkout of $expected_repo."
      shopt -u nocasematch
    fi
    meta="$(gh pr view "$number" --json number,baseRefOid,headRefOid)"
    base_sha="$(jq -r .baseRefOid <<<"$meta")"
    head_sha="$(jq -r .headRefOid <<<"$meta")"
    ;;
  local)
    base_ref="${2:-origin/main}"
    [[ "$base_ref" =~ ^[A-Za-z0-9][A-Za-z0-9._/-]*$ ]] || fail "base ref must match ^[A-Za-z0-9][A-Za-z0-9._/-]*$"
    number=""
    base_sha="$(git merge-base "$base_ref" HEAD)"
    head_sha="$(git rev-parse HEAD)"
    ;;
  *)
    fail "usage: prepare-context.sh pr <number> [<owner>/<repo>] | local [<base-ref>]"
    ;;
esac

[[ "$base_sha" =~ ^[0-9a-f]{40}$ ]] || fail "unexpected base sha: $base_sha"
[[ "$head_sha" =~ ^[0-9a-f]{40}$ ]] || fail "unexpected head sha: $head_sha"

git cat-file -e "$base_sha^{commit}" 2>/dev/null || git fetch -q origin "$base_sha" \
  || fail "base commit $base_sha is not in this checkout and could not be fetched"
if [[ "$mode" == pr ]]; then
  if ! git cat-file -e "$head_sha^{commit}" 2>/dev/null; then
    git fetch -q origin "pull/$number/head" 2>/dev/null || git fetch -q origin "$head_sha" 2>/dev/null || true
  fi
  # GitHub's PR diff is against the merge base, not the base branch tip, so base/ must be the same commit.
  base_sha="$(git merge-base "$base_sha" "$head_sha" 2>/dev/null)" \
    || fail "could not find the merge base of $base_sha and $head_sha"
fi

ctx="$(mktemp -d "${TMPDIR:-/tmp}/owning-team-review.XXXXXX")"

if [[ "$mode" == pr ]]; then
  gh pr diff "$number" >"$ctx/pr.diff"
  gh pr diff "$number" --name-only >"$ctx/files.txt"
else
  git diff "$base_sha" "$head_sha" >"$ctx/pr.diff"
  git diff --name-only "$base_sha" "$head_sha" >"$ctx/files.txt"
fi

# GitHub reads CODEOWNERS from .github/, the root, or docs/, in that order.
codeowners() {
  local sha="$1" out="$2" p
  for p in .github/CODEOWNERS CODEOWNERS docs/CODEOWNERS; do
    if git cat-file -e "$sha:$p" 2>/dev/null; then
      git show "$sha:$p" >"$out"
      return
    fi
  done
}
codeowners "$base_sha" "$ctx/CODEOWNERS.base"
if git cat-file -e "$head_sha^{commit}" 2>/dev/null; then
  codeowners "$head_sha" "$ctx/CODEOWNERS.head"
fi

mkdir "$ctx/base"
git archive "$base_sha" | tar -x -C "$ctx/base"

jq -n --arg mode "$mode" --arg number "$number" --arg base "$base_sha" --arg head "$head_sha" \
  '{mode: $mode, number: (if $number == "" then null else ($number | tonumber) end), base_sha: $base, head_sha: $head}' \
  >"$ctx/pr.json"

echo "$ctx"
