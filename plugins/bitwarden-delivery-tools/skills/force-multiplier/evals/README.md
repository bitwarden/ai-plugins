# force-multiplier evals

Behavior test cases for the `force-multiplier` skill, in the `skill-creator` schema.

`evals.json` holds seven cases covering the skill's substantive, checks-are-the-product decisions: campaign compilation, refusing `--no-pilot` on an agentic recipe, the two-way applicability filter, the destructive-recipe reference-check, held-back reconciliation, the total-fan-out ceiling, and untrusted repo content. Each case's `expectations` are the pass criteria; a case gains a `notes` field once ablation records an outcome (earned vs. borderline).

Cases are **advice-only** — they grade the plan the skill produces and run no live clones, commits, or PRs, so the benchmark is mutation-safe.

Run with `/skill-creator:skill-creator` in Benchmark mode (with-skill vs. without-skill), several runs per config with a config-blind grader. Cases 2, 4, 5, 6, and 7 guard the internal-coherence fixes; ablating the corresponding instruction and re-running is how each fix earns its keep.
