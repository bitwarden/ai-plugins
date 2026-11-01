#!/usr/bin/env bash
# Runs one classification-eval case once.
# Usage: run-eval.sh <eval-id> <run-number>
# Env:   OUT_DIR     scratch directory for fixtures, transcripts, and results
#        EVAL_SET    optional eval set file name in this directory, defaults to classification-eval.json
#        CLONES_DIR  directory holding a local clone of each repository, for real-PR cases
#        MODEL       optional, defaults to opus
set -euo pipefail

EVALS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$EVALS_DIR/.." && pwd)"
EVAL_SET="$EVALS_DIR/${EVAL_SET:-classification-eval.json}"
[[ "$(basename "$EVAL_SET")" =~ ^[a-z-]+\.json$ && -f "$EVAL_SET" ]] || { echo "unknown eval set: $EVAL_SET" >&2; exit 1; }

id="$1"
run="$2"
: "${OUT_DIR:?set OUT_DIR}"
[[ "$OUT_DIR" == /* ]] || { echo "OUT_DIR must be an absolute path" >&2; exit 1; }
[[ "$id" =~ ^[0-9]+$ ]] || { echo "eval id must be numeric" >&2; exit 1; }
[[ "$run" =~ ^[0-9]+$ ]] || { echo "run number must be numeric" >&2; exit 1; }
model="${MODEL:-opus}"

case_json="$(jq -ce --argjson id "$id" '.evals[] | select(.id == $id)' "$EVAL_SET")"
run_dir="$OUT_DIR/$id/run-$run"
[[ ! -e "$run_dir" ]] || { echo "$run_dir already exists" >&2; exit 1; }

if [[ "$(jq -r 'has("merge_sha")' <<<"$case_json")" == true ]]; then
  "$EVALS_DIR/fixtures/setup-real.sh" "$(jq -r .repo <<<"$case_json")" "$(jq -r .pr <<<"$case_json")" \
    "$(jq -r .merge_sha <<<"$case_json")" "$run_dir"
elif [[ "$(jq -r 'has("head_sha")' <<<"$case_json")" == true ]]; then
  "$EVALS_DIR/fixtures/setup-real.sh" "$(jq -r .repo <<<"$case_json")" "$(jq -r .pr <<<"$case_json")" \
    "$(jq -r .head_sha <<<"$case_json")" "$run_dir" "$(jq -r .base_sha <<<"$case_json")"
else
  fixture="$(jq -r .fixture <<<"$case_json")"
  [[ "$fixture" =~ ^[a-z0-9-]+$ ]] || { echo "unexpected fixture name: $fixture" >&2; exit 1; }
  "$EVALS_DIR/fixtures/setup.sh" "$fixture" "$run_dir"
fi
repo="$run_dir/repo"
number="$(jq -r .number "$run_dir/gh/pr.json")"

# Build the classifier's read-only context the way every real caller does. The gh stub serves the
# fixture's canned pull request, so nothing reaches GitHub.
cd "$repo"
ctx="$(env PATH="$EVALS_DIR/fixtures/gh-stub:$PATH" GH_STUB_DATA="$run_dir/gh" \
  bash "$PLUGIN_DIR/scripts/prepare-context.sh" pr "$number" 2>"$run_dir/context.log")" \
  || { echo "prepare-context failed for $id/run-$run" >&2; ctx=""; }
echo "$ctx" >"$run_dir/context"

# A fixture is untrusted input, like a real pull request. dontAsk denies every call not allowed here.
# The agent has no shell; reads are limited to the context and the plugin's own files.
allowed=(
  "Read(/$ctx/**)" "Read(/$PLUGIN_DIR/**)"
  Grep Glob
)

[[ ! -e "$repo/.claude/settings.local.json" && ! -L "$repo/.claude/settings.local.json" ]] \
  || { echo "fixture carries .claude/settings.local.json; refusing to load it" >&2; exit 1; }

start=$(date +%s)
if [[ -n "$ctx" ]]; then
  env -u CLAUDECODE \
    claude -p "CONTEXT: $ctx" \
    --agent bitwarden-owning-team-review:owning-team-classifier \
    --plugin-dir "$PLUGIN_DIR" \
    --model "$model" \
    --setting-sources local \
    --permission-mode dontAsk \
    --allowedTools "${allowed[@]}" \
    --no-session-persistence \
    --output-format stream-json --verbose \
    >"$run_dir/run.jsonl" 2>"$run_dir/stderr.log" || echo "claude exited $? for $id/run-$run" >&2
fi
echo $(( $(date +%s) - start )) >"$run_dir/seconds"

# The agent prints its result as its final message. Parse it the way a real caller does.
if [[ -f "$run_dir/run.jsonl" ]]; then
  jq -rs '[.[] | select(.type == "result") | .result] | last // empty' "$run_dir/run.jsonl" >"$run_dir/result.raw"
  "$EVALS_DIR/extract-result.sh" <"$run_dir/result.raw" >"$run_dir/result.json" 2>/dev/null || rm -f "$run_dir/result.json"
fi
