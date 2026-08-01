# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-10-07

### Added

- `references/playwright-testing-pipeline/tool-policy.md`, the tool boundary governing the web test pipeline during both planning and execution. Four categories of permitted step: web UI interaction via `playwright-cli`, Mailcatcher email reading, external-trigger simulation, and read-only Stripe queries. It documents its own two unenforced constraints rather than presenting them as guarantees.
- `reading-mailcatcher-api`, reading Bitwarden emails through the Mailcatcher REST API for verification links, magic links, and OTP codes. Directly invocable outside a test run.
- `using-stripe-cli`, read-only Stripe test data queries plus the single permitted write of advancing an already-attached test clock, through the `stripe_cli.py` wrapper.
- `compiling-test-report`, holding the deterministic report scripts `merge_results.py` and `render_report.py`, the report templates, the JSON results-schema reference with its golden examples, and 32 unit tests.
- `.gitignore` entries for `.claude/settings.local.json` and the subagent scratch workspace, which `main` lacked. Committed separately in Task 1.
- `scripts/eval_harness.py`, a shared trigger-eval runner at the plugin level, with unit tests. Per-skill eval scripts are now thin configuration over it rather than near-identical copies of a 200-line runner.
- Trigger evals for `reading-mailcatcher-api`, 20 queries with a recorded baseline.

### Changed

- `assessing-test-coverage`'s eval runner is now a thin wrapper over `scripts/eval_harness.py`. The CLI contract and the output JSON schema are unchanged, and behavior preservation was verified by source-level comparison: `run_query`, `runs_for`, and `main` are identical to the previous standalone runner once the four policy constants are read from an `EvalConfig` instead of module globals. The committed `baseline.json` was deliberately not used as the control here, because this plugin's skill inventory changed in the same release and a trigger-eval baseline is only meaningful against the inventory it was recorded on. All trigger baselines are re-recorded against the final inventory before this stack completes.

## [1.2.0] - 2026-09-14

### Added

- `recommending-test-layers` skill: a forward-looking counterpart to `assessing-test-coverage`. From a Jira key, Testmo CSV, an `assessing-test-coverage` report, a PR, or a feature description, it recommends which tests a change needs and at which layer each belongs, following minimumCD's testing model, and writes a markdown recommendation report under `${CLAUDE_PLUGIN_DATA}/recommending-test-layers/`. Its trigger-eval set runs on the shared harness, and its description is scoped so it does not cannibalize the sibling `assessing-test-coverage` skill's triggers; passes 10/10 should-trigger and 10/10 should-not-trigger on `claude-opus-4-8`. See the plugin README for details.

### Changed

- Replaced `assessing-test-coverage`'s bespoke eval runner with a single shared engine at `evals/run_real_eval.py` and a shared `evals/README.md`. Each skill's `evals/` directory now holds only its data (`trigger-eval.json` and `baseline.json`), so adding evals for a new skill no longer copies the engine. The runner records its model in the summary's `model` field and defaults to `claude-opus-4-8`, so the regression check fails a baseline recorded on a different model. Re-recorded `assessing-test-coverage`'s baseline on `claude-opus-4-8` (10/10 should-trigger, 10/10 should-not-trigger).

## [1.1.0] - 2026-08-12

### Added

- `writing-manual-test-cases` skill: authors new manual Gherkin test cases from a Jira ticket, PR, or feature description and delivers a paired `.txt` and Testmo-importable `.csv` under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`, keeping generated files out of the repo under test so they cannot be committed by accident. Ported from the `bitwarden/test` repository so it is available org-wide rather than only to that repo's contributors. See the plugin README for details.

### Changed

- Ported skill standardizes the Automation Type for `Functional` cases on `Not Automating`. The original skill named both `None` and `Not Automating` in different sections, which produced inconsistent CSV exports between runs.

## [1.0.0] - 2026-07-24

### Added

- Initial release of the `bitwarden-testing-tools` plugin.
- `assessing-test-coverage` skill: an evidence-grounded inventory of what a change is already tested by. See the plugin README for details.
