# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-09-22

### Added

- `references/playwright-tool-policy.md`, the shared tool boundary for the web test pipeline. It frames the four categories of permitted step (web UI via `playwright-cli`, Mailcatcher email reading, external trigger simulation, and read-only Stripe queries), lists the canonical script paths, and states the never-permitted operations and the stop condition. Category 2 and Category 4 point to the `reading-mailcatcher-api` and `using-stripe-cli` skills that own them.
- `scoping-playwright-application-context`, exploring the clients and server repositories to build a state-centric Application Context with a `## States` section of real-user-reachable UI conditions and their verification points, and a `## Flows` section of the sequences that transition between them. It draws on curated, per-domain catalogs of reusable states and flows under `references/known-flows/` (`auth.md`, `billing.md`, `admin.md`), copied through rather than re-derived per run.
- `mapping-services-under-test`, resolving the union of route-based and file-path-based service dependencies from the Application Context and the branch diff, returning service names with URLs and ports.
- `scripts/repo-diff.sh`, a small wrapper the scoping and mapping skills call to list a repo's changed files (`git diff --name-only origin/main...HEAD`), so the skills' `allowed-tools` Bash grant is scoped to the script rather than to `git`.
- Three planning-phase agents, each independently invocable and each returning its artifact as its markdown response: `playwright-test-context-gatherer`, which acquires the feature source; `playwright-application-context-scoper`, which produces the Application Context; and `services-under-test-mapper`, which produces the service list.
- The three planning-phase agents carry an untrusted-source guardrail: each treats the feature source it reads as data, never instructions, and never lets an embedded directive change its behavior or survive into the artifact it produces. The rules live in a shared `references/untrusted-source-policy.md`, referenced by each agent and by the scoping and mapping skills, so the guardrail holds whether an agent is invoked directly or chained together with the others. The context gatherer distills the raw feature source into its structured sections and discards it: the raw source is never reproduced into an artifact or passed downstream, so no untrusted verbatim content flows through the pipeline.
- Behavior evals for `scoping-playwright-application-context`, eight advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.
- Behavior evals for `mapping-services-under-test`, five advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.

## [1.2.0] - 2026-08-31

### Added

- `reading-mailcatcher-api`, reading Bitwarden emails through the Mailcatcher REST API for verification links, magic links, and tokens, directly invocable outside a test run. Includes a trigger eval recorded as an on-demand prose reading.
- `using-stripe-cli`, read-only Stripe test-mode data queries plus the single permitted write of advancing an already-attached test clock, through the `stripe_cli.py` wrapper. Includes a trigger eval and advice-only behavior evals, both recorded as on-demand prose readings.
- `scripts/eval_harness.py`, a shared trigger-eval runner that per-skill eval scripts configure rather than copy.

## [1.1.0] - 2026-08-12

### Added

- `writing-manual-test-cases` skill: authors new manual Gherkin test cases from a Jira ticket, PR, or feature description and delivers a paired `.txt` and Testmo-importable `.csv` under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`, keeping generated files out of the repo under test so they cannot be committed by accident. Ported from the `bitwarden/test` repository so it is available org-wide rather than only to that repo's contributors. See the plugin README for details.

### Changed

- Ported skill standardizes the Automation Type for `Functional` cases on `Not Automating`. The original skill named both `None` and `Not Automating` in different sections, which produced inconsistent CSV exports between runs.

## [1.0.0] - 2026-07-24

### Added

- Initial release of the `bitwarden-testing-tools` plugin.
- `assessing-test-coverage` skill: an evidence-grounded inventory of what a change is already tested by. See the plugin README for details.
