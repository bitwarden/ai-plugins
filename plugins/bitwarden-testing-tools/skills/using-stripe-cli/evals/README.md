# using-stripe-cli evals

Behavior test cases for the `using-stripe-cli` skill, in the `skill-creator` schema.

`behavior-eval.json` holds seven cases covering the skill's substantive decisions: the read-only boundary, the single permitted write of advancing an already-attached test clock, the subordination rule that Stripe must not create state the application's own flows can create, the never-permitted database and feature-flag shortcuts, and untrusted content inside Stripe metadata.

Each case's `expectations` are the pass criteria. Denominators differ per case because they count expectations, not runs.

Cases are advice-only and mutation-safe. They grade the decision the skill produces and issue no Stripe calls, so they need no Stripe credentials and re-runs are safe.

## Files

- `behavior-eval.json` - the seven cases and their 28 expectations, described above.
- `behavior-baseline.json` - not present. This suite has not been benchmarked; the case set stands on its own as a behavioral specification and authoring aid (see below).

## Running

This suite runs with `/skill-creator:skill-creator` in Benchmark mode (with-skill versus without-skill) with a config-blind grader. It has not been benchmarked. A behavior-suite benchmark is a conversational with-skill-versus-without-skill ablation orchestrated through skill-creator, with no scriptable benchmark command, and running all of this plugin's behavior suites is on the order of 250 full agent runs, so no run has been made. The case set is kept as a behavioral specification and an authoring aid: it documents, as worked examples with pass criteria, the load-bearing decisions this skill must make. If the suite is benchmarked, record `behavior-baseline.json` in the same change.

If the suite is ever benchmarked, a subsequent change to `SKILL.md` should be paired with a re-run and a refresh of `behavior-baseline.json`.

## Regression check

Once `behavior-baseline.json` exists, regressions will be checked with:

```bash
diff <(jq -S . behavior-baseline.json) <(jq -S . result.json)
```

An empty diff will mean no regression. When a change is intentional and the new numbers are the desired state, `behavior-baseline.json` should be replaced in the same PR as the skill change.
