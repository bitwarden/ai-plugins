# recommending-test-layers trigger evals

Reproducible trigger-rate test for the `bitwarden-testing-tools:recommending-test-layers` skill. Run before merging any change to the skill's `description` frontmatter to confirm the change doesn't degrade triggering on the natural-language phrasings the skill is designed to catch (or start firing on near-miss queries that want a different kind of test work). This skill shares trigger space with its two siblings, so also re-run the `assessing-test-coverage` eval after any description change here to confirm neither skill cannibalizes the other's triggers.

## Why a custom runner

The upstream `skill-creator` harness measures triggering by registering a temporary copy of the skill under a UUID-suffixed name and watching whether the model invokes that exact name. When the real plugin-registered skill is already installed in the test environment, the model invokes the real one and the harness records a false negative. `run_real_eval.py` instead watches `claude -p` stream events for any invocation of the real `recommending-test-layers` skill, ignoring unrelated session-init or workflow skills that may fire first.

## Files

- `trigger-eval.json` — 19-query test set: 10 should-trigger phrasings asking a forward-looking question about which tests to add and at which layer, spanning the documented input types (a Jira key, a Testmo CSV, an `assessing-test-coverage` report, a PR, and a feature description) and phrasings like "are unit tests enough", "trophy or pyramid", "which layer should this live at", and "do we need an E2E or can component cover it"; and 9 should-not-trigger near-misses that share the words "test"/"coverage"/"layer" but want something the skill deliberately does not do: inventorying coverage that already exists (`assessing-test-coverage`), authoring manual Gherkin cases (`writing-manual-test-cases`), writing or refactoring automated test code, running or fixing existing tests, reading an overall coverage percentage, or a general PR review.
- `run_real_eval.py` — runner. Spawns parallel `claude -p` subprocesses, parses streamed tool-use events, computes per-query trigger rates. Each subprocess is killed as soon as the model requests `Task`, or a `Bash` command outside the read-only `gh`/`git` allowlist, without first invoking the target skill — so the adversarial should-not-trigger queries never actually clone repos or run build/test toolchains. See the note under "Running".
- `baseline.json` — last known-good run. Diff against this to spot regressions on future description changes. Recorded 2026-09-03 with `--model sonnet` at `--runs-per-query 7`; use the same model when re-running so verdicts are comparable.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`. The plugin must be installed and enabled (`claude plugin install bitwarden-testing-tools@bitwarden-marketplace`), or every query records a false non-trigger. The eval reads the installed copy, not this working tree, so **reinstall after editing the skill** (uninstall + install) before running.

```bash
python3 run_real_eval.py \
  --eval-set trigger-eval.json \
  --runs-per-query 7 \
  --num-workers 5 \
  --timeout 90 \
  --model sonnet \
  > result.json
```

19 queries × 7 runs = 133 `claude -p` invocations. With 5 workers the run takes several minutes.

Each `claude -p` subprocess is a full agent, so keep `--num-workers` modest: the 9 should-not-trigger queries are adversarial real-work prompts, and the runner already bails the instant such a query reaches for `Task`, or a `Bash` command outside the read-only `gh`/`git` allowlist, but N full agents still run concurrently. Raising `--num-workers` much past the default (5), or removing the early-exit, will spawn enough parallel clone/build work to exhaust memory on a typical machine.

The first recorded run is also the baseline: redirect it to `baseline.json` and commit it alongside the skill.

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

Update `trigger-eval.json` (not the runner) when the test surface needs to evolve: a new natural-language phrasing the skill should catch, a new sibling skill creating a new near-miss, or an existing query that turned out to be ambiguous. Keep should-trigger and should-not-trigger counts roughly balanced.
