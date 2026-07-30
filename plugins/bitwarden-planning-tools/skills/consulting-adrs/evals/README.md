# Evals: consulting-adrs

Eval set for the `consulting-adrs` skill, covering the three assertion
categories from Bitwarden's AI Review Guidelines: **Triggering**, **Structure**,
and **Behavior**. Baselines were recorded on `claude-opus-4-8`.

## Files

- `trigger-eval.json` — triggering cases (`{query, should_trigger}`).
- `baseline.json` — recorded trigger baseline, keyed by model id. Run with
  `bitwarden-eval-tools:running-trigger-evals` in isolated mode.
- `evals.json` — structure + behavior cases with assertions.
- `benchmark.json` — recorded structure/behavior result (with-skill vs baseline).
- `fixtures/adr/` — synthetic ADRs modeled on the real catalog
  (`contributing.bitwarden.com/architecture/adr/`): accepted (0001, 0004, 0005),
  a superseded->replacement pair (0002 -> 0005), and a deprecated one (0003).
  Fabricated so offline behavior cases grade deterministically without depending
  on the live catalog. They are NOT real Bitwarden decisions.

## How to run

Triggering (isolated mode, unmerged skill):

```
python3 <bitwarden-eval-tools>/skills/running-trigger-evals/scripts/trigger_eval.py \
  --mode isolated --skill-path <this skill dir> \
  --eval-set evals/trigger-eval.json --model claude-opus-4-8 \
  --runs-per-query 3
```

Structure + behavior: run each `evals.json` case with the skill vs without
(baseline), several runs each, then grade blind. Grading must be an **LLM
grader**, not regex: the finding tokens (`CONFLICT`/`GAP`/`STALE-REFERENCE`)
appear both as finding labels and inside roll-up count lines (`CONFLICT: 0`),
which defeats naive pattern matching. Blind all three tiers (subject, observer,
grader).

Behavior cases point the skill at `fixtures/adr/` via its local-clone path so
grading is deterministic and offline. The `source-call-live` case provides no
local checkout, so the skill must reach `contributing.bitwarden.com` — it
verifies the skill consults the real source and cites a real ADR.

## Recorded results (claude-opus-4-8)

Triggering: should-trigger 7/8, should-not-trigger 6/6 (clean isolated run, no
duplicate-copy contamination). Structure + behavior: with-skill 1.00 vs baseline
0.78 run-pass-rate over 9 cases.

The skill matched the no-skill baseline on straightforward classification and
beat it on the discriminating cases: the baseline failed to emit an explicit
GAP classification for the event-bus case, and fabricated an ADR on the live
source-call case where the skill fetched the real ADR-0030. The summarize/lookup
case matches baseline (both 1.00) after a fix — see below.

## Known issues / boundaries

- **Under-trigger on "review my PR for alignment with our recorded architecture
  decisions".** A genuine should-trigger phrasing fires only 1/3 (goes silent,
  not to a competitor). The clearest candidate for a description tweak if trigger
  coverage proves insufficient in practice.
- **Mild over-trigger on ADR authoring / conceptual asks.** "Help me write a new
  ADR" and "What's an ADR" each trigger 1/3 (authoring/explaining is out of scope;
  consulting/summarizing is in scope). Below the pass threshold, but flaky.
- **Summarize/lookup fabrication (fixed).** An early summarize run invented
  `contributing.bitwarden.com` URLs for catalog ADRs (1/3 runs). The summarize
  branch now says to cite the local path and never construct a URL; re-run
  passes 3/3. Kept because it also removes the fabrication the naive version had.
- **Output format consistency:** the skill emits the finding label in varying
  styles (`[CONFLICT]`, `CONFLICT:`, `**[CONFLICT]**`). Classification is always
  correct; only the surface token style varies. Left lean; tighten the SKILL.md
  format spec if a downstream consumer needs a strictly parseable token.
