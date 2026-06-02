# creating-pull-request trigger evals

Reproducible trigger-rate test for the `bitwarden-delivery-tools:creating-pull-request` skill. Run before merging any change to the skill's `description` or `when_to_use` frontmatter to confirm the change doesn't degrade triggering on the natural-language phrasings the skill is designed to catch (or start firing on near-miss queries that belong to a sibling skill).

## Why a custom runner

The upstream `skill-creator` harness measures triggering by registering a temporary copy of the skill under a UUID-suffixed name and watching whether the model invokes that exact name. When the real plugin-registered skill is already installed in the test environment, the model invokes the real one and the harness records a false negative. `run_real_eval.py` instead watches `claude -p` stream events for any invocation of the real `creating-pull-request` skill, ignoring unrelated session-init or workflow skills that may fire first.

## Files

- `trigger-eval.json` — 20-query test set: 10 should-trigger natural-language phrasings ("package this up into a PR", "ship a draft", "get this in front of reviewers", etc.) and 10 should-not-trigger near-misses against sibling delivery skills (`committing-changes`, `labeling-changes`, `perform-preflight`) and against existing-PR management queries.
- `run_real_eval.py` — runner. Spawns parallel `claude -p` subprocesses, parses streamed tool-use events, computes per-query trigger rates.
- `baseline.json` — last known-good run. Diff against this to spot regressions on future description changes.

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

20 queries × 3 runs = 60 `claude -p` invocations. With 8 workers the run takes a few minutes.

## Regression check

```bash
diff <(jq -S . baseline.json) <(jq -S . result.json)
```

Empty diff means no regression. If a new failure appears, fix the skill description rather than the eval set — the eval set encodes intent, not implementation. If the change is intentional and the new run is the new desired behavior, replace `baseline.json` with `result.json` and commit alongside the description change.

## Updating the test surface

Update `trigger-eval.json` (not the runner) when the test surface needs to evolve: a new natural-language phrasing the skill should catch, a new sibling skill creating a new near-miss, or an existing query that turned out to be ambiguous. Keep should-trigger and should-not-trigger counts roughly balanced.
