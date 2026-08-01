# using-stripe-cli evals

Behavior test cases for the `using-stripe-cli` skill, in the `skill-creator` schema.

`behavior-eval.json` holds seven cases covering the skill's substantive decisions: the read-only boundary, the single permitted write of advancing an already-attached test clock, the subordination rule that Stripe must not create state the application's own flows can create, the never-permitted database and feature-flag shortcuts, and untrusted content inside Stripe metadata.

Each case's `expectations` are the pass criteria. Denominators differ per case because they count expectations, not runs.

Cases are advice-only and mutation-safe. They grade the decision the skill produces and issue no Stripe calls, so they need no Stripe credentials and re-runs are safe.

## Files

- `behavior-eval.json` - the seven cases and their 28 expectations, described above.
- `behavior-baseline.json` - not yet recorded. This suite is authored ahead of its first benchmark run; the file will be added once that run happens.

## Running

This suite is intended to run with `/skill-creator:skill-creator` in Benchmark mode (with-skill versus without-skill) with a config-blind grader. That benchmark has not been run yet. It will be run, and `behavior-baseline.json` recorded, in a later dedicated pass once all of this plugin's behavior suites exist, so they can be benchmarked together rather than one at a time. Until then, this file set defines intent (what the skill should be graded on) rather than a measured control.

When the benchmark does run, any subsequent change to `SKILL.md` should be paired with a re-run and a refresh of `behavior-baseline.json`.

## Regression check

Once `behavior-baseline.json` exists, regressions will be checked with:

```bash
diff <(jq -S . behavior-baseline.json) <(jq -S . result.json)
```

An empty diff will mean no regression. When a change is intentional and the new numbers are the desired state, `behavior-baseline.json` should be replaced in the same PR as the skill change.
