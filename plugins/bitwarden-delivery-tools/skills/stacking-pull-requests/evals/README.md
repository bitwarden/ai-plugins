# stacking-pull-requests trigger evals

Reproducible trigger-rate test for the `bitwarden-delivery-tools:stacking-pull-requests` skill. Run before merging any change to the skill's `description` to confirm it keeps firing on stack phrasings without stealing queries that belong to `creating-pull-request` or `force-multiplier`.

## Why a custom runner

The upstream `skill-creator` harness measures triggering by registering a temporary copy of the skill under a UUID-suffixed name and watching whether the model invokes that exact name. When the real plugin-registered skill is already installed in the test environment, the model invokes the real one and the harness records a false negative. `run_real_eval.py` instead watches `claude -p` stream events for any invocation of the real `stacking-pull-requests` skill, ignoring unrelated session-init or workflow skills that may fire first.

## Files

- `trigger-eval.json` — 20-query test set: 10 should-trigger phrasings covering layer planning, submission, lower-layer feedback, and merging the chain, and 10 should-not-trigger near-misses routed at `creating-pull-request` (single-branch PR work), `force-multiplier` (one change across many repos), `committing-changes`, `perform-preflight`, and plain git questions.
- `run_real_eval.py` — runner. Spawns parallel `claude -p` subprocesses, parses streamed tool-use events, computes per-query trigger rates. A copy of `../../filing-breakdown-tasks/evals/run_real_eval.py` with `TARGET_SKILL_TOKEN` set to this skill.
- `baseline.json` — **not yet recorded.** The skill ships in the same change as this eval, so there is no prior run to diff against. The runner takes `--plugin-dir`, so a baseline can be recorded from the working tree rather than waiting for the release; commit it alongside.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`. The runner sets no permission mode, so the imperative queries execute for real — run it against a clean checkout, never a dirty working tree.

```bash
python3 run_real_eval.py \
  --eval-set trigger-eval.json \
  --plugin-dir ../../.. \
  --runs-per-query 3 \
  --num-workers 8 \
  --timeout 120 \
  --model claude-opus-5 \
  > result.json
```

Pass `--plugin-dir` pointing at `bitwarden-delivery-tools` in the working tree. Without it the subprocesses load the installed plugin cache, which will not contain `stacking-pull-requests` until this change ships: every should-trigger query scores zero and every near-miss passes trivially against a skill that was never loaded. The same directory supplies `creating-pull-request` and `force-multiplier`, which the near-misses are written against.

20 queries × 3 runs = 60 `claude -p` invocations. With 8 workers the run takes a few minutes. The 120-second timeout is sized by the should-not-trigger cases: a trigger ends as soon as the token appears, but a non-trigger has to reach the terminal `result` event.

## Regression check

```bash
diff <(jq -S . baseline.json) <(jq -S . result.json)
```

Empty diff means no regression. If a new failure appears, fix the skill description rather than the eval set — the eval set encodes intent, not implementation. If the change is intentional and the new run is the new desired behavior, replace `baseline.json` with `result.json` and commit alongside the description change.

## Updating the test surface

Update `trigger-eval.json` (not the runner) when the test surface needs to evolve: a new phrasing the skill should catch, a new sibling skill creating a new near-miss, or an existing query that turned out to be ambiguous. Keep should-trigger and should-not-trigger counts roughly balanced.
