# committing-changes evals

Reproducible trigger-rate test for the `bitwarden-delivery-tools:committing-changes` skill. Run before merging any change to the skill's `description` or frontmatter.

## Files

- `trigger-eval.json` — 13-query test set: 8 should-trigger phrasings and 5 should-not-trigger near-misses against sibling skills (`creating-pull-request`, `labeling-changes`, `perform-preflight`), the cross-plugin `addressing-code-review-comments` skill, and bare branch-management queries.
- `run_real_eval.py` — runner. Spawns parallel `claude -p` subprocesses, parses streamed tool-use events, computes per-query trigger rates. See `creating-pull-request/evals/run_real_eval.py` for why this hand-rolled runner exists instead of the skill-creator harness.
- `baseline.json` — last known-good run. Diff against this to spot regressions.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`.

```bash
python3 run_real_eval.py \
  --eval-set trigger-eval.json \
  --runs-per-query 3 \
  --num-workers 8 \
  --timeout 60 \
  --model claude-opus-4-7 \
  > result.json
```

## Regression check

```bash
diff <(jq -S . baseline.json) <(jq -S . result.json)
```

Empty diff means no regression. If a new failure appears, fix the skill description rather than the eval set. If the change is intentional, replace `baseline.json` with `result.json` and commit alongside the description change.
