# Validation snapshot: managing-workflow-secrets

> **Historical, point-in-time report — not a live result.** These numbers reflect one model at one
> date against the case set as it stood then. There is **no committed runner**, so nothing in this
> repo refreshes them: they only go stale. Re-run the evals yourself before trusting any figure here,
> and treat a mismatch with the current `evals.json` as expected, not a regression.

**Model**: `<model-name>` (scrubbed — no model names are hardcoded)
**Date**: 2026-08-19
**Source**: two workspace iterations (evals 0–3, then 6–7), since condensed and discarded.

## Benchmark — with-skill vs without-skill

Each eval feeds the model the same prompt + fixture with and without the skill; a pass means every
expectation in the case's rubric was met.

| Eval | Name                     | Runs | With skill | Without skill | Without-skill miss                                                    |
| ---- | ------------------------ | ---- | ---------- | ------------- | --------------------------------------------------------------------- |
| 0    | add-secret-retrieval     | 1    | 100%       | 86%           | used `id: get-kv-secrets`, not canonical `id: secrets`                |
| 1    | downstream-job-handoff   | 1    | 100%       | 100%          | —                                                                     |
| 2    | flag-secret-exposure     | 1    | 100%       | 100%          | —                                                                     |
| 3    | reusable-workflow-triad  | 1    | 100%       | 60%           | `secrets: inherit`; omitted the two-sided contract note               |
| 4    | multi-secret-folded-list | —    | not run    | not run       | —                                                                     |
| 5    | app-token-cross-job      | —    | not run    | not run       | —                                                                     |
| 6    | logout-live-session      | 3    | 100%       | 80%           | third-party `azure/login` + raw `az logout`, not the internal actions |
| 7    | ask-for-names            | 3    | 100%       | 40%           | invented concrete vault/secret names instead of asking                |

**Aggregate over the six evals that were run (0–3, 6, 7):** with-skill 100%, without-skill 77.6%,
delta **+0.224**.

## Ablation — does each instruction earn its place?

Method: remove one instruction from a copy of the skill, re-run the case that should depend on it,
compare to the full-skill baseline. Regression ⇒ the instruction is additive. Single run each;
non-determinism not controlled for.

| Instruction                                      | Case                        | Ablated result       | Verdict                                                             |
| ------------------------------------------------ | --------------------------- | -------------------- | ------------------------------------------------------------------- |
| Standardize retrieval step on `id: secrets`      | eval-0 add-secret-retrieval | `id: kv`             | ADDITIVE (confounded: example ids also changed)                     |
| Cross-repo reusable wf: pass triad explicitly    | eval-3 reusable-wf-triad    | `secrets: inherit`   | ADDITIVE — loses least-privilege convention                         |
| Never infer vault/secret names; placeholders+ask | eval-7 ask-for-names        | context-derived name | WEAKLY ADDITIVE — marginal; ask behavior survived ablation. Review. |

**Not yet ablated** (defined as cases but not yet run): folded block scalar for ≥3 secrets (eval-4),
short-lived GitHub App token for cross-job GitHub access (eval-5).

## Triggering — right prompts fire, near-misses don't

12 queries, 5 runs each across 5 judges. **Accuracy 1.0**: all 6 positives fired 5/5, all 6
negatives fired 0/5. Near-miss negatives route to sibling skills (bitwarden-workflow-linter-rules,
workflow-audit/fix, action-audit/remediate, auditing-workflow-conventions) or to no skill.

## Caveats

- **Evals 4 and 5 were never run** — authored after these iterations; excluded from the aggregate.
- **Uneven run counts** — evals 0–3 are single-run per configuration; 6–7 are 3× with-skill, 1×
  without-skill. Single-run figures are indicative, not variance-controlled.
- **Grader blindness to configuration is not established** — the run records were labeled
  with/without-skill.
