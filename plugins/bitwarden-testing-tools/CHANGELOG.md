# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-07-31

### Added

- `exploring-application-context`, exploring the clients and server repositories to build a state-centric Application Context with a `## States` section of real-user-reachable UI conditions and their verification points, and a `## Flows` section of the sequences that transition between them.
- `determining-required-services`, resolving the union of route-based and file-path-based service dependencies from the Application Context and the branch diff, returning service names with URLs and ports.
- Three planning-phase agents: `context-gatherer`, which acquires the feature source; `code-explorer`, which produces the Application Context; and `service-mapper`, which produces the service list. Each returns its artifact as its response for the orchestrator to persist.

## [1.2.0] - 2026-07-31

### Added

- `references/playwright-testing-pipeline/tool-policy.md`, the tool boundary governing the web test pipeline during both planning and execution. Four categories of permitted step: web UI interaction via `playwright-cli`, Mailcatcher email reading, external-trigger simulation, and read-only Stripe queries. It documents its own two unenforced constraints rather than presenting them as guarantees.
- `reading-mailcatcher-api`, reading Bitwarden emails through the Mailcatcher REST API for verification links, magic links, and OTP codes. Directly invocable outside a test run.
- `using-stripe-cli`, read-only Stripe test data queries plus the single permitted write of advancing an already-attached test clock, through the `stripe_cli.py` wrapper.
- `.gitignore` entries for `.claude/settings.local.json` and the subagent scratch workspace, which `main` lacked. Committed separately in Task 1.
- `scripts/eval_harness.py`, a shared trigger-eval runner at the plugin level, with unit tests. Per-skill eval scripts are now thin configuration over it rather than near-identical copies of a 200-line runner.
- Trigger evals for `reading-mailcatcher-api`, 20 queries with a recorded baseline.
- Behavior evals for `using-stripe-cli`, seven advice-only cases. The with-skill versus without-skill baseline is recorded in a later pass.

### Changed

- `assessing-test-coverage`'s eval runner is now a thin wrapper over `scripts/eval_harness.py`. The CLI contract and the output JSON schema are unchanged, and behavior preservation was verified by source-level comparison: `run_query`, `runs_for`, and `main` are identical to the previous standalone runner once the four policy constants are read from an `EvalConfig` instead of module globals. The committed `baseline.json` was deliberately not used as the control here, because this plugin's skill inventory changed in the same release and a trigger-eval baseline is only meaningful against the inventory it was recorded on. All trigger baselines are re-recorded against the final inventory before this stack completes.

### Fixed

- Corrected a stale `references/tool-policy.md` path in `using-stripe-cli/scripts/stripe_cli.py`. The policy moved to `references/playwright-testing-pipeline/tool-policy.md` in this same release, and this docstring reference was missed because the original survey for it excluded non-markdown files.
- `scripts/eval_harness.py` now detects a direct agent dispatch. It counts a trigger on an `Agent` or legacy `Task` tool_use whose `subagent_type` contains the target token, and its `Read` branch now accepts an `AGENT.md` path as well as `SKILL.md`. Before this, an agent dispatch fell through to the `exec_tools` bail and was recorded as a non-trigger, so the agent non-trigger suite could not fail. The change is inert for the skill trigger suites and is locked by new cases in `scripts/tests/test_eval_harness.py`.

## [1.1.0] - 2026-08-12

### Added

- `writing-manual-test-cases` skill: authors new manual Gherkin test cases from a Jira ticket, PR, or feature description and delivers a paired `.txt` and Testmo-importable `.csv` under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`, keeping generated files out of the repo under test so they cannot be committed by accident. Ported from the `bitwarden/test` repository so it is available org-wide rather than only to that repo's contributors. See the plugin README for details.

### Changed

- Ported skill standardizes the Automation Type for `Functional` cases on `Not Automating`. The original skill named both `None` and `Not Automating` in different sections, which produced inconsistent CSV exports between runs.

## [1.0.0] - 2026-07-24

### Added

- Initial release of the `bitwarden-testing-tools` plugin.
- `assessing-test-coverage` skill: an evidence-grounded inventory of what a change is already tested by. See the plugin README for details.
