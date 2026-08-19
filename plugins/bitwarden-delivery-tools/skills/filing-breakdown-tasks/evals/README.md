# filing-breakdown-tasks trigger evals

Reproducible trigger-rate test for the `bitwarden-delivery-tools:filing-breakdown-tasks` skill. Run before merging any change to the skill's `description` or `when_to_use` frontmatter to confirm the change doesn't degrade triggering on the `tasks.md` phrasings the skill is meant to catch (or start firing on near-miss queries that belong to a sibling skill).

## Why a custom runner

The upstream `skill-creator` harness measures triggering by registering a temporary copy of the skill under a UUID-suffixed name and watching whether the model invokes that exact name. When the real plugin-registered skill is already installed in the test environment, the model invokes the real one and the harness records a false negative. `run_real_eval.py` instead watches `claude -p` stream events for any invocation of the real `filing-breakdown-tasks` skill, ignoring unrelated session-init or workflow skills that may fire first.

## Files

- `trigger-eval.json` — 18-query test set: 10 should-trigger `tasks.md` phrasings ("create the tickets from tasks.md", "turn this breakdown into Jira tickets", etc.) and 8 should-not-trigger near-misses against sibling skills (`researching-jira-issues`, `decomposing-into-tasks`), against editing an existing ticket, a generic Jira search, and a breakdown-file-move. Ticket keys are masked (`PM-XXXX`) so a live session can't resolve them against real Jira.
- `run_real_eval.py` — runner. Spawns parallel `claude -p` subprocesses, parses streamed tool-use events, computes per-query trigger rates. A local copy of `../creating-pull-request/evals/run_real_eval.py` with `TARGET_SKILL_TOKEN` set to this skill, plus two additions (see below).

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`.

```bash
python3 run_real_eval.py \
  --eval-set trigger-eval.json \
  --plugin-dir ../../.. \
  --runs-per-query 3 \
  --num-workers 8 \
  --timeout 60 \
  --model claude-opus-5 \
  > result.json
```

18 queries × 3 runs = 54 `claude -p` invocations. With 8 workers the run takes a few minutes. Pass a current `--model` — the script's default is stale.

Two additions over the sibling runner:

- `--permission-mode plan` is baked into the subprocess command so the eval's `claude -p` sessions cannot mutate the repo. Without it, an imperative should-not-trigger query (e.g. "move the finished breakdown into its team's complete folder") can execute against the working tree.
- `--plugin-dir <path>` loads a plugin straight from a directory. Before the skill is released, pass `--plugin-dir ../../..` (the `bitwarden-delivery-tools` plugin root) so the sessions load this working-tree version instead of the installed plugin.

## Regression check

```bash
diff <(jq -S . baseline.json) <(jq -S . result.json)
```

Empty diff means no regression. If a new failure appears, fix the skill description rather than the eval set — the eval set encodes intent, not implementation. If the change is intentional and the new run is the desired behavior, replace `baseline.json` with `result.json` and commit alongside the description change.

## Updating the test surface

Update `trigger-eval.json` (not the runner) when the test surface needs to evolve: a new phrasing the skill should catch, a new sibling skill creating a new near-miss, or an existing query that turned out to be ambiguous. Keep should-trigger and should-not-trigger counts roughly balanced.
