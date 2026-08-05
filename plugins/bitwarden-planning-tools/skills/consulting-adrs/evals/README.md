# Evals: consulting-adrs

Eval set for the `consulting-adrs` skill, covering the three assertion
categories from Bitwarden's AI Review Guidelines: **Triggering**, **Structure**,
and **Behavior**. Baselines were recorded on `claude-opus-4-8`.

## Files

- `trigger-eval.json` — triggering cases (`{query, should_trigger}`).
- `baseline.json` — recorded trigger baseline, keyed by model id.
- `evals.json` — structure + behavior cases with assertions.
- `benchmark.json` — recorded structure/behavior result (with-skill vs baseline).
- `fixtures/adr/` — synthetic ADRs, structurally matching the real catalog's
  frontmatter (`adr`/`status`/`date`/`tags`), heading, and Deprecated-admonition
  format (`contributing.bitwarden.com/architecture/adr/`): accepted (9001, 9004,
  9005), a superseded->replacement pair (9002 -> 9005), and a deprecated one
  (9003). Superseded is a real, documented ADR status; the live catalog just
  hasn't used it yet. Fabricated so offline behavior cases grade
  deterministically without depending on the live catalog. They are NOT real
  Bitwarden decisions.

## How to run

Structure + behavior: run each `evals.json` case with the skill vs without
(baseline), then grade blind; actual run counts per arm are recorded in
`benchmark.json`. Grading must be an **LLM
grader**, not regex: the finding tokens (`CONFLICT`/`GAP`/`STALE-REFERENCE`)
appear both as finding labels and inside roll-up count lines (`CONFLICT: 0`),
which defeats naive pattern matching. Blind all three tiers (subject, observer,
grader).

Behavior cases point the skill at `fixtures/adr/` via its local-clone path so
grading is deterministic and offline. The `source-call-live` case provides no
local checkout, so the skill must reach `contributing.bitwarden.com`; the
recorded assertions check that the output cites a real ADR path and does not
fabricate, not that a fetch actually occurred.

## Known issues / boundaries

- **Under-trigger on "review my PR for alignment with our recorded architecture
  decisions".** A genuine should-trigger phrasing fires only 1/3 (goes silent,
  not to a competitor).
