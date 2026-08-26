# filing-breakdown-tasks trigger evals

Reproducible trigger-rate test for the `bitwarden-delivery-tools:filing-breakdown-tasks` skill. Run before merging any change to the skill's `description` or `when_to_use` frontmatter to confirm the change doesn't degrade triggering on the `tasks.md` phrasings the skill is designed to catch (or start firing on near-miss queries that belong to a sibling skill).

## Why a custom runner

The upstream `skill-creator` harness measures triggering by registering a temporary copy of the skill under a UUID-suffixed name and watching whether the model invokes that exact name. When the real plugin-registered skill is already installed in the test environment, the model invokes the real one and the harness records a false negative. `run_real_eval.py` instead watches `claude -p` stream events for any invocation of the real `filing-breakdown-tasks` skill, ignoring unrelated session-init or workflow skills that may fire first.

## Files

- `trigger-eval.json` — 20-query test set: 10 should-trigger `tasks.md` phrasings ("create the tickets from tasks.md", "turn this breakdown into Jira tickets", etc.) and 10 should-not-trigger near-misses against sibling skills (`researching-jira-issues`, `filing-jira-tickets`, the upstream decomposition step) and against existing-ticket edits, Jira search, and breakdown-file moves. Ticket keys are masked (`PM-XXXX`) so a live session can't resolve them against real Jira.
- `run_real_eval.py` — runner. Spawns parallel `claude -p` subprocesses, parses streamed tool-use events, computes per-query trigger rates. A copy of `../../creating-pull-request/evals/run_real_eval.py` with `TARGET_SKILL_TOKEN` set to this skill, plus a repeatable `--plugin-dir` passthrough and run conditions recorded in the output.
- `baseline.json` — last known-good run. Diff against this to spot regressions on future description changes. Records the `model`, `plugin_dirs`, and `runs_per_query` that produced it; a run under different conditions will fail the diff.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`. The runner sets no permission mode, so the imperative queries execute for real — run it against a clean checkout, never a dirty working tree.

```bash
python3 run_real_eval.py \
  --eval-set trigger-eval.json \
  --plugin-dir ../../.. \
  --plugin-dir ../../../../bitwarden-atlassian-tools \
  --runs-per-query 3 \
  --num-workers 8 \
  --timeout 60 \
  --model claude-opus-5 \
  > result.json
```

`--plugin-dir` points the subprocesses at a plugin directory and is repeatable. Pass **every** plugin whose skills compete for these queries, from the working tree rather than the installed cache:

- `bitwarden-delivery-tools` — supplies `filing-breakdown-tasks` itself. Without it the skill isn't in the session at all and every should-trigger query scores zero.
- `bitwarden-atlassian-tools` — supplies `filing-jira-tickets` and `researching-jira-issues`, which the should-not-trigger near-misses are written against. Omit it and those queries pass against a skill that was never loaded.

20 queries × 3 runs = 60 `claude -p` invocations. With 8 workers the run takes a few minutes.

## Regression check

```bash
diff <(jq -S . baseline.json) <(jq -S . result.json)
```

Empty diff means no regression. If a new failure appears, fix the skill description rather than the eval set — the eval set encodes intent, not implementation. If the change is intentional and the new run is the new desired behavior, replace `baseline.json` with `result.json` and commit alongside the description change.

## Updating the test surface

Update `trigger-eval.json` (not the runner) when the test surface needs to evolve: a new phrasing the skill should catch, a new sibling skill creating a new near-miss, or an existing query that turned out to be ambiguous. Keep should-trigger and should-not-trigger counts roughly balanced.
