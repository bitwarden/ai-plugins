# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2026-08-01

### Added

- `start-playwright-test`, the pipeline entry point and the only orchestration skill. It accepts a Jira ticket id, a Jira browse URL, an implementation plan path, or a feature description, optionally followed by extra guidance, plus a `--confirm` flag that pauses for test-plan approval before execution. It runs an eight-task pipeline, dispatching six agents and persisting each response verbatim to `.playwright-testing-artifacts/<slug>/`, then renders an HTML report. Tasks 3 and 4 are dispatched together and run concurrently.
- Trigger evals for `start-playwright-test`, a 20-query set covering all three input types, the `--confirm` review gate, and near-misses against `assessing-test-coverage` and the separate `qa-testing-notes` skill. Kept as an on-demand diagnostic with no committed baseline; the last observed reading (`should_trigger_pass=10/10`, `should_not_trigger_pass=10/10`, no query in the flaky 0.35-0.65 band) is recorded as dated prose in the eval README.
- A shared agent non-trigger suite, eight queries targeting the "do not invoke directly" convention that all six pipeline agents' descriptions carry. Recorded `should_not_trigger_pass=8/8` for every one of the six agents, including the two queries that name an agent explicitly. This result is guaranteed by a gap in the harness's trigger detection (it cannot observe a direct agent dispatch at all) rather than measured evidence that the convention holds; see the suite's README for the known limitation and the follow-up needed to make it a real test.

### Changed

- The plugin README now describes two families of tooling: standalone analysis skills, and the web test pipeline whose components are composed rather than invoked.
- `assessing-test-coverage`'s trigger baseline was re-recorded against the final ten-skill inventory. `should_not_trigger_pass` moved from 10/10 to 7/10, because three near-miss queries began attracting the newly added sibling testing skills.
- `reading-mailcatcher-api`'s trigger set had a near-duplicate SMTP-configuration query replaced with a retry-policy query.
- Eval baseline policy: trigger baselines are no longer committed. The query sets and the shared harness are kept; each skill's eval README records its last observed reading as dated prose and is re-run on demand when its description changes. Behavior suites are kept as authoring aids and are not benchmarked. This diverges deliberately from skill-creator's baseline-oriented methodology; see the eval READMEs for the reasoning.

### Fixed

- The agent non-trigger suite is now a real measurement. It was trimmed from eight queries to six (the two that named an agent explicitly were removed), the harness fix in 1.2.0 lets it observe a direct agent dispatch, and its committed `agent-non-trigger-baseline.json` was deleted in favor of a dated prose reading in the eval README. The earlier `should_not_trigger_pass=8/8` was an artifact of the harness's detection gap, not measured evidence.

### Notes

- With this release the migration from the `bitwarden-playwright-testing` branch is complete. Of the 54 files in that branch, 51 landed as files in this plugin and 3 (the old README, CHANGELOG, and plugin.json) were absorbed into this plugin's own metadata; the migration harness reports `checked=51 skipped=3`. The migrated files preserve the original pipeline's tested behavior. 149 unit tests pass: 130 migrated plus 19 for the new shared eval harness.
- Two constraints in the tool policy remain agent instructions rather than platform boundaries: navigation targets and `eval` payloads under Category 1, and the agent script grants, which are leading-wildcard path suffixes not anchored to the install directory. A `PreToolUse` hook on `Bash` is the documented enforcement point for both and is not yet implemented.
- Six behavior-eval suites (`checking-localhost-web-health`, `running-playwright-tests`, `writing-playwright-test-cases`, `scoping-playwright-test-cases`, `mapping-services-under-test`, `using-stripe-cli`) ship with cases and READMEs and no committed baseline. They are kept as behavioral specifications and authoring aids and have not been benchmarked; see each suite's README.

## [1.5.0] - 2026-07-31

### Added

- `checking-localhost-web-health`, verifying Docker dev containers via preflight, application services via the health-check script, and the Angular bootstrap via render verification, halting on the first failure. It only verifies and never starts, builds, or stops services.
- Behavior evals for `checking-localhost-web-health`, four refusal-graded cases covering halting on the first failure, the verify-only boundary against starting services, render verification as a gate distinct from the `/alive` check, and refusing to improvise around a missing `playwright-cli` dependency. The suite is kept as an authoring aid and has not been benchmarked.
- `running-playwright-tests`, executing test cases through the `playwright-cli` skill with the tool policy applied throughout, plus screenshot naming, transient-toast capture, and setup-step handling. Emits a results object per segment as `complete`, `paused`, or `aborted`.
- Behavior evals for `running-playwright-tests`, six refusal-graded cases covering off-origin navigation, network requests in eval payloads, the mailcatcher exit 1 versus exit 3 distinction, carrying completed cases through an abort, browser-based verification, and segment schema conformance. The suite is kept as an authoring aid and has not been benchmarked.
- Two execution-phase agents: `localhost-web-health-checker`, which gates the run on environment health, and `playwright-test-runner`, which executes the plan and returns the segment results JSON.
- `external_trigger.py`, the Category 3 wrapper. It restricts destinations to `localhost`, `127.0.0.1`, `::1`, and `bitwarden.test` by default, extensible only additively through `PLAYWRIGHT_TESTING_ALLOWED_HOSTS`, enforces POST-only, and bypasses TLS verification solely for the four built-in dev hosts. This resolves the forward reference the tool policy has carried since 1.2.0.

### Changed

- `running-playwright-tests` now reads the tool policy from `references/playwright-testing-pipeline/tool-policy.md`.

### Fixed

- `read_admin_email.py` now reads the real JSONC dev secrets file: string-aware `//` and `/* */` comment stripping, `adminSettings.admins` resolution with a top-level fallback, and comma-separated string values. Tests rewritten to the real file's shape.

## [1.4.0] - 2026-07-31

### Added

- `writing-playwright-test-cases`, building structured Playwright test cases from plan context with starting URLs, interaction sequences, and screenshot checkpoints. Every generated step must fall into one of the tool policy's four categories, and external-trigger steps carry an explicit label so they are visible to whoever approves the plan.
- `playwright-test-case-writer`, the planning-phase agent that reads the context and Application Context artifacts and returns test cases for the orchestrator to persist.
- Behavior evals for `writing-playwright-test-cases`, six advice-only cases covering external-trigger labeling in the exact `EXTERNAL TRIGGER:` format, the Category 3 qualifying test, web-first setup from scratch, the billing test card, preserving a `[HUMAN]` marker from an unreachable state's recipe, and refusing out-of-category steps. The suite is kept as an authoring aid and has not been benchmarked.

### Changed

- `writing-playwright-test-cases` now reads the tool policy from `references/playwright-testing-pipeline/tool-policy.md`.

## [1.3.0] - 2026-07-31

### Added

- `scoping-playwright-test-cases`, exploring the clients and server repositories to build a state-centric Application Context with a `## States` section of real-user-reachable UI conditions and their verification points, and a `## Flows` section of the sequences that transition between them.
- `mapping-services-under-test`, resolving the union of route-based and file-path-based service dependencies from the Application Context and the branch diff, returning service names with URLs and ports.
- Three planning-phase agents: `playwright-test-context-gatherer`, which acquires the feature source; `playwright-test-case-scoper`, which produces the Application Context; and `services-under-test-mapper`, which produces the service list. Each returns its artifact as its response for the orchestrator to persist.
- Behavior evals for `scoping-playwright-test-cases`, five advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.
- Behavior evals for `mapping-services-under-test`, four advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.

## [1.2.0] - 2026-07-31

### Added

- `references/playwright-testing-pipeline/tool-policy.md`, the tool boundary governing the web test pipeline during both planning and execution. Four categories of permitted step: web UI interaction via `playwright-cli`, Mailcatcher email reading, external-trigger simulation, and read-only Stripe queries. It documents its own two unenforced constraints rather than presenting them as guarantees.
- `reading-mailcatcher-api`, reading Bitwarden emails through the Mailcatcher REST API for verification links, magic links, and OTP codes. Directly invocable outside a test run.
- `using-stripe-cli`, read-only Stripe test data queries plus the single permitted write of advancing an already-attached test clock, through the `stripe_cli.py` wrapper.
- `.gitignore` entries for `.claude/settings.local.json` and the subagent scratch workspace, which `main` lacked. Committed separately in Task 1.
- `scripts/eval_harness.py`, a shared trigger-eval runner at the plugin level, with unit tests. Per-skill eval scripts are now thin configuration over it rather than near-identical copies of a 200-line runner.
- Trigger evals for `reading-mailcatcher-api`, 20 queries. Kept as an on-demand diagnostic with no committed baseline; the last observed reading is recorded as dated prose in the eval README.
- Behavior evals for `using-stripe-cli`, seven advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.

### Changed

- `assessing-test-coverage`'s eval runner is now a thin wrapper over `scripts/eval_harness.py`. The CLI contract and the output JSON schema are unchanged, and behavior preservation was verified by source-level comparison: `run_query`, `runs_for`, and `main` are identical to the previous standalone runner once the four policy constants are read from an `EvalConfig` instead of module globals. The committed `baseline.json` was deliberately not used as the control here, because this plugin's skill inventory changed in the same release and a trigger-eval baseline is only meaningful against the inventory it was recorded on. Trigger baselines are no longer committed; each skill's eval README records its last observed reading as dated prose, run on demand (see the eval READMEs).

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
