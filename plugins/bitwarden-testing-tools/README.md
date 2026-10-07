# Bitwarden Testing Tools Plugin

A set of test related skills for Bitwarden.

## Overview

This plugin holds Bitwarden's testing and quality tooling in two families.

**Standalone analysis skills** are invoked directly and work on their own. `assessing-test-coverage` determines what a change is already tested by.

**The web test pipeline** is driven by one entry point, `start-playwright-test`, which orchestrates six agents to take a Jira ticket, implementation plan, or feature description and turn it into a full Playwright test run against a local dev environment. Its component skills are composed by that pipeline rather than invoked directly. It reads email and Stripe data through two vendor plugins it depends on, `bitwarden-mailcatcher-tools` and `bitwarden-stripe-tools`, whose skills are also useful on their own outside a test run.

## Prerequisites

**Required Claude Code skill:** Install the `playwright-cli` skill before using the web test pipeline. Four components declare a `playwright-cli` dependency in their own frontmatter: `checking-localhost-web-health`, `running-playwright-tests`, `localhost-web-health-checker`, and `playwright-test-runner`. Render verification and all browser test execution depend on it.

**Bitwarden dev environment:** Start all required services before invoking `start-playwright-test`. The pipeline only verifies; it never starts, builds, or stops services.

- **Dev infrastructure (containers)**: start Bitwarden's mssql, mailcatcher, and azurite containers via either Docker Compose (`server/dev/docker-compose.yml`) or .NET Aspire (`server/AppHost`).
- **Application services**: start the web frontend (`clients` Nx workspace, `nx serve web --configuration=commercial`), plus the .NET services your test will touch (typically `Api`, `Identity`, and depending on scope `Billing`, `billing-pricing`, `Admin` / Bitwarden Portal, `Notifications`, `Events`, `Icons`).

The `checking-localhost-web-health` skill confirms Docker dev containers, application `/alive` endpoints, required feature flags, and the Angular bootstrap before tests begin. If anything is missing or a flag is in the wrong state, it halts with a hint pointing to what to start or change.

## Skills

| Skill                                    | What It Does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `assessing-test-coverage`                | Determines what a change is **already tested by**. From a PR, Jira key, Tech Breakdown, or Testmo CSV, resolves the change surface, finds the existing tests PRs-first, buckets each by layer (unit / integration / E2E), cites it as a stable GitHub permalink, and records untested behaviors as gaps, writing a self-contained markdown report under `${CLAUDE_PLUGIN_DATA}/coverage-reports/`.                                                                                                                                                          |
| `writing-manual-test-cases`              | Authors the **new manual test cases** a change needs. From a Jira ticket, PR, or feature description, gap-checks the requirements, plans the scenario coverage for approval, then drafts Gherkin cases — each classified Smoke / Regression / Functional with a matching Automation Type. Delivers a plain-text file for review and a Testmo-importable CSV under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`.                                                                                                                                       |
| `recommending-test-layers`               | Recommends **which tests to add and at which layer**. From a Jira key, Testmo CSV, an `assessing-test-coverage` report, a PR, or a feature description, places each behavior at its lowest sufficient deterministic layer (static / unit / component / contract), then adds non-deterministic layers (integration, E2E, smoke, synthetic monitoring, exploratory) where each one's trigger is met, grading criticality against Bitwarden's Severity guide. Writes a markdown recommendation report under `${CLAUDE_PLUGIN_DATA}/recommending-test-layers/`. |
| `start-playwright-test`                  | Orchestration skill; the only pipeline entry point. Dispatches the six agents below in an eight-task pipeline and renders an HTML report.                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `scoping-playwright-application-context` | Returns a state-centric Application Context — real-user-reachable UI states with grounded verification points, and the flows that transition between them — the scoping artifact that precedes Playwright test-case authoring. Working context (changed files, routes, selectors) is used to derive the states, not emitted. Reusable states and flows live in curated per-domain catalogs under `references/known-flows/`; newly validated ones belong in the domain-appropriate catalog rather than being re-derived per run.                             |
| `mapping-services-under-test`            | Maps routes and the branch diff to the local services that must be running.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `writing-playwright-test-cases`          | Builds Playwright test cases with a web-first policy from plan context, labeling external-trigger steps so they are visible in the plan and the execution log.                                                                                                                                                                                                                                                                                                                                                                                              |
| `checking-localhost-web-health`          | Verifies Docker dev containers via preflight, application services via the health-check script, required feature flags via the flag-check script, and Angular bootstrap via render verification. Halts on the first failure.                                                                                                                                                                                                                                                                                                                                |
| `running-playwright-tests`               | Drives the browser via the `playwright-cli` skill's CLI with guardrails and screenshots, governing tool policy, screenshot naming, toast capture, and setup-step execution.                                                                                                                                                                                                                                                                                                                                                                                 |
| `compiling-playwright-report`            | Home of the deterministic report scripts (`render_report.py`, `merge_results.py`), the report templates, and the results-schema reference.                                                                                                                                                                                                                                                                                                                                                                                                                  |

## Agents

| Agent                                   | Description                                                                                                                                                                       |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `playwright-test-context-gatherer`      | Acquires feature source content (Jira ticket, plan file, or free-form description) and extracts structured context.                                                               |
| `playwright-application-context-scoper` | Reads the context, explores the affected codebases, and produces the Application Context.                                                                                         |
| `services-under-test-mapper`            | Reads the Application Context and maps its routes, together with the branch's changed file paths, to the local services that need to be running.                                  |
| `playwright-test-case-writer`           | Reads the context and Application Context artifacts and builds grounded test cases via `writing-playwright-test-cases`.                                                           |
| `localhost-web-health-checker`          | Reads the test plan and runs `checking-localhost-web-health`. Halts the run on any failure, including a required feature flag in the wrong state. Never starts or stops services. |
| `playwright-test-runner`                | Drives the browser via the `playwright-cli` skill's CLI to execute test cases with guardrails and screenshots, returning structured results.                                      |

In the pipeline these six agents are dispatched by `start-playwright-test`. Each agent's description also stands on its own, so an agent can be invoked directly, but doing so outside the pipeline is harmless and produces nothing useful, since each expects artifact paths the pipeline's earlier steps create. There is no frontmatter field that hides an agent from direct invocation, and the one documented mechanism — a `permissions.deny` rule of the form `Agent(<name>)` — applies to the whole session, so it would block the pipeline's own dispatch along with direct invocation.

## Hooks

| Hook                          | Event                          | What It Does                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ----------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `restrict_planning_agents.py` | `PreToolUse` (`Skill`)         | Limits the `playwright-application-context-scoper`, `services-under-test-mapper`, `playwright-test-context-gatherer`, and `playwright-test-case-writer` agents, which hold no `Bash`, to their own skill, blocking any other `Skill` call before permission rules are evaluated while the hook runs. Other agents and the main session are unaffected. Needs `python3` on `PATH`; see "Known limits of these controls" in `references/playwright-tool-policy.md`. |
| `restrict_health_checker.py`  | `PreToolUse` (`Bash`, `Skill`) | Limits the `localhost-web-health-checker` agent to the `checking-localhost-web-health` scripts and the `playwright-cli` calls render verification makes, and its `Skill` calls to that skill and `playwright-cli`, blocking anything else. Other agents and the main session are unaffected. Needs `python3` on `PATH`; see the same section.                                                                                                                     |

## Cross-Plugin Integration

| Plugin                        | How It's Used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-atlassian-tools`   | **Recommended** for `assessing-test-coverage` and `start-playwright-test` alike, the primary way to drive analysis from Jira tickets and linked Confluence requirements, via its `researching-jira-issues` skill and Atlassian MCP tools. `recommending-test-layers` also uses its `get_confluence_page` tool to grade criticality against the Bitwarden Defect Severity Classification Guide, for any input type. Optional by design: if absent, drive the analysis from the PR / CSV / tech-breakdown / description instead and grade criticality by judgment. A Jira ticket input, however, requires the plugin; without it, stop and ask the user to install and configure it. |
| `bitwarden-mailcatcher-tools` | **Required, installed automatically** — the Playwright test pipeline reads verification links, magic links, and invites through its `bitwarden-mailcatcher-tools:reading-mailcatcher-api` skill. Needs the local Mailcatcher service running (part of the Bitwarden `server` dev environment); see that plugin's README.                                                                                                                                                                                                                                                                                                                                                           |
| `bitwarden-stripe-tools`      | **Required, installed automatically** — the Playwright test pipeline reads Stripe test-mode data and advances attached test clocks through its `bitwarden-stripe-tools:using-stripe-cli` skill. Needs the [Stripe CLI](https://docs.stripe.com/stripe-cli), authenticated once with `stripe login`; see that plugin's README.                                                                                                                                                                                                                                                                                                                                                      |

## Installation

```bash
/plugin install bitwarden-testing-tools@bitwarden-marketplace
```

For Jira-backed analysis, install the Atlassian tools alongside it:

```bash
/plugin install bitwarden-atlassian-tools@bitwarden-marketplace
```

For the web test pipeline, also install `playwright-cli`. Restart Claude Code after installing for the plugin to become active.

## Usage

### Standalone skills

Skills activate based on natural-language triggers:

```
What's already tested for bitwarden/server#5821?
```

```
Does this PR have tests, and what layers do they cover?
```

```
What coverage exists for the item-types import/export work in PM-32009?
```

```
Write manual test cases for PM-35944, the free-user health upgrade banner.
```

```
Turn these acceptance criteria into Gherkin test cases I can import into Testmo.
```

```
Should I add integration tests for the SsoController change, or are unit tests enough?
```

```
Recommend which tests to add and at which layer for PM-32009.
```

### The web test pipeline

Invoke the orchestration skill:

```bash
/start-playwright-test <jira-ticket-id | feature-plan-path | feature-description>
```

The first argument is the source the test run is built from: a Jira ticket key, a Jira browse URL, or a path to an implementation plan. When it is one of those, anything typed after it reaches the orchestrator as extra guidance, which it folds into the instructions it gives each agent. If the first argument is none of those, the whole input is read as a plain description of the feature to test.

**Examples:**

```bash
/start-playwright-test PM-1234
/start-playwright-test https://bitwarden.atlassian.net/browse/PM-1234
/start-playwright-test PM-1234 focus on the owner role
/start-playwright-test ~/code/bitwarden/server/plans/PM-1234-billing-ui.md
/start-playwright-test "exempt orgs from billing automation when the flag is set"
```

## How the pipeline works

`start-playwright-test` runs an eight-task pipeline as the orchestrator. Each agent returns its artifact as its response; the orchestrator writes those responses verbatim to `.playwright-testing-artifacts/<slug>/` before dispatching what comes next. Tasks 3 and 4 are dispatched together and run concurrently.

| Task | Agent                                                                                           | Artifact                                  |
| ---- | ----------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 1    | `playwright-test-context-gatherer`                                                              | `context-<timestamp>.md`                  |
| 2    | `playwright-application-context-scoper`                                                         | `app-context-<timestamp>.md`              |
| 3    | `services-under-test-mapper`                                                                    | `services-<timestamp>.md`                 |
| 4    | `playwright-test-case-writer`                                                                   | `test-cases-<timestamp>.md`               |
| 5    | _(orchestrator composes)_                                                                       | `test-plan-<timestamp>.md`                |
| 6    | `localhost-web-health-checker` _(verifies the environment via `checking-localhost-web-health`)_ | _(no artifact; halts the run on failure)_ |
| 7    | `playwright-test-runner`                                                                        | `test-results-<timestamp>.json`           |
| 8    | _(orchestrator renders via `render_report.py`)_                                                 | `report-<timestamp>.html`                 |

## Web-first policy

All test actions (account creation, org setup, form submission) happen through the browser UI. Direct database queries, REST API calls outside the browser, and CLI tools are never permitted during setup or test execution.

## Billing tests

When the plan involves billing flows, `writing-playwright-test-cases` bakes the Stripe test card and related values directly into the test-case steps, which run through the web UI. A billing-related 400 error during execution halts all testing immediately.

## Out of scope

The following Bitwarden surfaces are not testable via the web test pipeline (no Playwright UI surface):

- **Browser extensions** (`clients/apps/browser/`), require browser extension testing setup
- **Desktop app** (`clients/apps/desktop/`), requires Electron testing setup
- **CLI** (`clients/apps/cli/`), command-line tool, no browser UI

## Path variables

Skill and reference files in this plugin use two harness-substituted path variables, both officially supported by Claude Code:

- `${CLAUDE_PLUGIN_ROOT}` — the plugin root. Used for plugin-shared paths, e.g. one skill referencing another skill's script.
- `${CLAUDE_SKILL_DIR}` — the invoking skill's own directory. Used for a skill's own `references/…` files.

## References

- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
