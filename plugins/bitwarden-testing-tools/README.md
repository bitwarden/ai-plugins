# Bitwarden Testing Tools Plugin

A set of test related skills for Bitwarden.

## Overview

This plugin holds Bitwarden's testing and quality tooling in two families.

**Standalone analysis skills** are invoked directly and work on their own. `assessing-test-coverage` determines what a change is already tested by.

**The web test pipeline** is driven by one entry point, `test-web-changes`, which orchestrates six agents to take a Jira ticket, implementation plan, or feature description and turn it into a full Playwright test run against a local dev environment. Its component skills are composed by that pipeline rather than invoked directly, with one exception: `reading-mailcatcher-api` is also useful on its own for reading a single Bitwarden email outside a test run.

## Prerequisites

**Required Claude Code skill:** Install the `playwright-cli` skill before using the web test pipeline. Four components declare a `playwright-cli` dependency in their own frontmatter: `verifying-environment-health`, `executing-web-tests`, `service-manager`, and `test-runner`. Render verification and all browser test execution depend on it.

**Bitwarden dev environment:** Start all required services before invoking `test-web-changes`. The pipeline only verifies; it never starts, builds, or stops services.

- **Dev infrastructure (containers)**: start Bitwarden's mssql, mailcatcher, and azurite containers via either Docker Compose (`server/dev/docker-compose.yml`) or .NET Aspire (`server/AppHost`).
- **Application services**: start the web frontend (`clients` Nx workspace, `nx serve web --configuration=commercial`), plus the .NET services your test will touch (typically `Api`, `Identity`, and depending on scope `Billing`, `billing-pricing`, `Admin` / Bitwarden Portal, `Notifications`, `Events`, `Icons`).

The `verifying-environment-health` skill confirms Docker dev containers, application `/alive` endpoints, and the Angular bootstrap before tests begin. If anything is missing it halts with a hint pointing to what to start.

## Skills

| Skill                           | What It Does                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `assessing-test-coverage`       | Determines what a change is **already tested by**. From a PR, Jira key, Tech Breakdown, or Testmo CSV, resolves the change surface, finds the existing tests PRs-first, buckets each by layer (unit / integration / E2E), cites it as a stable GitHub permalink, and records untested behaviors as gaps, writing a self-contained markdown report under `${CLAUDE_PLUGIN_DATA}/coverage-reports/`.                    |
| `writing-manual-test-cases`     | Authors the **new manual test cases** a change needs. From a Jira ticket, PR, or feature description, gap-checks the requirements, plans the scenario coverage for approval, then drafts Gherkin cases — each classified Smoke / Regression / Functional with a matching Automation Type. Delivers a plain-text file for review and a Testmo-importable CSV under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`. |
| `test-web-changes`              | Orchestration skill; the only pipeline entry point. Dispatches the six agents below in an eight-task pipeline and renders an HTML report.                                                                                                                                                                                                                                                                             |
| `reading-mailcatcher-api`       | Reads Bitwarden emails via the Mailcatcher REST API for verification links, magic links, and OTP codes. Directly invocable, and also used by the pipeline.                                                                                                                                                                                                                                                            |
| `using-stripe-cli`              | Queries read-only Stripe test data and advances an already-attached test clock via the `stripe_cli.py` wrapper.                                                                                                                                                                                                                                                                                                       |
| `exploring-application-context` | Surveys changed files, routes, selectors, and verification points across affected repositories into a States and Flows document.                                                                                                                                                                                                                                                                                      |
| `determining-required-services` | Maps routes and the branch diff to the local services that must be running.                                                                                                                                                                                                                                                                                                                                           |
| `build-test-cases`              | Builds Playwright test cases with a web-first policy from plan context, labeling external-trigger steps so the approver can see them.                                                                                                                                                                                                                                                                                 |
| `verifying-environment-health`  | Verifies Docker dev containers via preflight, application services via the health-check script, and Angular bootstrap via render verification. Halts on the first failure.                                                                                                                                                                                                                                            |
| `executing-web-tests`           | Calls the `playwright-cli` skill with guardrails and screenshots, governing tool policy, screenshot naming, toast capture, and setup-step execution.                                                                                                                                                                                                                                                                  |

## Agents

| Agent              | Description                                                                                                                                      |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `context-gatherer` | Acquires feature source content (Jira ticket, plan file, or free-form description) and extracts structured context.                              |
| `code-explorer`    | Reads the context, explores the affected codebases, and produces the Application Context.                                                        |
| `service-mapper`   | Reads the Application Context and maps its routes, together with the branch's changed file paths, to the local services that need to be running. |
| `test-planner`     | Reads the context and Application Context artifacts and builds grounded test cases via `build-test-cases`.                                       |
| `service-manager`  | Reads the test plan and dispatches `verifying-environment-health`. Halts the run on any failure. Never starts or stops services.                 |
| `test-runner`      | Calls the `playwright-cli` skill to execute test cases with guardrails and screenshots, returning structured results.                            |

The six agents are dispatched by `test-web-changes` and are not meant to be invoked directly. That is a convention stated in each agent's description, not an enforced restriction. Claude Code has no agent frontmatter field that hides an agent from direct invocation, and the one documented mechanism, a `permissions.deny` rule of the form `Agent(<name>)`, applies to the whole session, so it would block the pipeline's own dispatch along with direct invocation. Invoking one of these agents on its own is harmless but produces nothing useful, since each expects artifact paths the orchestrator creates.

## Cross-Plugin Integration

| Plugin                      | How It's Used                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `bitwarden-atlassian-tools` | **Recommended** for `assessing-test-coverage` and `test-web-changes` alike, the primary way to drive analysis from Jira tickets and linked Confluence requirements, via its `researching-jira-issues` skill and Atlassian MCP tools. Optional by design: if absent, drive the analysis from the PR / CSV / tech-breakdown / description instead. A Jira ticket input, however, requires the plugin; without it, stop and ask the user to install and configure it. |
| `playwright-cli`            | **Required** for the web test pipeline. `verifying-environment-health`, `executing-web-tests`, and the `test-runner` agent all reach it as `Skill(playwright-cli)` for render verification and browser test execution. Not needed for `assessing-test-coverage`.                                                                                                                                                                                                   |

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

### The web test pipeline

Invoke the orchestration skill:

```bash
/test-web-changes <jira-ticket-id | feature-plan-path | feature-description> [--confirm]
```

The first argument is the source the test run is built from: a Jira ticket key, a Jira browse URL, or a path to an implementation plan. When it is one of those, anything typed after it reaches the orchestrator as extra guidance, which it folds into the instructions it gives each agent. If the first argument is none of those, the whole input is read as a plain description of the feature to test.

**Examples:**

```bash
/test-web-changes PM-1234
/test-web-changes https://bitwarden.atlassian.net/browse/PM-1234
/test-web-changes PM-1234 focus on the owner role
/test-web-changes ~/code/bitwarden/server/plans/PM-1234-billing-ui.md
/test-web-changes "exempt orgs from billing automation when the flag is set" --confirm
```

**Flags:**

- `--confirm`: pause after the test plan is built and display the test cases for review before executing.

## How the pipeline works

`test-web-changes` runs an eight-task pipeline as the orchestrator. Each agent returns its artifact as its response; the orchestrator writes those responses verbatim to `.playwright-testing-artifacts/<slug>/` before dispatching what comes next. Tasks 3 and 4 are dispatched together and run concurrently.

| Task | Agent                                                                             | Artifact                                  |
| ---- | --------------------------------------------------------------------------------- | ----------------------------------------- |
| 1    | `context-gatherer`                                                                | `context-<timestamp>.md`                  |
| 2    | `code-explorer`                                                                   | `app-context-<timestamp>.md`              |
| 3    | `service-mapper`                                                                  | `services-<timestamp>.md`                 |
| 4    | `test-planner`                                                                    | `test-cases-<timestamp>.md`               |
| 5    | _(orchestrator composes)_                                                         | `test-plan-<timestamp>.md`                |
| 6    | `service-manager` _(verifies the environment via `verifying-environment-health`)_ | _(no artifact; halts the run on failure)_ |
| 7    | `test-runner`                                                                     | `test-results-<timestamp>.json`           |
| 8    | _(orchestrator renders via `render_report.py`)_                                   | `report-<timestamp>.html`                 |

## Web-first policy

All test actions (account creation, org setup, form submission) happen through the browser UI. Direct database queries, REST API calls outside the browser, and CLI tools are never permitted during setup or test execution.

## Billing tests

When the plan involves billing flows, `build-test-cases` bakes the Stripe test card and related values directly into the test-case steps, which run through the web UI. A billing-related 400 error during execution halts all testing immediately.

## Out of scope

The following Bitwarden surfaces are not testable via the web test pipeline (no Playwright UI surface):

- **Browser extensions** (`clients/apps/browser/`), require browser extension testing setup
- **Desktop app** (`clients/apps/desktop/`), requires Electron testing setup
- **CLI** (`clients/apps/cli/`), command-line tool, no browser UI

## References

- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
