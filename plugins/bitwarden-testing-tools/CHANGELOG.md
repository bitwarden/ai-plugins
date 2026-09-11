# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-09-11

### Added

- `recommending-test-layers` skill: a forward-looking counterpart to `assessing-test-coverage` that recommends which tests a change needs and at which layer each belongs, following minimumCD's testing model. From a Jira key, Testmo CSV, an `assessing-test-coverage` report, a PR, or a feature description, it places each behavior at its lowest sufficient deterministic layer (static, unit, component, contract) to form a fast, fully controlled pre-merge gate, then grades criticality against Bitwarden's Defect Severity Classification Guide fetched live from Confluence when reachable (marking criticality `unverified` and noting the missing guide when it is not, rather than stopping) to decide which critical journeys additionally earn a non-deterministic post-deploy layer (E2E, smoke, integration, synthetic monitoring, exploratory), and writes a markdown recommendation report under `${CLAUDE_PLUGIN_DATA}/recommending-test-layers/`. Ships an `evals/` trigger harness, kept in step with the `assessing-test-coverage` harness, so the two forward/backward coverage skills do not cannibalize each other's triggers. See the plugin README for details.

### Changed

- `assessing-test-coverage` eval harness brought in step with the new skill's harness: the read-only `gh`/`git` allowlist now guards its `gh api repos/` carve-out against write requests (any method or request-body flag bails, across spaced, joined, and `=`-attached spellings) and against process-substitution and redirection operators, and `baseline.json` was re-recorded on `claude-opus-4-8` at 7 runs/query, now persisting the run's `model`, `runs_per_query`, and `recorded_utc` plus per-query `timeouts` and `first_skills`.

## [1.1.0] - 2026-08-12

### Added

- `writing-manual-test-cases` skill: authors new manual Gherkin test cases from a Jira ticket, PR, or feature description and delivers a paired `.txt` and Testmo-importable `.csv` under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`, keeping generated files out of the repo under test so they cannot be committed by accident. Ported from the `bitwarden/test` repository so it is available org-wide rather than only to that repo's contributors. See the plugin README for details.

### Changed

- Ported skill standardizes the Automation Type for `Functional` cases on `Not Automating`. The original skill named both `None` and `Not Automating` in different sections, which produced inconsistent CSV exports between runs.

## [1.0.0] - 2026-07-24

### Added

- Initial release of the `bitwarden-testing-tools` plugin.
- `assessing-test-coverage` skill: an evidence-grounded inventory of what a change is already tested by. See the plugin README for details.
