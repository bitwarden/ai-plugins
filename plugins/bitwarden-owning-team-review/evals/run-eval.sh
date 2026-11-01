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

# A fixture is untrusted input, like a real pull request. dontAsk denies every call not allowed here.
# The deny list closes git options that write files or run commands under an allowed prefix.
allowed=(
  Read
  "Edit(/$repo/owning-team-review-*.json)"
  "Bash(gh pr view:*)" "Bash(gh pr diff:*)"
  "Bash(git grep:*)" "Bash(git show:*)"
)
denied=(
  "Bash(git * --output*)" "Bash(git *--output=*)"
  "Bash(git *--upl*)" "Bash(git *--open-files-in-pager*)" "Bash(git * -O*)"
)

harness_note="Tool permissions in this session are an allow-list, enforced per command. Allowed Bash commands: gh pr view, gh pr diff, git grep, and git show. Run each command on its own, not chained with && or ;."

[[ ! -e "$repo/.claude/settings.local.json" && ! -L "$repo/.claude/settings.local.json" ]] \
  || { echo "fixture carries .claude/settings.local.json; refusing to load it" >&2; exit 1; }

cd "$repo"
start=$(date +%s)
env -u CLAUDECODE \
  PATH="$EVALS_DIR/fixtures/gh-stub:$PATH" \
  GH_STUB_DATA="$run_dir/gh" \
  claude -p "TARGET: PR #$number" \
  --agent bitwarden-owning-team-review:owning-team-classifier \
  --plugin-dir "$PLUGIN_DIR" \
  --model "$model" \
  --setting-sources local \
  --permission-mode dontAsk \
  --allowedTools "${allowed[@]}" \
  --disallowedTools "${denied[@]}" \
  --append-system-prompt "$harness_note" \
  --no-session-persistence \
  --output-format stream-json --verbose \
  >"$run_dir/run.jsonl" 2>"$run_dir/stderr.log" || echo "claude exited $? for $id/run-$run" >&2
echo $(( $(date +%s) - start )) >"$run_dir/seconds"

result="$repo/owning-team-review-$number.json"
if [[ -f "$result" ]]; then cp "$result" "$run_dir/result.json"; fi
