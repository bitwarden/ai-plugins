# using-stripe-cli evals

Trigger-rate diagnostic for the `bitwarden-stripe-tools:using-stripe-cli` skill, plus a behavior-eval case set that documents its load-bearing decisions as worked examples in the `skill-creator` schema.

## Files

- `trigger-eval.json`: 20-query test set. 10 should-trigger phrasings covering read-only Stripe test-mode data needs: subscription and test-clock status, payment and charge failures, price and coupon lookups, customer payment methods, invoices, and webhook events. 10 should-not-trigger near-misses covering code authoring, live or production data, Stripe configuration, and general questions about the billing flow, including a live customer and a production subscription named to test whether "test" phrasing alone is doing the work.
- `behavior-eval.json`: eight cases and their 32 expectations covering the skill's read-only boundary, the single permitted write of advancing an already-attached test clock, previewing a subscription's next invoice through the wrapper rather than treating it as a write, the subordination rule that Stripe must not create state the application's own flows can create, the database and feature-flag shortcuts it refuses, and untrusted content inside Stripe metadata. Cases are advice-only and mutation-safe: they grade the decision the skill produces and issue no Stripe calls, so they need no Stripe credentials and re-runs are safe.

No `baseline.json` or `behavior-baseline.json` is committed. A trigger baseline is tied to whichever skills are installed alongside this one at the time it was recorded, so it drifts whenever that inventory changes; the reading below states its own inventory instead. The behavior suite runs through a conversational with-skill-versus-without-skill ablation with no scriptable benchmark command, so the case set stands on its own as a behavioral specification rather than against a stored baseline.

## Running

The plugin's shared runner, [`evals/run_real_eval.py`](../../../evals/README.md), spawns parallel `claude -p` subprocesses, parses streamed tool-use events, and computes per-query trigger rates. See its README for prerequisites and for pinning the plugin's skill inventory to this working tree. Then, from this directory:

```bash
python3 ../../../evals/run_real_eval.py --eval-set trigger-eval.json --runs-per-query 3 --num-workers 3 --timeout 90 --model claude-opus-4-8 > result.json
```

The behavior suite runs separately, through `/skill-creator:skill-creator` in Benchmark mode with a config-blind grader, and has no scriptable command here.

## Last observed reading

Recorded 2026-10-07 with `claude-opus-4-8` at 3 runs per query, measured against this plugin's own inventory (`using-stripe-cli` alone, loaded with `--setting-sources project --plugin-dir` on this plugin): should-trigger 10/10, should-not-trigger 9/10. The one miss was `how do I configure the Stripe API keys in the server config?` at 2/3; re-run alone at 7 runs it triggered 3/7, a pass. With no sibling skill installed to take a Stripe-adjacent question, the model sometimes reads this skill to check, so expect that query to sit near the threshold in a single-plugin inventory.

## When to run

Run the trigger suite when the skill's `description` frontmatter changes. It is a diagnostic reading, not a merge gate. Run the behavior suite when a decision it covers changes in `SKILL.md`.
