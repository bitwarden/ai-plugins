# Bitwarden Playwright Testing Plugin

Automated end-to-end UI testing for Bitwarden web changes using Playwright.

## Overview

This plugin provides a single user-facing skill, `test-web-changes`, that orchestrates a six-agent pipeline to take a Jira ticket, implementation plan, or feature description and turn it into a full Playwright test run. The pipeline gathers context, explores the affected codebases, builds grounded test cases, verifies the local dev environment is ready, executes the tests, and renders an HTML report with full-page screenshots.

## Prerequisites

**Required Claude Code plugin:** Install the [`playwright-cli`](https://github.com/microsoft/playwright-cli) plugin before using this plugin. Render verification and all browser test execution depend on it.

**Bitwarden dev environment:** Start all required services before invoking the plugin. The plugin only verifies — it never starts, builds, or stops services.

- **Dev infrastructure (containers)**: start Bitwarden's mssql, mailcatcher, and azurite containers via either Docker Compose (`server/dev/docker-compose.yml`) or .NET Aspire (`server/AppHost`).
- **Application services**: start the web frontend (`clients` Nx workspace, `nx serve web --configuration=commercial`), plus the .NET services your test will touch (typically `Api`, `Identity`, and depending on scope `Billing`, `billing-pricing`, `Admin` / Bitwarden Portal, `Notifications`, `Events`, `Icons`).

The plugin's `verifying-environment-health` skill confirms Docker dev containers, application `/alive` endpoints, and the Angular bootstrap before tests begin. If anything is missing it halts with a hint pointing to what to start.

## Installation

```bash
/plugin install bitwarden-playwright-testing@bitwarden-marketplace
```

Restart Claude Code after installing for the plugin to become active.

## Usage

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

## How it works

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

## Agents and skills

### Agents

| Component          | Description                                                                                                                                                                                                                  |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `context-gatherer` | Acquires feature source content (Jira ticket, plan file, or free-form description) and extracts structured context.                                                                                                          |
| `code-explorer`    | Reads the context, explores the affected codebases, and produces the Application Context (changed files, routes, selectors, verification points).                                                                            |
| `service-mapper`   | Reads the Application Context and maps changed file paths to the local services that need to be running.                                                                                                                     |
| `test-planner`     | Reads context and Application Context artifacts and builds grounded test cases via the `build-test-cases` skill.                                                                                                             |
| `service-manager`  | Reads the test plan and dispatches `verifying-environment-health` to confirm Docker dev containers, application `/alive` endpoints, and the Angular bootstrap. Halts the run on any failure. Never starts or stops services. |
| `test-runner`      | Calls the `playwright-cli` skill to execute test cases with guardrails and screenshots, and returns structured results.                                                                                                      |

The six agents are dispatched by `test-web-changes` and are not meant to be invoked directly. That is a convention stated in each agent's description, not an enforced restriction. Claude Code has no agent frontmatter field that hides an agent from direct invocation, and the one documented mechanism, a `permissions.deny` rule of the form `Agent(<name>)`, applies to the whole session, so it would block the pipeline's own dispatch along with direct invocation. Invoking one of these agents on its own is harmless but produces nothing useful, since each expects artifact paths the orchestrator creates.

### Skills

| Skill                           | Description                                                                                                                                                                      |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test-web-changes`              | Orchestration skill; the only user-facing entry point.                                                                                                                           |
| `exploring-application-context` | Surveys changed files, routes, selectors, and verification points across affected repositories.                                                                                  |
| `determining-required-services` | Maps changed file paths to the local services that need to be running.                                                                                                           |
| `verifying-environment-health`  | Verifies Docker dev containers via preflight, application services via the health-check script, and Angular bootstrap via render verification. Halts on the first failure.       |
| `build-test-cases`              | Builds Playwright test cases with a web-first policy from plan context.                                                                                                          |
| `executing-web-tests`           | Calls the `playwright-cli` skill with guardrails and screenshots.                                                                                                                |
| `reading-mailcatcher-api`       | Reads Bitwarden emails via the Mailcatcher REST API for verification links, magic links, and OTP codes.                                                                          |
| `using-stripe-cli`              | Queries read-only Stripe test data and advances an already-attached test clock via the Stripe CLI wrapper (`stripe_cli.py`), for Category 4 data needs the web UI can't satisfy. |
| `compiling-test-report`         | Home of the deterministic report scripts (render_report.py, merge_results.py), templates, and the results-schema reference.                                                      |

## Web-first policy

All test actions (account creation, org setup, form submission) happen through the browser UI. Direct database queries, REST API calls outside the browser, and CLI tools are never permitted during setup or test execution.

## Billing tests

When the plan involves billing flows, `build-test-cases` bakes the Stripe test card and related values directly into the test-case steps, which run through the web UI. A billing-related 400 error during execution halts all testing immediately.

## Out of scope

The following Bitwarden surfaces are not testable via this plugin (no Playwright UI surface):

- **Browser extensions** (`clients/apps/browser/`) — require browser extension testing setup
- **Desktop app** (`clients/apps/desktop/`) — requires Electron testing setup
- **CLI** (`clients/apps/cli/`) — command-line tool, no browser UI

## Plugin structure

See [Agents](#agents) and [Skills](#skills) above for the full component list, and each component's own directory for its files. This section intentionally doesn't duplicate that list as a file tree — a hand-maintained tree here fell out of sync with the filesystem in the past and would only do so again.

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for plugin development guidelines, structure requirements, versioning rules, and the review process.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

See [LICENSE.txt](../../LICENSE.txt)
