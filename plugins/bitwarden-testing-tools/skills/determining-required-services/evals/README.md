# determining-required-services evals

Behavior test cases for the `determining-required-services` skill, in the `skill-creator` schema.

`behavior-eval.json` holds four cases covering the skill's substantive decisions: taking the union of route-based and file-path-based dependencies rather than one alone, running its own `git diff --name-only origin/main...HEAD -- <repo-path>` rather than relying on the caller, sourcing names, URLs, and ports from `references/services.md` rather than recall, and returning a minimal set matched by the documented rules rather than a defensively padded one.

Each case's `expectations` are the pass criteria. Cases are **advice-only** and start no services, so re-runs are mutation-safe.

Case 2's expectations "Does not proceed on route information alone while silently skipping the diff" and "Runs its own `git diff --name-only origin/main...HEAD -- <repo-path>` rather than requesting the changed-file list" are did-not-take-an-action checks: a correct run never asks the caller for the file list and leaves no trace of that omission in the final markdown artifact either way. Grading them requires the benchmark harness to capture the tool-call trace (that a `git diff` command actually ran), not just the final output, so whoever runs the benchmark should confirm trace capture is enabled before scoring this case.

Case 3's expectation about sourcing ports from `references/services.md` is only weakly exercised by its prompt: the web vault login page requires Web, Api, and Identity, all three of which are fully documented with URLs and ports in the reference, so this case never puts the model in a position where a service is genuinely absent from the reference. It confirms sourcing from the reference is possible to check, not that the skill handles a missing-service case correctly, since the skill's own text does not document a missing-service contingency to test against.

## Files

- `behavior-eval.json` - the four cases and their 16 expectations, described above.
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
