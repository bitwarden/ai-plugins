# exploring-application-context evals

Behavior test cases for the `exploring-application-context` skill, in the `skill-creator` schema.

`behavior-eval.json` holds five cases covering the skill's substantive decisions: producing a state-centric decomposition rather than a changed-file inventory, discriminating a state that fails the observability validity gate (dropped silently) from a state that is observable but unreachable by playwright alone (disclosed explicitly), grounding selectors in real client code including the text-versus-structural selector rule, recording a `[HUMAN]` verification point when a check the tool policy disallows is the only way to confirm a state, and preserving the admin-email placeholder token rather than resolving it from local secrets.

Untrusted-content handling from a Jira ticket or its comments is deliberately out of scope for this suite. That behavior is owned by the agents that wrap this skill in the pipeline (`context-gatherer` and `code-explorer`), not by this skill itself: this skill's documented input is already-extracted feature description and acceptance criteria, not raw ticket content, and its `SKILL.md` never mentions Jira, tickets, or untrusted source content. A case exercising that boundary belongs in those agents' own eval suites.

Each case's `expectations` are the pass criteria. Denominators differ per case because they count expectations, not runs.

Cases are **advice-only**. They grade the Application Context the skill produces and run no live edits or browser sessions, so re-runs are mutation-safe.

## Files

- `behavior-eval.json` - the five cases and their 20 expectations, described above.
- `behavior-baseline.json` - not yet recorded. This suite is authored ahead of its first benchmark run; the file will be added once that run happens.

## Running

This suite is intended to run with `/skill-creator:skill-creator` in Benchmark mode (with-skill versus without-skill) with a config-blind grader. That benchmark has not been run yet. It will be run, and `behavior-baseline.json` recorded, in a later dedicated pass once all of this plugin's behavior suites exist, so they can be benchmarked together rather than one at a time. Until then, this file set defines intent (what the skill should be graded on) rather than a measured control.

When the benchmark does run, any subsequent change to `SKILL.md` should be paired with a re-run and a refresh of `behavior-baseline.json`.

Case 5's expectation "Does NOT read `server/dev/secrets.json`" is a did-not-take-an-action check: a correct run never touches the file and leaves no trace of that in the final markdown artifact either way. Grading it requires the benchmark harness to capture the tool-call trace, not just the final output, so whoever runs the benchmark should confirm trace capture is enabled before scoring this case.

## Regression check

Once `behavior-baseline.json` exists, regressions will be checked with:

```bash
diff <(jq -S . behavior-baseline.json) <(jq -S . result.json)
```

An empty diff will mean no regression. When a change is intentional and the new numbers are the desired state, `behavior-baseline.json` should be replaced in the same PR as the skill change.
