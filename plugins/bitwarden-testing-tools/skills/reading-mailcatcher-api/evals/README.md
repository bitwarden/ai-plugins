# reading-mailcatcher-api trigger evals

Reproducible trigger-rate test for the `bitwarden-testing-tools:reading-mailcatcher-api` skill. Run before merging any change to the skill's `description` frontmatter to confirm the change does not degrade triggering on the email-reading phrasings the skill is designed to catch, or start firing on near-miss queries that want SMTP configuration, email-template work, or server-side flow explanation.

## Files

- `trigger-eval.json`: 20-query test set. 10 should-trigger phrasings covering the flows the skill names (account verification, magic link, trial activation, OTP, password reset, org invite, emergency access) addressed by recipient and by subject. 10 should-not-trigger near-misses that share the words "email", "mail", and "mailcatcher" but want something the skill does not do: debugging mail delivery, configuring SMTP, starting containers, writing or reviewing email-template code, explaining the server-side flow, or inventorying test coverage.
- `run_real_eval.py`: a thin configuration wrapper over the plugin's shared runner at `scripts/eval_harness.py`, setting only the target skill token. The harness spawns parallel `claude -p` subprocesses, parses streamed tool-use events, and computes per-query trigger rates.

## Last observed reading

This is an on-demand diagnostic, not a committed regression control. See "Why no committed baseline" below.

Last run 2026-08-21, model `claude-opus-4-8`, 20 queries at `--runs-per-query 3`, against the installed ten-skill inventory (`assessing-test-coverage`, `build-test-cases`, `compiling-test-report`, `determining-required-services`, `executing-web-tests`, `exploring-application-context`, `reading-mailcatcher-api`, `test-web-changes`, `using-stripe-cli`, `verifying-environment-health`): should_trigger 10/10, should_not_trigger 10/10. Taken after the TTM-06 negative-scope clause was added to the description; the runs-per-query differs from the earlier 7-run readings by TTM-06 design, so the figures are read on their own, not diffed against them.

Resolved misfire: the near-miss "start the mailcatcher container for me" previously triggered 7/7 against a description with no negative scope. After the TTM-06 clause was added (the skill reads messages only and does not start, stop, or health-check the Mailcatcher container or any other service), it now reads should-not-trigger (0/3 this run). Service lifecycle is the user's responsibility outside the pipeline.

## Why no committed baseline

A trigger rate depends on the skill description, the harness, the model, and the full set of installed skills competing for selection. Three of those four are outside this skill, so a committed `baseline.json` goes stale whenever the model is bumped or the plugin's skill set changes, neither of which is a change to this skill. Nothing re-runs these evals, so a committed file cannot act as a live regression control regardless. We keep the query set and the shared harness, record the last observed reading above as a dated diagnostic, and re-run on demand when editing this skill's description, comparing a fresh before and after in the same session. This diverges deliberately from skill-creator's baseline-oriented methodology, which assumes the description can be tuned in response to the number. Do not restore a committed baseline here.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`. The eval reads the **installed** copy of the plugin, not this working tree. Install from a marketplace entry that points at this working directory (`bitwarden-marketplace` tracks GitHub, so use a local marketplace added separately for this purpose), then reinstall to pick up any local edit:

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

## On-demand comparison

There is no committed baseline to diff against. When editing this skill's `description`, run the eval once before the edit and once after, in the same session so the model and installed inventory match, and diff the two by PASS/FAIL verdict rather than the raw `trigger_rate` values, which are stochastic:

```bash
project='{
  should_trigger_pass, should_not_trigger_pass,
  results: [.results[] | {query, should_trigger, pass: ((.trigger_rate >= 0.5) == .should_trigger)}]
}'
diff <(jq -S "$project" before.json) <(jq -S "$project" after.json)
```

An empty diff means the edit changed no verdict. Fix the skill description rather than the eval set if an edit regresses a verdict, and update the "Last observed reading" prose above when you record a new run.
