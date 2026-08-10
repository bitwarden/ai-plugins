# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-07-31

### Added

- `verifying-environment-health`, verifying Docker dev containers via preflight, application services via the health-check script, and the Angular bootstrap via render verification, halting on the first failure. It only verifies and never starts, builds, or stops services.
- Behavior evals for `verifying-environment-health`, four refusal-graded cases covering halting on the first failure, the verify-only boundary against starting services, render verification as a gate distinct from the `/alive` check, and refusing to improvise around a missing `playwright-cli` dependency. The with-skill versus without-skill baseline is recorded in a later pass.
- `executing-web-tests`, executing test cases through the `playwright-cli` skill with the tool policy applied throughout, plus screenshot naming, transient-toast capture, and setup-step handling. Emits a results object per segment as `complete`, `paused`, or `aborted`.
- Behavior evals for `executing-web-tests`, six refusal-graded cases covering off-origin navigation, network requests in eval payloads, the mailcatcher exit 1 versus exit 3 distinction, carrying completed cases through an abort, browser-based verification, and segment schema conformance. The with-skill versus without-skill baseline is recorded in a later pass.
- Two execution-phase agents: `service-manager`, which gates the run on environment health, and `test-runner`, which executes the plan and returns the segment results JSON.
- `external_trigger.py`, the Category 3 wrapper. It restricts destinations to `localhost`, `127.0.0.1`, `::1`, and `bitwarden.test` by default, extensible only additively through `PLAYWRIGHT_TESTING_ALLOWED_HOSTS`, enforces POST-only, and bypasses TLS verification solely for the four built-in dev hosts. This resolves the forward reference the tool policy has carried since 1.2.0.

### Changed

- `executing-web-tests` now reads the tool policy from `references/playwright-testing-pipeline/tool-policy.md`.

### Fixed

- `read_admin_email.py` now reads the real JSONC dev secrets file: string-aware `//` and `/* */` comment stripping, `adminSettings.admins` resolution with a top-level fallback, and comma-separated string values. Tests rewritten to the real file's shape.

## [1.4.0] - 2026-07-31

### Added

- `writing-playwright-test-cases`, building structured Playwright test cases from plan context with starting URLs, interaction sequences, and screenshot checkpoints. Every generated step must fall into one of the tool policy's four categories, and external-trigger steps carry an explicit label so they are visible to whoever approves the plan.
- `playwright-test-case-writer`, the planning-phase agent that reads the context and Application Context artifacts and returns test cases for the orchestrator to persist.
- Behavior evals for `writing-playwright-test-cases`, six advice-only cases covering external-trigger labeling in the exact `EXTERNAL TRIGGER:` format, the Category 3 qualifying test, web-first setup from scratch, the billing test card, preserving a `[HUMAN]` marker from an unreachable state's recipe, and refusing out-of-category steps. The with-skill versus without-skill baseline is recorded in a later pass.

### Changed

- `writing-playwright-test-cases` now reads the tool policy from `references/playwright-testing-pipeline/tool-policy.md`.

## [1.3.0] - 2026-07-31

### Added

- `scoping-playwright-test-cases`, exploring the clients and server repositories to build a state-centric Application Context with a `## States` section of real-user-reachable UI conditions and their verification points, and a `## Flows` section of the sequences that transition between them.
- `mapping-services-under-test`, resolving the union of route-based and file-path-based service dependencies from the Application Context and the branch diff, returning service names with URLs and ports.
- Three planning-phase agents: `playwright-test-context-gatherer`, which acquires the feature source; `playwright-test-case-scoper`, which produces the Application Context; and `services-under-test-mapper`, which produces the service list. Each returns its artifact as its response for the orchestrator to persist.
- Behavior evals for `scoping-playwright-test-cases`, five advice-only cases. The with-skill versus without-skill baseline is recorded in a later pass.
- Behavior evals for `mapping-services-under-test`, four advice-only cases. The with-skill versus without-skill baseline is recorded in a later pass.

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
