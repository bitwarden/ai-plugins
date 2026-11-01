#!/usr/bin/env bash
# Aggregates every score.json under OUT_DIR into one summary on stdout.
# Usage: aggregate.sh
# Env:   OUT_DIR  the directory run-eval.sh and score.sh wrote to
set -euo pipefail
: "${OUT_DIR:?set OUT_DIR}"

find "$OUT_DIR" -name score.json -print0 | xargs -0 cat | jq -s '
  (map(select(.error == null))) as $ok
  | {
      runs: length,
      errored_runs: (map(select(.error != null)) | length),
      pass_rate: (if ($ok | length) > 0 then ($ok | map(select(.passed)) | length) / ($ok | length) else null end),
      result_accuracy: (if ($ok | length) > 0 then ($ok | map(select(.result_correct)) | length) / ($ok | length) else null end),
      kind_accuracy: (if ($ok | length) > 0 then ($ok | map(select(.kind_correct)) | length) / ($ok | length) else null end),
      false_negatives: ($ok | map(select(.false_negative)) | length),
      false_positives: ($ok | map(select(.false_positive)) | length),
      cost_usd: ($ok | map(.cost_usd // 0) | add),
      cases: ($ok | group_by(.id) | map({
        id: .[0].id,
        covers: .[0].covers,
        passed: "\(map(select(.passed)) | length) / \(length)",
        failures: (map(.failures) | add | unique)
      }))
    }'
