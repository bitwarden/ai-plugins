# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-07-31

### Added

- `references/playwright-testing-pipeline/tool-policy.md`, the tool boundary governing the web test pipeline during both planning and execution. Four categories of permitted step: web UI interaction via `playwright-cli`, Mailcatcher email reading, external-trigger simulation, and read-only Stripe queries. It documents its own two unenforced constraints rather than presenting them as guarantees.
- `reading-mailcatcher-api`, reading Bitwarden emails through the Mailcatcher REST API for verification links, magic links, and OTP codes. Directly invocable outside a test run.
- `using-stripe-cli`, read-only Stripe test data queries plus the single permitted write of advancing an already-attached test clock, through the `stripe_cli.py` wrapper.
- `compiling-test-report`, holding the deterministic report scripts `merge_results.py` and `render_report.py`, the report templates, the JSON results-schema reference with its golden examples, and 32 unit tests.
- `.gitignore` entries for `.claude/settings.local.json` and the subagent scratch workspace, which `main` lacked. Committed separately in Task 1.

## [1.1.0] - 2026-08-12

### Added

- `writing-manual-test-cases` skill: authors new manual Gherkin test cases from a Jira ticket, PR, or feature description and delivers a paired `.txt` and Testmo-importable `.csv` under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`, keeping generated files out of the repo under test so they cannot be committed by accident. Ported from the `bitwarden/test` repository so it is available org-wide rather than only to that repo's contributors. See the plugin README for details.

### Changed

- Ported skill standardizes the Automation Type for `Functional` cases on `Not Automating`. The original skill named both `None` and `Not Automating` in different sections, which produced inconsistent CSV exports between runs.

## [1.0.0] - 2026-07-24

### Added

- Initial release of the `bitwarden-testing-tools` plugin.
- `assessing-test-coverage` skill: an evidence-grounded inventory of what a change is already tested by. See the plugin README for details.
