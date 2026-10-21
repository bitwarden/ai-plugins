#!/usr/bin/env bash
# Combines every result.json under OUT_DIR into one benchmark document on stdout.
# Usage: aggregate-catch-rate.sh <model> <grader-model> > catch-rate-baseline.json
# Env:   OUT_DIR  same scratch directory run-catch-rate.sh and score-catch-rate.sh used
set -euo pipefail

: "${OUT_DIR:?set OUT_DIR}"

find "$OUT_DIR" -name result.json -print0 | xargs -0 cat | jq -s \
  --arg model "$1" --arg grader "$2" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
  def ratio(a; b): (b // 0) as $b | if $b == 0 then null else (((a // 0) / $b * 1000) | round / 1000) end;
  # An errored run measured nothing, so it is left out of every rate rather than scored as a miss.
  def summary:
    ([.[] | select(.error)] | length) as $errored
    | [.[] | select(.error | not)]
    | group_by(.run_number) as $by_run
    | {
        runs: length,
        catch_rate_per_run: [$by_run[] | {run_number: .[0].run_number, catch_rate: ratio([.[] | select(.hit)] | length; length)}],
        mean_catch_rate: ratio([.[] | select(.hit)] | length; length),
        false_finding_rate: ratio([.[].false_findings] | add; [.[].validated_findings] | add),
        validated_findings: ([.[].validated_findings] | add),
        false_findings: ([.[].false_findings] | add),
        errored_runs: $errored
      };
  sort_by(.eval_id, .configuration, .run_number) as $runs
  | {
      metadata: {
        skill_name: "performing-multi-agent-code-review",
        eval_type: "catch-rate",
        executor_model: $model,
        grader_model: $grader,
        timestamp: $ts,
        evals_run: [$runs[].eval_id] | unique,
        runs_per_configuration: ([$runs[].run_number] | max)
      },
      run_summary: ($runs | group_by(.configuration) | map({key: .[0].configuration, value: summary}) | from_entries),
      runs: $runs
    }'
