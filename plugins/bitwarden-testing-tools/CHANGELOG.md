# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-08-24

### Added

- `checking-localhost-web-health`, verifying Docker dev containers via preflight, application services via the health-check script, and the Angular bootstrap via render verification, halting on the first failure. It only verifies and never starts, builds, or stops services.
- Behavior evals for `checking-localhost-web-health`, five refusal-graded cases covering halting on the first failure, the verify-only boundary against starting services, render verification as a gate distinct from the `/alive` check, refusing to improvise around a missing `playwright-cli` dependency, and surfacing a malformed or absent required-services list rather than health-checking a partial one. The suite is kept as an authoring aid and has not been benchmarked.
- `running-playwright-tests`, executing test cases through the `playwright-cli` skill with the tool policy applied throughout, plus screenshot naming, transient-toast capture, and setup-step handling. Emits a results object per segment as `complete`, `paused`, or `aborted`. Reads the admin recipient through `read_admin_email.py`, which parses the JSONC dev secrets file.
- Behavior evals for `running-playwright-tests`, seven refusal-graded cases covering off-origin navigation, network requests in eval payloads, the mailcatcher exit 1 versus exit 3 distinction, carrying completed cases through an abort, browser-based verification, segment schema conformance, and surfacing a malformed or absent test-cases input rather than executing a partial one. The suite is kept as an authoring aid and has not been benchmarked.
- `compiling-playwright-report`, holding the deterministic report scripts `merge_results.py` and `render_report.py`, the report templates, the JSON results-schema reference with its golden examples, and its 32 unit tests.
- `external_trigger.py`, the Category 3 wrapper. It restricts destinations to `localhost`, `127.0.0.1`, `::1`, and `bitwarden.test` by default, extensible only additively through `PLAYWRIGHT_TESTING_ALLOWED_HOSTS`, enforces POST-only, and bypasses TLS verification solely for the four built-in dev hosts.
- Two execution-phase agents: `localhost-web-health-checker`, which gates the run on environment health, and `playwright-test-runner`, which executes the plan and returns the segment results JSON. Both carry the untrusted-source guardrail from the shared `references/untrusted-source-policy.md`, so the test plan they read — and, for the runner, the runtime data it receives such as email bodies, rendered page content, and tool output — stays data, not instructions.
- Category 3 execution content and Category 1 execution constraints in `references/playwright-tool-policy.md`: the `external_trigger.py` registry entry with its POST-only, allowed-hosts, and TLS rules, and the `eval` and `run-code` no-network rule. Plus Category 1 and execution-agent entries in the tool policy's known-limits section, recording that these are agent instructions rather than platform-enforced boundaries, pending a `PreToolUse` hook.

## [1.4.0] - 2026-08-24

### Added

- `writing-playwright-test-cases`, building structured Playwright test cases from plan context with starting URLs, interaction sequences, and screenshot checkpoints. Every generated step must fall into one of the tool policy's four categories, and external-trigger steps carry an explicit label so they are visible to whoever approves the plan.
- `playwright-test-case-writer`, the planning-phase agent that reads the context and Application Context artifacts and returns test cases for the orchestrator to persist. It carries the same untrusted-source guardrail as the other planning-phase agents, from the shared `references/untrusted-source-policy.md`, and locates each artifact by the first-START/last-END of its fence so an embedded marker cannot truncate it.
- Category 3 (external trigger simulation) planning content in `references/playwright-tool-policy.md`: the qualifying test, the examples, and the `EXTERNAL TRIGGER` labeling rule.
- Behavior evals for `writing-playwright-test-cases`, seven advice-only cases covering external-trigger labeling in the exact `EXTERNAL TRIGGER:` format, the Category 3 qualifying test, web-first setup from scratch, the billing test card, preserving a `[HUMAN]` marker from an unreachable state's recipe, refusing out-of-category steps, and erroring when no Application Context is provided. The suite is kept as an authoring aid and has not been benchmarked.

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
