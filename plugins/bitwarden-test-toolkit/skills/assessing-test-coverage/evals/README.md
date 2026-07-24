# assessing-test-coverage trigger evals

Reproducible trigger-rate test for the `bitwarden-test-toolkit:assessing-test-coverage` skill. Run before merging any change to the skill's `description` frontmatter to confirm the change doesn't degrade triggering on the natural-language phrasings the skill is designed to catch (or start firing on near-miss queries that want a different kind of test work).

## Why a custom runner

The upstream `skill-creator` harness measures triggering by registering a temporary copy of the skill under a UUID-suffixed name and watching whether the model invokes that exact name. When the real plugin-registered skill is already installed in the test environment, the model invokes the real one and the harness records a false negative. `run_real_eval.py` instead watches `claude -p` stream events for any invocation of the real `assessing-test-coverage` skill, ignoring unrelated session-init or workflow skills that may fire first.

## Files

- `trigger-eval.json` — 20-query test set: 10 should-trigger phrasings asking for an inventory of coverage that _already exists_ for a change ("what's already tested for this PR", "which behaviors have no test today", "audit the current coverage for…") and 10 should-not-trigger near-misses that share the words "test"/"coverage" but want something the skill deliberately does not do — writing new tests, recommending a test strategy or layer, generating a test plan, running or fixing existing tests, reading an overall coverage percentage, or a general PR review.
- `run_real_eval.py` — runner. Spawns parallel `claude -p` subprocesses, parses streamed tool-use events, computes per-query trigger rates. Each subprocess is killed as soon as the model requests a real-work tool (Bash/Task) without first invoking the target skill, so the adversarial should-not-trigger queries never actually clone repos or run build/test toolchains — see the memory note under "Running".
- `baseline.json` — last known-good run. Diff against this to spot regressions on future description changes. Recorded 2026-07-24 with `--model claude-sonnet-4-6` at `--runs-per-query 7`.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`. The plugin must be installed and enabled (`claude plugin install bitwarden-test-toolkit@bitwarden-marketplace`), or every query records a false non-trigger. The eval reads the installed copy, not this working tree, so **reinstall after editing the skill** (uninstall + install) before running.

```bash
python3 run_real_eval.py \
  --eval-set trigger-eval.json \
  --runs-per-query 7 \
  --num-workers 8 \
  --timeout 90 \
  --model claude-sonnet-4-6 \
  > result.json
```

20 queries × 7 runs = 140 `claude -p` invocations. With 8 workers the run takes several minutes.

Each `claude -p` subprocess is a full agent, so keep `--num-workers` modest: the 10 should-not-trigger queries are adversarial real-work prompts, and the runner already bails the instant such a query reaches for a real-work tool (Bash/Task) — but N full agents still run concurrently. Raising `--num-workers` much past the default, or removing the early-exit, will spawn enough parallel clone/build work to exhaust memory on a typical machine.

## Regression check

```bash
diff <(jq -S . baseline.json) <(jq -S . result.json)
```

Empty diff means no regression. If a new failure appears, fix the skill description rather than the eval set — the eval set encodes intent, not implementation. If the change is intentional and the new run is the new desired behavior, replace `baseline.json` with `result.json` and commit alongside the description change.

## Updating the test surface

Update `trigger-eval.json` (not the runner) when the test surface needs to evolve: a new natural-language phrasing the skill should catch, a new sibling skill (e.g. a forward-looking test-recommendation skill) creating a new near-miss, or an existing query that turned out to be ambiguous. Keep should-trigger and should-not-trigger counts roughly balanced.
