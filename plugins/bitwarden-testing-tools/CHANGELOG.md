# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2026-08-24

### Added

- `start-playwright-test`, the pipeline entry point and the only orchestration skill. It accepts a Jira ticket id, a Jira browse URL, an implementation plan path, or a feature description, optionally followed by extra guidance, plus a `--confirm` flag that pauses for test-plan approval before execution. It runs an eight-task pipeline, dispatching six agents and persisting each response verbatim to `.playwright-testing-artifacts/<slug>/`, then renders an HTML report. Tasks 3 and 4 are dispatched together and run concurrently.
- Trigger evals for `start-playwright-test`, a 20-query set covering all three input types, the `--confirm` review gate, and near-misses against `assessing-test-coverage` and the separate `qa-testing-notes` skill. Kept as an on-demand diagnostic with no committed baseline; the last observed reading is recorded as dated prose in the eval README.
- A shared agent non-trigger suite, six queries covering the "do not invoke directly" convention that all six pipeline agents' descriptions carry. Kept as an on-demand diagnostic with no committed baseline; the last observed reading is recorded as dated prose in the eval README.
- Untrusted-source trust boundary for the web test pipeline: the orchestrator generates a per-run fence token, wraps raw feature source in verified `UNTRUSTED-SOURCE-<nonce>` markers, and prepends a single guardrail to every agent dispatch; each agent carries a one-line backstop, and a `validate-guardrail.sh` check (run in `pnpm lint`) prevents drift.

### Changed

- The plugin README now describes two families of tooling: standalone analysis skills, and the web test pipeline whose components are composed rather than invoked.
- `scripts/eval_harness.py` counts an `Agent` tool_use as real work alongside `Bash` and `Task`, so the agent non-trigger suite observes a direct agent dispatch.

## [1.5.0] - 2026-08-24

### Added

- `checking-localhost-web-health`, verifying Docker dev containers via preflight, application services via the health-check script, and the Angular bootstrap via render verification, halting on the first failure. It only verifies and never starts, builds, or stops services.
- Behavior evals for `checking-localhost-web-health`, four refusal-graded cases covering halting on the first failure, the verify-only boundary against starting services, render verification as a gate distinct from the `/alive` check, and refusing to improvise around a missing `playwright-cli` dependency. The suite is kept as an authoring aid and has not been benchmarked.
- `running-playwright-tests`, executing test cases through the `playwright-cli` skill with the tool policy applied throughout, plus screenshot naming, transient-toast capture, and setup-step handling. Emits a results object per segment as `complete`, `paused`, or `aborted`. Reads the admin recipient through `read_admin_email.py`, which parses the JSONC dev secrets file.
- Behavior evals for `running-playwright-tests`, six refusal-graded cases covering off-origin navigation, network requests in eval payloads, the mailcatcher exit 1 versus exit 3 distinction, carrying completed cases through an abort, browser-based verification, and segment schema conformance. The suite is kept as an authoring aid and has not been benchmarked.
- `compiling-playwright-report`, holding the deterministic report scripts `merge_results.py` and `render_report.py`, the report templates, the JSON results-schema reference with its golden examples, and its 32 unit tests.
- `external_trigger.py`, the Category 3 wrapper. It restricts destinations to `localhost`, `127.0.0.1`, `::1`, and `bitwarden.test` by default, extensible only additively through `PLAYWRIGHT_TESTING_ALLOWED_HOSTS`, enforces POST-only, and bypasses TLS verification solely for the four built-in dev hosts.
- Two execution-phase agents: `localhost-web-health-checker`, which gates the run on environment health, and `playwright-test-runner`, which executes the plan and returns the segment results JSON.
- Category 3 execution content and Category 1 execution constraints in `references/playwright-tool-policy.md`: the `external_trigger.py` registry entry with its POST-only, allowed-hosts, and TLS rules, and the `eval` and `run-code` no-network rule. Plus a known-limits note recording that these Category 1 constraints and the agent script grants are agent instructions rather than platform-enforced boundaries, pending a `PreToolUse` hook.

## [1.4.0] - 2026-08-24

### Added

- `writing-playwright-test-cases`, building structured Playwright test cases from plan context with starting URLs, interaction sequences, and screenshot checkpoints. Every generated step must fall into one of the tool policy's four categories, and external-trigger steps carry an explicit label so they are visible to whoever approves the plan.
- `playwright-test-case-writer`, the planning-phase agent that reads the context and Application Context artifacts and returns test cases for the orchestrator to persist.
- Category 3 (external trigger simulation) planning content in `references/playwright-tool-policy.md`: the qualifying test, the examples, and the `EXTERNAL TRIGGER` labeling rule.
- Behavior evals for `writing-playwright-test-cases`, six advice-only cases covering external-trigger labeling in the exact `EXTERNAL TRIGGER:` format, the Category 3 qualifying test, web-first setup from scratch, the billing test card, preserving a `[HUMAN]` marker from an unreachable state's recipe, and refusing out-of-category steps. The suite is kept as an authoring aid and has not been benchmarked.

## [1.3.0] - 2026-09-03

### Added

- `references/playwright-tool-policy.md`, the shared tool boundary for the web test pipeline. It frames the four categories of permitted step (web UI via `playwright-cli`, Mailcatcher email reading, external trigger simulation, and read-only Stripe queries), lists the canonical script paths, and states the never-permitted operations and the stop condition. Category 2 and Category 4 point to the `reading-mailcatcher-api` and `using-stripe-cli` skills that own them.
- `scoping-playwright-application-context`, exploring the clients and server repositories to build a state-centric Application Context with a `## States` section of real-user-reachable UI conditions and their verification points, and a `## Flows` section of the sequences that transition between them.
- `mapping-services-under-test`, resolving the union of route-based and file-path-based service dependencies from the Application Context and the branch diff, returning service names with URLs and ports.
- Three planning-phase agents, each independently invocable and each returning its artifact as its markdown response: `playwright-test-context-gatherer`, which acquires the feature source; `playwright-application-context-scoper`, which produces the Application Context; and `services-under-test-mapper`, which produces the service list.
- The `playwright-test-context-gatherer` agent carries an untrusted-source guardrail: content read from Jira, Confluence, or any linked source is treated as data, never instructions, and embedded directives are reported rather than obeyed. The `playwright-application-context-scoper` and `services-under-test-mapper` agents carry the same guardrail, scoped to the `## Source Summary` block they read from the context artifact.
- Behavior evals for `scoping-playwright-application-context`, five advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.
- Behavior evals for `mapping-services-under-test`, four advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.

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
