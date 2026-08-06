# test-web-changes evals

Two suites for the `bitwarden-testing-tools:test-web-changes` orchestrator and the six agents it dispatches.

## `trigger-eval.json`

20-query trigger-rate set for the orchestrator. 10 should-trigger phrasings covering all three input types (Jira key, Jira browse URL, plan file path, and free-form description), the `--confirm` review gate, and extra-guidance phrasings. 10 should-not-trigger near-misses that share the vocabulary but want something else: a backward-looking coverage inventory (which belongs to `assessing-test-coverage`), authoring a committed spec file, debugging a flaky test, starting the dev environment, test-layer strategy advice, PR review, test-pyramid explanation, running the existing jest suite, fixing a broken build, and writing manual QA notes.

Two of those near-misses deliberately target sibling tooling. `assessing-test-coverage` now lives in this same plugin, and `qa-testing-notes` is a separate skill, so proving no cross-fire is part of the set's job.

## `agent-non-trigger-eval.json`

8 queries, all `should_trigger: false`, testing a claim every one of the six agent descriptions makes: "Do not invoke directly; dispatched by the `test-web-changes` skill." Each query is phrased to tempt one specific agent with exactly the work it does.

Run `run_agent_eval.py --agent <name>` once per agent. A pass is zero triggers across all eight queries for all six agents.

The final two queries name an agent explicitly. A trigger there would be defensible rather than a defect, since the user asked for that agent by name, but see "Known limitation" below: the harness cannot observe a direct agent dispatch at all, so it cannot register a trigger on these two queries regardless of what the model actually does. Treat any recorded result on queries 7 and 8 as uninformative, not as a pass or a failure.

## Known limitation: this suite cannot fail by construction

The harness counts a trigger only on a `Skill` tool_use whose `input.skill` contains the target token, or a `Read` whose `file_path` contains the token and ends in `SKILL.md`. `run_agent_eval.py` passes an agent name as that token. A direct agent invocation surfaces as an `Agent` (or legacy `Task`) tool_use carrying `subagent_type`, which matches neither branch, so it is bailed to a non-trigger by the harness's exec-tool check regardless of whether the model actually dispatched the named agent directly.

This means the suite's `should_not_trigger_pass=8/8` result is guaranteed by the harness's detection gap, not measured evidence that the "do not invoke directly" convention holds. This suite does not currently validate that convention. Doing so requires extending the harness to count a trigger on an `Agent` tool_use whose `subagent_type` contains the target token. That extension is a known follow-up, not done here.

## Baseline provenance

These readings were recorded on 2026-08-01 against the final, ten-skill plugin inventory:

- `assessing-test-coverage`
- `build-test-cases`
- `compiling-test-report`
- `determining-required-services`
- `executing-web-tests`
- `exploring-application-context`
- `reading-mailcatcher-api`
- `test-web-changes`
- `using-stripe-cli`
- `verifying-environment-health`

plus all six agents (`context-gatherer`, `code-explorer`, `service-mapper`, `test-planner`, `service-manager`, `test-runner`). A trigger eval measures whether the model auto-selects a skill or agent from a natural-language query among everything installed alongside it, so the recorded numbers are only meaningful against this exact inventory.

### Orchestrator trigger suite: last observed reading

On-demand diagnostic, not a committed regression control. Last run 2026-08-01, model `claude-opus-4-8`, against the ten-skill inventory and six agents named above: should_trigger 10/10, should_not_trigger 10/10 at `--runs-per-query 7`, with no query in the 0.35-0.65 band. These numbers predate the addition of `Agent` to `scripts/eval_harness.py`'s `exec_tools` set, so the should_trigger figure is a ceiling and the should_not_trigger figure is a floor. There is no committed `baseline.json` for the orchestrator trigger suite: the query set and shared harness are kept and re-run on demand when editing the skill's description. This diverges deliberately from skill-creator's baseline-oriented methodology, which assumes the description can be tuned in response to the number; do not restore a committed baseline here.

### Agent suite result

`should_not_trigger_pass=8/8` for all six agents at `--runs-per-query 3`, meaning zero recorded triggers on queries 1 through 6 for every agent, and zero recorded triggers on queries 7 and 8 as well. The recorded baseline rows carry only `query`, `should_trigger`, `triggers`, `runs`, and `trigger_rate` (nothing about which tool actually fired), so this result does not establish that the orchestrator fired instead of the named agent on queries 7 and 8, only that the harness did not register a trigger. See "Known limitation" above: the harness cannot observe a direct agent dispatch at all, so `8/8` is guaranteed by construction rather than measured proof that the do-not-invoke-directly convention held.

This committed baseline was also recorded before `Agent` was added to the harness's `exec_tools` bail-out set, which is a separate, unrelated gap from the detection limitation above; it should likewise be re-recorded before being relied on as a regression control.

One query (`gather the context for PM-40020 from Jira and give me the affected repos and acceptance criteria`) hit a single run-level timeout on two of the six agents (`test-planner`, `test-runner`), each counted conservatively as a non-trigger by the harness. The query still passed 0/3 on both, so this is noted for transparency rather than as a finding.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH` at v2.1.129 or later, since the pipeline's script grants depend on `${CLAUDE_SKILL_DIR}` substitution inside `allowed-tools`.

The eval reads the **installed** copy, and the `bitwarden-marketplace` entry tracks `main` only. For an unmerged branch, point a local marketplace at the working tree:

```
/plugin marketplace add <path-to-your-clone>
/plugin install bitwarden-testing-tools@ai-plugins
```

Reinstall (uninstall then install) after every edit to the skill.

```bash
python3 run_real_eval.py \
  --eval-set trigger-eval.json \
  --runs-per-query 7 \
  --num-workers 5 \
  --timeout 90 \
  --model claude-opus-4-8 \
  > result.json
```

Keep `--num-workers` at 5 or below. The should-not-trigger queries are adversarial real-work prompts and each worker is a full agent.

For the agent suite, run once per agent name at `--runs-per-query 3`. Three runs are enough here because the expectation is zero triggers, and a zero-versus-nonzero signal does not need seven samples to establish:

```bash
for a in context-gatherer code-explorer service-mapper test-planner service-manager test-runner; do
  python3 run_agent_eval.py --agent "$a" --eval-set agent-non-trigger-eval.json \
    --runs-per-query 3 --num-workers 5 --timeout 90 --model claude-opus-4-8 \
    > "/tmp/agent-$a.json"
done
```

## Regression check

The orchestrator trigger suite has no committed baseline. When editing the skill's `description`, run the trigger eval once before the edit and once after, in the same session so the model and installed inventory match, and diff the two by PASS/FAIL verdict rather than the raw `trigger_rate` values, which are stochastic:

```bash
project='{
  should_trigger_pass, should_not_trigger_pass,
  results: [.results[] | {query, should_trigger, pass: ((.trigger_rate >= 0.5) == .should_trigger)}]
}'
diff <(jq -S "$project" before.json) <(jq -S "$project" after.json)
```

An empty diff means the edit changed no verdict. Fix the skill description rather than the eval set if an edit regresses a verdict, and update the orchestrator reading above. The agent non-trigger suite still carries its committed `agent-non-trigger-baseline.json`.
