#!/usr/bin/env bash
# Renders the classifier's result as the PR comment. The workflow posts the output.
# A missing or unparseable result renders as no verdict, so the comment fails shut like the gate.
# Usage: render-comment.sh <result.json> <teams.json> <owner/repo> <pr-number> <head-sha> <run-url>
#   result.json may be missing. teams.json holds the workflow's team check and may also be missing.
set -euo pipefail

fail() { echo "render-comment: $*" >&2; exit 1; }

[[ $# -eq 6 ]] || fail "usage: render-comment.sh <result.json> <teams.json> <owner/repo> <pr-number> <head-sha> <run-url>"
result="$1" teams="$2" repo="$3" pr="$4" head="$5" run_url="$6"
[[ "$repo" =~ ^[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+$ ]] || fail "repository must look like owner/name"
[[ "$pr" =~ ^[0-9]+$ ]] || fail "pr number must match ^[0-9]+$"
[[ "$head" =~ ^[0-9a-f]{40}$ ]] || fail "head sha must be 40 hex characters"
[[ "$run_url" =~ ^https://[A-Za-z0-9./_-]+$ ]] || fail "run url must be an https URL"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
version="$(jq -r .version "$script_dir/../.claude-plugin/plugin.json")"

teams_json='{"token": "unavailable", "checks": []}'
if [[ -s "$teams" ]] && jq -e 'type == "object" and (.checks | type == "array")' "$teams" >/dev/null 2>&1; then
  teams_json="$(cat "$teams")"
fi

input=null
if [[ -s "$result" ]] && jq -e 'type == "object"' "$result" >/dev/null 2>&1; then
  input="$(cat "$result")"
fi

jq -r --argjson teams "$teams_json" --arg repo "$repo" --arg pr "$pr" --arg head "$head" \
  --arg version "$version" --arg run_url "$run_url" -f "$script_dir/render-comment.jq" <<<"$input"
