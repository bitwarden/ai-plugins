# verifying-doc-parity evals

Behavior test cases for the `verifying-doc-parity` skill, in the `skill-creator` schema.

`behavior-eval.json` holds cases exercising what happens when the skill fires. Covers both primary success paths (session and pull-request review), every outcome the skill claims to produce (Update, Attest, Dismiss), and each recently-added instruction (below-component source-embedded surfaces, placement follows what the doc describes, root-level placement for a repo-wide capability).

`behavior-baseline.json` is the recorded benchmark that intentional skill changes must not regress silently.

## Do not add trigger evals for this skill

It was found that the `run_eval.py`'s methodology incorrectly failed to detect skill triggers due to requiring immediate skill execution rather than context exploration, which models almost always do regardless of description changes.

This skill's load-bearing invocation paths are the doc-parity Stop hook and the ai-review workflow's documentation pass. Natural-language triggering is a nice-to-have fallback, not the critical path.

## Eval cases

Behavior cases run against the Seeder subsystem of [bitwarden/server](https://github.com/bitwarden/server) (`util/Seeder/`, `util/SeederApi/`, `util/SeederUtility/`), chosen because its code-to-docs mapping is known.

These evals are executed against a pinned server ref, `d6c84a7562cc6b464de910dbf829690885500137`. To increase stability in testing, evaluate against that reference point.

Each case is constructed so a run that skips a documented scope, stays silent instead of attesting, token-edits its way past the gate, or mishandles a specific outcome type (Update, Attest, Dismiss) fails a named expectation. Behavior cases assume the run happens inside a bitwarden/server checkout so the ground-truth docs are readable.

Case 10 exercises the review context (out-of-repo discovery against the contributing-docs corpus); all other cases are session cases. Cases involve live edits to a scratch checkout, so run them against a disposable clone or a git worktree, never a working tree you care about.

Each case's `expectations` array is the pass criterion — every expectation is graded independently. Denominators differ per case because they count expectations, not runs.

## Running

Run with `/skill-creator:skill-creator` in benchmark mode (with-skill vs. without-skill) with a config-blind grader. Install the runner from the `claude-plugins-official` marketplace if it is not already present:

```bash
/plugin install skill-creator@claude-plugins-official
```

The AI Review Guidelines want at least three iterations per case per configuration so pass rate and variance are both captured.

Regression check against the current baseline compares the aggregate summary and per-run pass rates; timestamps, models, and per-run evidence prose vary on every execution and are not signal:

```bash
proj='{run_summary, runs: [.runs[] | {eval_id, configuration, run_number, pass_rate: .result.pass_rate}]}'
diff <(jq -S "$proj" behavior-baseline.json) <(jq -S "$proj" result.json)
```

An empty diff on that projection means no regression on the graded data. When a change is intentional and the new numbers are the new desired state, replace the baseline with the new results in the same PR as the skill change.

## Updating the test surface

Update `behavior-eval.json` when the test surface needs to evolve: a new load-bearing rule in the skill, a Seeder doc restructure that invalidates a case's ground truth, or an expectation that turned out to be ambiguous. The eval set encodes intent, not implementation — when a run fails, fix the skill, not the case, unless the case itself is wrong.
