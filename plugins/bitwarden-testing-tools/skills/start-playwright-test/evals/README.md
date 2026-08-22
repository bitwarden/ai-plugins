# start-playwright-test evals

Two suites for the `bitwarden-testing-tools:start-playwright-test` orchestrator and the six agents it dispatches.

## `trigger-eval.json`

20-query trigger-rate set for the orchestrator. 10 should-trigger phrasings covering all three input types (Jira key, Jira browse URL, plan file path, and free-form description), the `--confirm` review gate, and extra-guidance phrasings. 10 should-not-trigger near-misses that share the vocabulary but want something else: a backward-looking coverage inventory (which belongs to `assessing-test-coverage`), authoring a committed spec file, debugging a flaky test, starting the dev environment, test-layer strategy advice, PR review, test-pyramid explanation, running the existing jest suite, fixing a broken build, and writing manual QA notes.

Two of those near-misses deliberately target sibling tooling. `assessing-test-coverage` now lives in this same plugin, and `qa-testing-notes` is a separate skill, so proving no cross-fire is part of the set's job.

## `agent-non-trigger-eval.json`

6 queries, all `should_trigger: false`, testing a claim every one of the six agent descriptions makes: "Do not invoke directly; dispatched by the `start-playwright-test` skill." Each query is phrased to tempt one specific agent with exactly the work it does, without naming any agent, so a trigger means the model reached for an internal agent on its own.

Run `run_agent_eval.py --agent <name>` once per agent. A pass is zero triggers across all six queries for all six agents.

## What this suite measures

The harness counts a trigger three ways: a `Skill` tool_use whose `input.skill` contains the target token, a `Read` whose `file_path` contains the token and ends in `SKILL.md` or `AGENT.md`, or an `Agent` (or legacy `Task`) tool_use whose `subagent_type` contains the target token. `run_agent_eval.py` passes an agent name as that token, so a direct dispatch of the named agent, or the model reading that agent's `AGENT.md`, registers as a trigger. This suite is a real measurement of the "do not invoke directly" convention.

One residual caveat: direct-dispatch detection depends on the CLI surfacing a dispatch as an `Agent`/`Task` tool_use carrying `subagent_type`. If a future CLI changes that event shape, this branch needs revisiting.

## Baseline provenance

These readings were recorded against the final, ten-skill plugin inventory (each reading below notes its own run date):

- `assessing-test-coverage`
- `writing-playwright-test-cases`
- `compiling-playwright-report`
- `mapping-services-under-test`
- `running-playwright-tests`
- `scoping-playwright-test-cases`
- `reading-mailcatcher-api`
- `start-playwright-test`
- `using-stripe-cli`
- `checking-localhost-web-health`

plus all six agents (`playwright-test-context-gatherer`, `playwright-test-case-scoper`, `services-under-test-mapper`, `playwright-test-case-writer`, `localhost-web-health-checker`, `playwright-test-runner`). A trigger eval measures whether the model auto-selects a skill or agent from a natural-language query among everything installed alongside it, so the recorded numbers are only meaningful against this exact inventory.

### Orchestrator trigger suite: last observed reading

On-demand diagnostic, not a committed regression control. Last run 2026-08-01, model `claude-opus-4-8`, against the ten-skill inventory and six agents named above: should_trigger 10/10, should_not_trigger 10/10 at `--runs-per-query 7`, with no query in the 0.35-0.65 band. These numbers predate the addition of `Agent` to `scripts/eval_harness.py`'s `exec_tools` set, so the should_trigger figure is a ceiling and the should_not_trigger figure is a floor. There is no committed `baseline.json` for the orchestrator trigger suite: the query set and shared harness are kept and re-run on demand when editing the skill's description. This diverges deliberately from skill-creator's baseline-oriented methodology, which assumes the description can be tuned in response to the number; do not restore a committed baseline here.

### Agent suite result: last observed reading

On-demand diagnostic, not a committed regression control. Last run 2026-08-10, model `claude-opus-4-8`, six queries per agent at `--runs-per-query 3`, against the ten-skill inventory and six agents named above. This is the first real measurement of the "do not invoke directly" convention: the harness now detects a direct agent dispatch, so a `should_not_trigger` pass is evidence the model did not reach for the agent on its own.

should_not_trigger result per agent:

- playwright-test-context-gatherer: 6/6
- playwright-test-case-scoper: 6/6
- services-under-test-mapper: 6/6
- playwright-test-case-writer: 6/6
- localhost-web-health-checker: 6/6
- playwright-test-runner: 6/6

No agent triggered on any of the six work requests; the convention held across the suite.

The earlier committed reading of `should_not_trigger_pass=8/8` for all six agents is retired: it was an artifact of a harness that could not observe a direct agent dispatch, not measured evidence. There is no committed `agent-non-trigger-baseline.json` for this suite. A trigger rate depends on the agent set, the harness, the model, and the full installed skill inventory competing for selection, and most of those are outside any one agent, so a committed baseline would go stale for reasons unrelated to the agents. The query set and shared harness are kept and re-run on demand when an agent's behavior or description changes. This diverges deliberately from skill-creator's baseline-oriented methodology; do not restore a committed baseline here.

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

For the agent suite, run once per agent name at `--runs-per-query 3`. Three runs are enough here because the expectation is zero triggers, and a zero-versus-nonzero signal does not need seven samples to establish. Install from a local marketplace pointing at the worktree checkout (`/Users/kyle/code/bitwarden/worktrees/testing-tools`), not the `ai-plugins` checkout, which is on the frozen source branch and holds a differently named plugin; reinstall after any harness edit so the run measures the current harness:

```bash
for a in playwright-test-context-gatherer playwright-test-case-scoper services-under-test-mapper playwright-test-case-writer localhost-web-health-checker playwright-test-runner; do
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

An empty diff means the edit changed no verdict. Fix the skill description rather than the eval set if an edit regresses a verdict, and update the orchestrator reading above. The agent non-trigger suite has no committed baseline either: re-run it on demand with the per-agent loop above and update the agent reading when an agent's behavior or description changes.
