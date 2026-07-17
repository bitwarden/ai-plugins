# Authoring trigger eval sets

An eval set for this runner is a JSON array of cases, each a `{query,
should_trigger}` pair:

```json
[
  { "query": "package this up into a draft pr", "should_trigger": true },
  { "query": "merge PR #4567, CI is green", "should_trigger": false }
]
```

`query` is the real trigger phrasing a user would type. `should_trigger` is the
checkable expectation: whether the skill under test should fire on it.

## Balance the trigger boundary

Include true positives and near-miss negatives in **roughly equal number**; a
lopsided set biases the pass rate toward whichever class dominates. The runner
emits a non-blocking stderr `WARNING:` when the split is off by more than
~20%; treat it as a prompt to rebalance, not a gate.

Cover, at minimum:

- the primary success path or paths (true positives on the real asks);
- each near-miss the description risks over-triggering on (true negatives);
- at least one clearly out-of-scope case, to confirm the skill declines it.

## Write real near-misses

A near-miss shares surface vocabulary with the true positives but is
genuinely a different ask: the kind of phrasing that tempts a too-broad
description to fire. For a "create a pull request" skill, near-misses
include asking about PR _status_, _merging_ an existing PR, or _explaining
how PRs work_: all mention "PR", none should trigger skill creation. Weak
negatives (obviously unrelated topics) pass trivially and prove nothing.
Mine real near-misses from sibling skills and from phrasings that have
caused mis-triggers before.

## Account for non-determinism

Run each case several times (`--runs-per-query`, default 3); a query firing
three of five runs is a real reliability problem, not a borderline pass. See
`SKILL.md` for how the runner reports and weights this.

## Record a baseline

Run the set against the current version and keep the recorded summary as the
baseline. That recorded result is the contract: a net-new skill establishes it,
and every later edit must hold or beat it. Feed it back with
`--check-regression --baseline <file>` on subsequent runs.

## Installed mode is environment-sensitive

A pass rate from `--mode installed` reflects every plugin installed alongside
the skill under test, not just the skill itself. A query can fire a competing
sibling instead of the target, dropping the target's rate with no change to
the target. Treat a baseline as comparable only against runs from a similar
plugin footprint; check per-case samples before calling a rate drop a
regression. `--exclude-skill` surfaces this competition as a visibility
signal.

## Blinding: keep the eval honest

Three tiers must each be blind:

- **The subject is blind.** The skill runs exactly as in production. Do not
  phrase a query to telegraph the wanted answer, and do not signal that an eval
  is underway.
- **The observer is blind.** Whoever runs the cases does not steer toward the
  expected outcome, retry until it passes, or record selectively. Running the
  full set unattended via the script satisfies this.
- **The grader is blind and independent.** Scoring here is deterministic: the
  runner counts token fires, which removes grader bias by construction, as long
  as eval-set expectations were set before seeing results, not fitted to them
  afterward.

## Keep it proportional

A net-new skill warrants a spread of cases across all the above. A one-line
description edit warrants only the cases touching what changed, run against the
existing baseline. Match the effort to the surface at risk; do not demand a full
harness for a typo fix.
