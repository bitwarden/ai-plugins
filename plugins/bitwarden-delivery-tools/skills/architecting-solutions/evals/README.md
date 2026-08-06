# architecting-solutions evals

Behavior test cases for the `architecting-solutions` skill, in the `skill-creator` schema.

`behavior-eval.json` holds nine cases targeting the Bitwarden-specific parts of the skill.

Each case's `expectations` are the pass criteria. Denominators differ per case because they count expectations, not runs — every expectation is graded independently for both configurations.

Cases are **advice-only** — they grade the design the skill produces and run no live edits, commits, or PRs, so re-runs are mutation-safe.

Run with `/skill-creator:skill-creator` in Benchmark mode (with-skill vs. without-skill) with a config-blind grader. Any change to `SKILL.md` should be paired with a re-run and a refresh of `behavior-baseline.json`; the baseline is what future comparisons diff against.

`behavior-baseline.json` records the pass/fail rate per case, keyed by model + effort. Regression check:

```bash
diff <(jq -S . behavior-baseline.json) <(jq -S . result.json)
```

An empty diff means no regression. When a change is intentional and the new numbers are the new desired state, replace `behavior-baseline.json` with the new results in the same PR as the skill change.
