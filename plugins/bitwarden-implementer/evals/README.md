# bitwarden-implementer evals

Real cases certifying the agent as additive per the [AI Review Guidelines](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/3101458451/AI+Review+Guidelines).

## Run

Use `/skill-creator:skill-creator` as the harness. Run each case 3-5× to record pass rate and variance. Grade blind — the grader should not know which case is positive vs. negative, or which config version produced the output.

## Coverage

- **Trigger positives** (`trigger-positive-*`) — the agent activates on real "take this task to PR" asks (Jira ID, bug ticket, breakdown-doc fallback when the user cannot provide a Jira key).
- **Trigger negatives** (`trigger-negative-*`) — the agent does _not_ activate on: PR review of a teammate, breakdown decomposition, architectural choice, plan-only asks.
- **Behavior** (`behavior-*`) — golden path (small real bug), scope drift declined, deep design ambiguity surfaced as a stakeholder question, PR shape matches repo template and label conventions, self-review catches and fixes critical, orient reads breakdown + sibling epic tasks when a breakdown exists, blocker check stops the loop when `is blocked by` links are not yet Done, tasks track each phase of the loop, shallow gaps are investigated in the code before escalating.

## Baseline

`baseline.md` records the current pass rate for each case, along with variance across trials. Every subsequent change to `AGENT.md` must hold or beat these numbers. Regression without justification is a blocker.

## Ablation

To certify an instruction in `AGENT.md` as earned: remove it, re-run the case set, and confirm at least one case regresses. If nothing regresses, cut the instruction. This is the additive gate — the case set exists to make it enforceable.
