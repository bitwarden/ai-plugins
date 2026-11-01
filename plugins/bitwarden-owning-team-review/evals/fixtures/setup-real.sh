#!/usr/bin/env bash
# Builds one real-PR eval fixture from a squash-merged pull request, or from an open one.
# The fixture replays the pull request on a base that carries draft INTENT.md files, because the real
# repository has none yet:
#   base' = the pull request's base commit + the intent overlay
#   head' = base' + the pull request's diff
# Usage: setup-real.sh <repo> <pr-number> <head-sha> <empty-target-dir> [<base-sha>]
#   Without <base-sha>, <head-sha> must be a squash-merge commit, and its parent is the base.
#   With <base-sha>, the fixture replays <base-sha>..<head-sha>, as for an open pull request.
# Env:   CLONES_DIR  directory holding a local clone of each repository, named by repository
# Output matches setup.sh: <dir>/repo checked out at base', and <dir>/gh/pr.json, pr.diff, pr.files.
set -euo pipefail

FIXTURES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$1"
number="$2"
head_sha="$3"
dir="$4"
base_sha="${5:-}"
: "${CLONES_DIR:?set CLONES_DIR}"
[[ "$repo" =~ ^bitwarden/[A-Za-z0-9._-]+$ ]] || { echo "unexpected repo: $repo" >&2; exit 1; }
[[ "$number" =~ ^[0-9]+$ ]] || { echo "pr number must be numeric" >&2; exit 1; }
[[ "$head_sha" =~ ^[0-9a-f]{40}$ ]] || { echo "unexpected head sha: $head_sha" >&2; exit 1; }
[[ -z "$base_sha" || "$base_sha" =~ ^[0-9a-f]{40}$ ]] || { echo "unexpected base sha: $base_sha" >&2; exit 1; }
[[ "$dir" == /* ]] || { echo "target dir must be an absolute path" >&2; exit 1; }

name="${repo#bitwarden/}"
clone="$CLONES_DIR/$name"
intent="$FIXTURES_DIR/intent/$name"
[[ -d "$intent" ]] || { echo "no intent overlay for $name" >&2; exit 1; }
git -C "$clone" cat-file -e "$head_sha^{commit}" 2>/dev/null || git -C "$clone" fetch -q origin "pull/$number/head" \
  || git -C "$clone" fetch -q origin "$head_sha"
if [[ -z "$base_sha" ]]; then
  [[ "$(git -C "$clone" log -1 --format=%P "$head_sha" | wc -w)" -eq 1 ]] || { echo "$head_sha is not a squash merge" >&2; exit 1; }
  base_sha="$(git -C "$clone" rev-parse "$head_sha^")"
fi
git -C "$clone" cat-file -e "$base_sha^{commit}" 2>/dev/null || git -C "$clone" fetch -q origin "$base_sha"

mkdir -p "$dir/gh"
git clone -q --shared --no-checkout "$clone" "$dir/repo"
cd "$dir/repo"
git config user.email eval@example.com
git config user.name eval
git config commit.gpgsign false
git checkout -q --detach "$base_sha"
# Branches and tags from the source clone reach later history; drop them.
git for-each-ref --format='delete %(refname)' | git update-ref --no-deref --stdin

# Overlay: each intent file becomes INTENT.md in every directory it covers that exists at this base.
overlay() {
  local file="$1"
  shift
  local d
  for d in "$@"; do
    [[ -d "$d" ]] || continue
    cp "$intent/$file.md" "$d/INTENT.md"
  done
}

case "$name" in
  clients)
    overlay platform \
      libs/common/src/platform libs/platform libs/state libs/state-internal libs/messaging libs/storage-core \
      libs/logging libs/scheduling libs/serialization libs/client-type libs/angular/src/platform \
      apps/browser/src/platform apps/desktop/src/platform apps/cli/src/platform libs/common/src/state-migrations
    ;;
  *)
    echo "no overlay mapping for $name" >&2
    exit 1
    ;;
esac

git add -A
git commit -qm "eval: intent overlay"
BASE_SHA="$(git rev-parse HEAD)"

git diff --binary "$base_sha" "$head_sha" | git apply --index
git commit -qm "eval: replay #$number"
HEAD_SHA="$(git rev-parse HEAD)"

git diff "$BASE_SHA" "$HEAD_SHA" >"$dir/gh/pr.diff"
git diff --name-only "$BASE_SHA" "$HEAD_SHA" >"$dir/gh/pr.files"
jq -n \
  --argjson number "$number" \
  --arg repo "$repo" \
  --arg base "$BASE_SHA" \
  --arg head "$HEAD_SHA" \
  '{number: $number, url: ("https://github.com/" + $repo + "/pull/" + ($number | tostring)),
    baseRefOid: $base, headRefOid: $head, baseRefName: "main", headRefName: "eval/replay",
    state: "MERGED", isCrossRepository: false, author: {login: "outside-author"},
    title: "eval replay", body: ""}' >"$dir/gh/pr.json"

git checkout -q --detach "$BASE_SHA"
