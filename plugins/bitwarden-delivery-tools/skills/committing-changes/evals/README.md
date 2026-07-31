# committing-changes evals

Two eval sets. Run the one that matches what changed.

| Changed                      | Run                                  |
| ---------------------------- | ------------------------------------ |
| `description` or frontmatter | trigger eval (`trigger-eval.json`)   |
| skill body                   | behavior eval (`behavior-eval.json`) |

## Trigger eval

Does the skill activate on the right phrasings and stay silent on near-misses? `trigger-eval.json` holds 13 queries; `run_real_eval.py` runs them (see `../../creating-pull-request/evals/run_real_eval.py` for why this runner exists instead of the skill-creator harness); `baseline.json` is the last known-good run. Requires Python 3.10+ and an authenticated `claude` CLI.

```bash
python3 run_real_eval.py --eval-set trigger-eval.json --runs-per-query 3 \
  --num-workers 8 --timeout 60 --model claude-opus-4-7 > result.json

diff <(jq -S . baseline.json) <(jq -S . result.json)
```

Empty diff means no regression. Fix the description rather than the eval set; if a change is intentional, replace `baseline.json` in the same PR.

**Known flaky query:** `create a new branch for the PM-33210 work before I start coding, nothing to commit yet` sits near the decision boundary and `baseline.json` records it at 1-of-3. A clean re-run can diff non-empty with no regression — judge that query by whether it stayed under the 0.5 threshold, not by byte equality.

## Behavior eval

Does an active skill change the output? Cases live in `behavior-eval.json` (`skill-creator` schema, matching `../../architecting-solutions/evals/`); pass rates in `behavior-baseline.json`, keyed by model and effort. Run with `/skill-creator:skill-creator` in Benchmark mode with a config-blind grader. Every expectation is graded independently, so denominators are expectations × runs.

Cases are **advice-only** — git state is quoted in the prompt and the graded artifact is the stated plan, so re-runs mutate nothing. The cost is that they grade what the skill says it would do. Where a case must prove a gate actually stops a mutation, use a live disposable fixture and hand-run it.

### Arms

- `no-skill` — is the skill load-bearing at all? The right control when adding a skill.
- `old-skill` — did this edit regress anything? **Required whenever the skill body changes.** Snapshot the previous version (`git show <ref>:.../SKILL.md`). `no-skill` cannot answer this: old and new both beat it, so it can't detect an edit that made things worse.
- `new-skill` — the working tree.

Refresh `behavior-baseline.json` in the same PR as the skill change.

Caveats on the current numbers:

- The advice-only framing inflates `no-skill`. `default-is-main-no-hint` scores 12/16 with no skill at all, where a live fixture had the pre-change skill committing straight to `main`.
- Only `default-is-main-no-hint` and `default-unresolvable` separate the arms. The other four sit at ceiling in all three, so treat them as regression guards rather than evidence.
- A default named `main` or `master` cannot isolate the resolution instruction, because a model declines to commit onto either name unprompted. `default-is-master` shows the gate fires on a non-`main` default; it is not proof that resolution beats name matching.

### Methodology

- **Point at the skill by file path, not by name.** The installed plugin cache lags the working tree, so `Skill(bitwarden-delivery-tools:committing-changes)` gets the last published version, not your edit. Copy SKILL.md to a scratch path and have the subagent read it.
- **Never let a subagent invoke an interactive question tool for real** — it may reach a live human. Tell it: non-interactive, no follow-up coming, state any question as plain text and stop.
- Keep the grader blind (shuffle response-index-to-arm per case, keep the mapping out of paths the grader is given), and supply every input the skill doesn't claim to decide so a stall is attributable to the thing under test.
