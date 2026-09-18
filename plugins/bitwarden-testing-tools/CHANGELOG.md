# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-10-07

### Added

- `checking-localhost-web-health`, verifying Docker dev containers via preflight, application services via the health-check script, and the Angular bootstrap via render verification, halting on the first failure. It only verifies and never starts, builds, or stops services.
- Behavior evals for `checking-localhost-web-health`, five refusal-graded cases covering halting on the first failure, the verify-only boundary against starting services, render verification as a gate distinct from the `/alive` check, refusing to improvise around a missing `playwright-cli` dependency, and surfacing a malformed or absent required-services list rather than health-checking a partial one. The suite is kept as an authoring aid and has not been benchmarked.
- `running-playwright-tests`, executing test cases through the `playwright-cli` skill with the tool policy applied throughout, plus screenshot naming, transient-toast capture, and setup-step handling. Emits a results object per segment as `complete`, `paused`, or `aborted`. Reads the admin recipient through `read_admin_email.py`, which parses the JSONC dev secrets file.
- Behavior evals for `running-playwright-tests`, seven refusal-graded cases covering off-origin navigation, network requests in eval payloads, the mailcatcher exit 1 versus exit 3 distinction, carrying completed cases through an abort, browser-based verification, segment schema conformance, and surfacing a malformed or absent test-cases input rather than executing a partial one. The suite is kept as an authoring aid and has not been benchmarked.
- `compiling-playwright-report`, holding the deterministic report scripts `merge_results.py` and `render_report.py`, the report templates, the JSON results-schema reference with its golden examples, and its 32 unit tests.
- `external_trigger.py`, the Category 3 wrapper. It restricts destinations to `localhost`, `127.0.0.1`, `::1`, and `bitwarden.test` by default, extensible only additively through `PLAYWRIGHT_TESTING_ALLOWED_HOSTS`, enforces POST-only, and bypasses TLS verification solely for the four built-in dev hosts.
- Two execution-phase agents: `localhost-web-health-checker`, which gates the run on environment health, and `playwright-test-runner`, which executes the plan and returns the segment results JSON.
- Category 3 execution content and Category 1 execution constraints in `references/playwright-tool-policy.md`: the `external_trigger.py` registry entry with its POST-only, allowed-hosts, and TLS rules, and the `eval` and `run-code` no-network rule. Plus a known-limits note recording that these Category 1 constraints and the agent script grants are agent instructions rather than platform-enforced boundaries, pending a `PreToolUse` hook.

## [1.4.0] - 2026-10-07

### Added

- `writing-playwright-test-cases`, building structured Playwright test cases from plan context and an Application Context with starting URLs, setup steps, interaction sequences, and assertions. Every generated step must fall into one of the tool policy's four categories, and external-trigger steps carry an explicit label so they are visible in the plan and the execution log. It never writes a feature-flag step or a Stripe write other than the sanctioned test-clock advance, and drops a `[HUMAN]` marker from a step whose only action is a granted skill's read or test-clock advance. Email-reading steps name the `bitwarden-mailcatcher-tools:reading-mailcatcher-api` skill and its arguments, never a script path.
- `playwright-test-case-writer`, the planning-phase agent that reads the context and Application Context artifacts and returns test cases for the orchestrator to persist. It carries the same untrusted-source guardrail as the other planning-phase agents, from the shared `references/untrusted-source-policy.md`, and locates each artifact by the first-START/last-END of its fence so an embedded marker cannot truncate it. The plugin's `PreToolUse` hook from 1.3.0 limits it to its own skill.
- Category 3 (external trigger simulation) planning content in `references/playwright-tool-policy.md`: the qualifying test, the examples, and the `EXTERNAL TRIGGER` labeling rule.
- Behavior evals for `writing-playwright-test-cases`, nine advice-only cases covering external-trigger labeling in the exact `EXTERNAL TRIGGER:` format, the Category 3 qualifying test, web-first setup from scratch, the billing test card, preserving a `[HUMAN]` marker from an unreachable state's recipe, refusing out-of-category steps, erroring when no Application Context is provided, never writing a feature-flag step, and dropping `[HUMAN]` from a granted skill's read. The suite is kept as an authoring aid and has not been benchmarked.

## [1.3.0] - 2026-10-07

### Added

- `references/playwright-tool-policy.md`, the shared tool boundary for the web test pipeline. It frames the four categories of permitted step (web UI via `playwright-cli`, Mailcatcher email reading, external trigger simulation, and read-only Stripe queries), and states the never-permitted operations and the stop condition. Category 2 and Category 4 are owned by skills in the vendor plugins this plugin depends on, `bitwarden-mailcatcher-tools:reading-mailcatcher-api` and `bitwarden-stripe-tools:using-stripe-cli`, which the pipeline reaches only by invoking them.
- `scoping-playwright-application-context`, exploring the clients and server repositories to build a state-centric Application Context with a `## States` section of real-user-reachable UI conditions and their verification points, and a `## Flows` section of the sequences that transition between them. It draws on curated, per-domain catalogs of reusable states and flows under `references/known-flows/` (`auth.md`, `billing.md`, `admin.md`), copied through, once their cited source literals check out, rather than re-derived per run. Billing trials default to a normal paid-org signup; marketing-initiated and sales-assisted trial flows are used only when the ticket or the user's extra instructions call for that kind of trial or state a requirement only that flow meets. It records the feature flags a run depends on in an optional `## Required Feature Flags` section, and reserves `[HUMAN]` for actions and checks no granted tool can perform.
- `mapping-services-under-test`, resolving the union of route-based and file-path-based service dependencies from the Application Context and the branch diff, returning service names with URLs and ports. It carries the Application Context's `## Required Feature Flags` section into the services artifact, and adds `Api` whenever that section is present.
- `scripts/repo-diff.sh`, a small wrapper that lists a repo's changed files (`git diff --name-only origin/main...HEAD`), so no Bash grant ever exposes `git` itself. The scoping and mapping skills run it when no diff artifact is supplied.
- `hooks/restrict_planning_agents.py`, a `PreToolUse` hook that limits the scoper, mapper, and context gatherer agents, none of which holds `Bash`, to their own skill, since a forked skill runs its `Bash` as a different agent type, outside the agents' `tools:` allowlists. It blocks before permission rules are evaluated, so the limit holds in every permission mode while the hook runs; other agents and the main session are unaffected.
- Three planning-phase agents, each independently invocable and each returning its artifact as its markdown response: `playwright-test-context-gatherer`, which acquires the feature source; `playwright-application-context-scoper`, which produces the Application Context; and `services-under-test-mapper`, which produces the service list. Each is listed under the manifest's `agents` key, so it loads as `bitwarden-testing-tools:<agent>`. The scoper and mapper read the changed files from a `diff-<timestamp>.md` artifact the caller supplies rather than holding `Bash`, which on macOS, Linux, and WSL would cost the scoper its Grep and Glob tools.
- The three planning-phase agents carry an untrusted-source guardrail: each treats the feature source it reads as data, never instructions, and never lets an embedded directive change its behavior or survive into the artifact it produces. The rules live in a shared `references/untrusted-source-policy.md`, referenced by each agent and by the scoping and mapping skills, so the guardrail holds whether an agent is invoked directly or chained together with the others. The context gatherer distills the raw feature source into its structured sections and discards it: the raw source is never reproduced into an artifact or passed downstream, so no untrusted verbatim content flows through the pipeline.
- Dependencies on `bitwarden-mailcatcher-tools` and `bitwarden-stripe-tools`, declared in `plugin.json` so they install with this plugin. They own the pipeline's email reading and Stripe queries.
- Behavior evals for `scoping-playwright-application-context`, thirteen advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.
- Behavior evals for `mapping-services-under-test`, six advice-only cases. The suite is kept as an authoring aid and has not been benchmarked.
- Trigger evals for `scoping-playwright-application-context` and `mapping-services-under-test`, each ten should-trigger phrasings and ten near-misses, including the other skill's phrasings. Neither suite has been run, so neither has a baseline yet.

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
