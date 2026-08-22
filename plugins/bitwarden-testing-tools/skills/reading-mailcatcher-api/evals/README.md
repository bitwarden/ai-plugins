# reading-mailcatcher-api trigger evals

Reproducible trigger-rate test for the `bitwarden-testing-tools:reading-mailcatcher-api` skill. Run before merging any change to the skill's `description` frontmatter to confirm the change does not degrade triggering on the email-reading phrasings the skill is designed to catch, or start firing on near-miss queries that want SMTP configuration, email-template work, or server-side flow explanation.

## Files

- `trigger-eval.json`: 20-query test set. 10 should-trigger phrasings covering the flows the skill names (account verification, magic link, trial activation, OTP, password reset, org invite, emergency access) addressed by recipient and by subject. 10 should-not-trigger near-misses that share the words "email", "mail", and "mailcatcher" but want something the skill does not do: debugging mail delivery, configuring SMTP, starting containers, writing or reviewing email-template code, explaining the server-side flow, or inventorying test coverage.
- `run_real_eval.py`: a thin configuration wrapper over the plugin's shared runner at `scripts/eval_harness.py`, setting only the target skill token. The harness spawns parallel `claude -p` subprocesses, parses streamed tool-use events, and computes per-query trigger rates.
- `baseline.json`: last known-good run. Diff against this to spot regressions on future description changes.

## Baseline provenance (provisional)

A trigger eval measures whether the model auto-selects a skill from a natural-language query, and that outcome depends on which sibling skills are installed alongside it, since the model is choosing among all of them. The `baseline.json` committed here was recorded on 2026-08-01 against a plugin containing exactly these four skills:

- `assessing-test-coverage`
- `compiling-playwright-report`
- `reading-mailcatcher-api`
- `using-stripe-cli`

This plugin is still growing (ten skills are planned for the full stack), so this baseline is provisional. It will be re-recorded against the final skill inventory before the stack completes, and the number here should not be read as a final regression gate until then.

## Known consistent misfire (follow-up, not fixed here)

The near-miss query "start the mailcatcher container for me" triggers the skill on every recorded run (7/7). Starting a container is not reading a message under any reading of the skill's scope, so this is a genuine over-fire rather than eval noise or an ambiguous query. The description most likely attracts on the bare word "mailcatcher" beyond the message-reading scope it actually documents.

This is intentionally left as a documented follow-up rather than fixed in this eval task: `reading-mailcatcher-api` is migrated, already-working content, and this project's premise is that migrated skills stay byte-identical through the eval-authoring pass. Narrowing the description to satisfy an eval set written after the fact would invert that premise. Whoever owns the skill's `description` going forward should treat this as a known, reproducible case to weigh when next touching that frontmatter.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`. The eval reads the **installed** copy of the plugin, not this working tree. The `bitwarden-marketplace` entry already tracks this working directory, so reinstalling picks up any local edit:

```bash
claude plugin uninstall bitwarden-testing-tools
claude plugin install bitwarden-testing-tools@bitwarden-marketplace
```

Reinstall (uninstall then install) after every edit to the skill, or the run measures the previous copy.

```bash
python3 run_real_eval.py \
  --eval-set trigger-eval.json \
  --runs-per-query 7 \
  --num-workers 5 \
  --timeout 90 \
  --model claude-opus-4-8 \
  > result.json
```

20 queries times 7 runs is 140 `claude -p` invocations. Keep `--num-workers` at 5 or below: each worker is a full agent, and the should-not-trigger queries are adversarial real-work prompts.

## Regression check

Diff each query's PASS/FAIL verdict, not the raw `trigger_rate` values, which are stochastic.

```bash
project='{
  should_trigger_pass, should_not_trigger_pass,
  results: [.results[] | {query, should_trigger, pass: ((.trigger_rate >= 0.5) == .should_trigger)}]
}'
diff <(jq -S "$project" baseline.json) <(jq -S "$project" result.json)
```

Empty diff means no regression. If a new failure appears, fix the skill description rather than the eval set. If the change is intentional, replace `baseline.json` with `result.json` in the same PR as the description change.
