# creating-jira-tickets evals

Behavior test cases for the `creating-jira-tickets` skill, in the `skill-creator` schema.

`evals.json` holds seven cases guarding the skill's load-bearing decisions: acli auth preflight, refusing to write through the read-only MCP, refusing to batch-create, rewriting a decomposition label into a real title, the Gherkin "Acceptance criteria" ADF section, the inverted `--in`/`--out` link direction, and asking about a missing epic. Each prompt embeds an inline `tasks.md` fixture with placeholder keys, so cases stay hermetic.

Cases are **advice-only** — every prompt asks for the plan, so no case creates or links a live ticket; the benchmark is mutation-safe.

Run with `/skill-creator:skill-creator` in Benchmark mode (with-skill vs. without-skill), several runs per config with a config-blind grader. A case gains a `notes` field once an ablation records an outcome.

`trigger-eval.json` is a separate 10/10 should-trigger / should-not set; run it with the sibling `../creating-pull-request/evals/run_real_eval.py` after setting its `TARGET_SKILL_TOKEN` to `creating-jira-tickets`.
