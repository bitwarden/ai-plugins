#!/usr/bin/env bash
# Scores one classification-eval run. Writes <run-dir>/score.json.
# Usage: score.sh <eval-id> <run-number>
# Env:   OUT_DIR   the directory run-eval.sh wrote to
#        EVAL_SET  optional eval set file name in this directory, defaults to classification-eval.json
set -euo pipefail

EVALS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVAL_SET="$EVALS_DIR/${EVAL_SET:-classification-eval.json}"
[[ "$(basename "$EVAL_SET")" =~ ^[a-z-]+\.json$ && -f "$EVAL_SET" ]] || { echo "unknown eval set: $EVAL_SET" >&2; exit 1; }

id="$1"
run="$2"
: "${OUT_DIR:?set OUT_DIR}"
[[ "$id" =~ ^[0-9]+$ ]] || { echo "eval id must be numeric" >&2; exit 1; }
[[ "$run" =~ ^[0-9]+$ ]] || { echo "run number must be numeric" >&2; exit 1; }

run_dir="$OUT_DIR/$id/run-$run"
case_json="$(jq -ce --argjson id "$id" '.evals[] | select(.id == $id)' "$EVAL_SET")"

# Files a no_file check names must not exist anywhere in the run directory.
missing='[]'
while IFS= read -r path; do
  [[ -n "$path" ]] || continue
  if [[ -n "$(find "$run_dir" -name "$path" -print -quit)" ]]; then
    missing="$(jq -c --arg p "$path" '. + [$p]' <<<"$missing")"
  fi
done < <(jq -r '(.checks // [])[] | select(.kind == "no_file") | .path' <<<"$case_json")

calls='[]'
[[ -f "$run_dir/gh/calls.log" ]] && calls="$(jq -Rsc 'split("\n") | map(select(. != ""))' "$run_dir/gh/calls.log")"
facts="$(jq -nc --argjson m "$missing" --argjson c "$calls" '{missing_files: $m, calls: $c}')"

# A run that ended in an API error is not scored, so a crash never reads as a miss.
if grep -q '"is_error":true' "$run_dir/run.jsonl" 2>/dev/null && [[ ! -f "$run_dir/result.json" ]]; then
  jq -n --argjson id "$id" --argjson run "$run" '{id: $id, run: $run, error: "run ended in an error"}' >"$run_dir/score.json"
  exit 0
fi

if [[ -f "$run_dir/result.json" ]] && jq -e . "$run_dir/result.json" >/dev/null 2>&1; then
  result="$(cat "$run_dir/result.json")"
else
  result=null
fi

cost="$(jq -s '[.[] | select(.type == "result") | .total_cost_usd] | add // null' "$run_dir/run.jsonl" 2>/dev/null || echo null)"

jq --argjson case "$case_json" --argjson facts "$facts" -f "$EVALS_DIR/score.jq" <<<"$result" \
  | jq --argjson id "$id" --argjson run "$run" --argjson cost "$cost" \
       --arg covers "$(jq -r .covers <<<"$case_json")" \
       '{id: $id, run: $run, covers: $covers, cost_usd: $cost} + .' >"$run_dir/score.json"
