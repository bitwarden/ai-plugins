# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-10-07

### Added

- `references/playwright-tool-policy.md`, the shared tool boundary for the web test pipeline. It frames the four categories of permitted step (web UI via `playwright-cli`, Mailcatcher email reading, external trigger simulation, and read-only Stripe queries), lists the canonical script paths, and states the never-permitted operations and the stop condition. Category 2 and Category 4 point to the `reading-mailcatcher-api` and `using-stripe-cli` skills that own them.
- `scoping-playwright-test-cases`, exploring the clients and server repositories to build a state-centric Application Context with a `## States` section of real-user-reachable UI conditions and their verification points, and a `## Flows` section of the sequences that transition between them.
- `mapping-services-under-test`, resolving the union of route-based and file-path-based service dependencies from the Application Context and the branch diff, returning service names with URLs and ports.
- Three planning-phase agents: `playwright-test-context-gatherer`, which acquires the feature source; `playwright-test-case-scoper`, which produces the Application Context; and `services-under-test-mapper`, which produces the service list. Each returns its artifact as its response for the orchestrator to persist.
- The `playwright-test-context-gatherer` agent carries an untrusted-source guardrail: content read from Jira, Confluence, or any linked source is treated as data, never instructions, and embedded directives are reported rather than obeyed. The `playwright-test-case-scoper` and `services-under-test-mapper` agents carry the same guardrail, scoped to the `## Source Summary` block they read from the context artifact.
- Behavior evals for `scoping-playwright-test-cases`, five advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.
- Behavior evals for `mapping-services-under-test`, four advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.

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
