# assessing-test-coverage trigger evals

Reproducible trigger-rate test for the `bitwarden-testing-tools:assessing-test-coverage` skill. Run before merging any change to the skill's `description` frontmatter to confirm the change doesn't degrade triggering on the natural-language phrasings the skill is designed to catch (or start firing on near-miss queries that want a different kind of test work).

## Why a custom runner

The upstream `skill-creator` harness measures triggering by registering a temporary copy of the skill under a UUID-suffixed name and watching whether the model invokes that exact name. When the real plugin-registered skill is already installed in the test environment, the model invokes the real one and the harness records a false negative. `run_real_eval.py` instead watches `claude -p` stream events for any invocation of the real `assessing-test-coverage` skill, ignoring unrelated session-init or workflow skills that may fire first.

## Files

- `trigger-eval.json` — 20-query test set: 10 should-trigger phrasings asking for an inventory of coverage that _already exists_ for a change, spanning all four documented input types (a PR, a Jira key, a Tech Breakdown doc, and a Testmo CSV) plus branch/component/screen surfaces ("what's already tested for this PR", "which behaviors have no test today", "cross-reference this Testmo CSV against automated coverage", "inventory coverage for the surfaces in this Tech Breakdown"), and 10 should-not-trigger near-misses that share the words "test"/"coverage" but want something the skill deliberately does not do — writing new tests, recommending a test strategy or layer, generating a test plan, running or fixing existing tests, reading an overall coverage percentage, or a general PR review.
- `run_real_eval.py` — thin config wrapper over the plugin's shared runner. The runner itself (spawning parallel `claude -p` subprocesses, parsing streamed tool-use events, computing per-query trigger rates, and killing each subprocess as soon as the model requests `Task`, or a `Bash` command outside the read-only `gh`/`git` allowlist, without first invoking the target skill) now lives in `../../../scripts/eval_harness.py`, shared across the plugin's skills. See the memory note under "Running".
- `baseline.json` — last known-good run. Diff against this to spot regressions on future description changes.

## Baseline provenance

A trigger eval measures whether the model auto-selects a skill from a natural-language query, and that outcome depends on which sibling skills are installed alongside it, since the model is choosing among all of them. The `baseline.json` committed here was recorded on 2026-08-01 against the plugin's final ten-skill inventory:

- `assessing-test-coverage`
- `writing-playwright-test-cases`
- `compiling-playwright-report`
- `mapping-services-under-test`
- `running-playwright-tests`
- `scoping-playwright-test-cases`
- `reading-mailcatcher-api`
- `start-playwright-test`
- `using-stripe-cli`
- `checking-localhost-web-health`

An earlier baseline for this skill was recorded on 2026-07-29 against a plugin containing only `assessing-test-coverage` itself, and read `should_trigger_pass=10/10`, `should_not_trigger_pass=10/10`. That baseline is stale now that the inventory is final: `should_not_trigger_pass` moved to **7/10** in this run. This is not a regression. Three should-not-trigger queries began firing once the nine sibling testing skills were installed, because the model now has real work-adjacent skills to reach for on queries that ask about testing strategy or scope rather than existing coverage, and it sometimes reaches for one of them instead of correctly declining to trigger anything:

- `"what's the right testing strategy for the billing webhook handler..."`, rate 6/7 (0.857)
- `"should I add integration tests for the SsoController change, or are unit tests enough"`, rate 7/7 (1.0)
- `"explain how the testing pyramid works and which layers bitwarden uses"`, rate 4/7 (0.571)

The unmodified original runner reproduced this independently; nothing in the skill's `description` or the eval set changed to cause it. Two queries also landed in the 0.35-0.65 flaky band and are flagged here as rewording candidates rather than re-run:

- `"what's the overall code-coverage percentage on bitwarden/server right now"`, rate 3/7 (0.429), still a pass (rate below 0.5) but close to the threshold.
- `"explain how the testing pyramid works and which layers bitwarden uses"`, rate 4/7 (0.571), the same query listed above as a new failure; it sits inside the flaky band on top of having flipped verdict.

This committed baseline was recorded before `Agent` was added to `scripts/eval_harness.py`'s `exec_tools` bail-out set (the installed CLI emits `Agent`, with `Task` kept only as a legacy alias), so a run that dispatched a subagent before reaching for the target skill was not being caught as real work at the time these numbers were measured; it should be re-recorded before being relied on as a regression control.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`. The plugin must be installed and enabled (`claude plugin install bitwarden-testing-tools@bitwarden-marketplace`), or every query records a false non-trigger. The eval reads the installed copy, not this working tree, so **reinstall after editing the skill** (uninstall + install) before running.

```bash
python3 run_real_eval.py \
  --eval-set trigger-eval.json \
  --runs-per-query 7 \
  --num-workers 5 \
  --timeout 90 \
  --model claude-opus-4-8 \
  > result.json
```

20 queries × 7 runs = 140 `claude -p` invocations. With 5 workers the run takes several minutes.

Each `claude -p` subprocess is a full agent, so keep `--num-workers` modest: the 10 should-not-trigger queries are adversarial real-work prompts, and the runner already bails the instant such a query reaches for `Task`, or a `Bash` command outside the read-only `gh`/`git` allowlist — but N full agents still run concurrently. Raising `--num-workers` much past the default (5), or removing the early-exit, will spawn enough parallel clone/build work to exhaust memory on a typical machine.

## Regression check

Diff each query's PASS/FAIL verdict, not the raw `trigger_rate` values (which are stochastic and flag sampling noise):

```bash
project='{
  should_trigger_pass, should_not_trigger_pass,
  results: [.results[] | {query, should_trigger, pass: ((.trigger_rate >= 0.5) == .should_trigger)}]
}'
diff <(jq -S "$project" baseline.json) <(jq -S "$project" result.json)
```

Empty diff means no regression; a non-empty diff means a query flipped PASS↔FAIL (the changed `pass` field names it). If a new failure appears, fix the skill description rather than the eval set — the eval set encodes intent, not implementation. If the change is intentional and the new run is the new desired behavior, replace `baseline.json` with `result.json` and commit alongside the description change.

## Updating the test surface

Update `trigger-eval.json` (not the runner) when the test surface needs to evolve: a new natural-language phrasing the skill should catch, a new sibling skill (e.g. a forward-looking test-recommendation skill) creating a new near-miss, or an existing query that turned out to be ambiguous. Keep should-trigger and should-not-trigger counts roughly balanced.
