# Bitwarden Playwright Testing Plugin

Automated end-to-end UI testing for Bitwarden web changes using Playwright.

## Overview

This plugin provides a single user-facing skill, `test-web-changes`, that orchestrates a seven-agent team to take a Jira ticket, implementation plan, or feature description and turn it into a full Playwright test run. The team gathers context, explores the affected codebases, builds grounded test cases, verifies the local dev environment is ready, executes the tests, and compiles an HTML report with full-page screenshots.

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

Invoke the team-lead skill:

```bash
/test-web-changes <jira-ticket-id | feature-plan-path | feature-description> [--confirm]
```

**Examples:**

```bash
/test-web-changes PM-1234
/test-web-changes ~/code/bitwarden/server/plans/PM-1234-billing-ui.md
/test-web-changes "exempt orgs from billing automation when the flag is set" --confirm
```

**Flags:**

- `--confirm`: pause after the test plan is built and display the test cases for review before executing.

## How it works

`test-web-changes` runs an eight-task pipeline as the team lead. Each agent returns its artifact as a markdown response; the team lead writes those responses verbatim to `.playwright-testing-artifacts/<slug>/` and dispatches the next agent.

| Task | Agent | Artifact |
|---|---|---|
| 1 | `context-gatherer` | `context-<timestamp>.md` |
| 2 | `code-explorer` | `app-context-<timestamp>.md` |
| 3 | `service-mapper` | `services-<timestamp>.md` |
| 4 | `test-planner` | `test-cases-<timestamp>.md` |
| 5 | *(team lead composes)* | `test-plan-<timestamp>.md` |
| 6 | `service-manager` *(verifies the environment via `verifying-environment-health`)* | *(no artifact; halts the run on failure)* |
| 7 | `test-runner` | `test-results-<timestamp>.md` |
| 8 | `report-compiler` | `report-<timestamp>.html` |

## Agents and skills

### Agents

| Component | Description |
|---|---|
| `context-gatherer` | Acquires feature source content (Jira ticket, plan file, or free-form description) and extracts structured context. |
| `code-explorer` | Reads the context, explores the affected codebases, and produces the Application Context (changed files, routes, selectors, verification points). |
| `service-mapper` | Reads the Application Context and maps changed file paths to the local services that need to be running. |
| `test-planner` | Reads context and Application Context artifacts and builds grounded test cases via the `build-test-cases` skill. |
| `service-manager` | Reads the test plan and dispatches `verifying-environment-health` to confirm Docker dev containers, application `/alive` endpoints, and the Angular bootstrap. Halts the run on any failure. Never starts or stops services. |
| `test-runner` | Launches the `playwright-cli` agent to execute test cases with guardrails and screenshots, and returns structured results. |
| `report-compiler` | Compiles an HTML report from the test results. |

### Skills

| Skill | Description |
|---|---|
| `test-web-changes` | Team-lead orchestration skill; the only user-facing entry point. |
| `exploring-application-context` | Surveys changed files, routes, selectors, and verification points across affected repositories. |
| `determining-required-services` | Maps changed file paths to the local services that need to be running. |
| `verifying-environment-health` | Verifies Docker dev containers via preflight, application services via the health-check script, and Angular bootstrap via render verification. Halts on the first failure. |
| `build-test-cases` | Builds Playwright test cases with a web-first policy from plan context. |
| `executing-web-tests` | Launches the `playwright-cli` agent with guardrails and screenshots. |
| `reading-mailcatcher-api` | Reads Bitwarden emails via the Mailcatcher REST API for verification links, magic links, and OTP codes. |
| `compiling-test-report` | Writes an HTML report from agent results. |

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

```
bitwarden-playwright-testing/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── CHANGELOG.md
├── agents/
│   ├── context-gatherer/AGENT.md
│   ├── code-explorer/AGENT.md
│   ├── service-mapper/AGENT.md
│   ├── test-planner/AGENT.md
│   ├── service-manager/AGENT.md
│   ├── test-runner/AGENT.md
│   └── report-compiler/AGENT.md
├── scripts/
│   └── playwright.config.json           # Sets ignoreHTTPSErrors for dev certs
└── skills/
    ├── test-web-changes/SKILL.md        # Team-lead entry point
    ├── exploring-application-context/
    │   ├── SKILL.md
    │   └── references/
    ├── determining-required-services/
    │   ├── SKILL.md
    │   └── references/services.md
    ├── verifying-environment-health/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── preflight-check.sh       # Verifies Docker and dev-env preconditions
    │       └── health-check.sh          # Polls service /alive endpoints
    ├── build-test-cases/
    │   ├── SKILL.md
    │   └── references/billing-test-data.md
    ├── executing-web-tests/
    │   └── SKILL.md
    ├── reading-mailcatcher-api/
    │   ├── SKILL.md
    │   └── references/email-patterns.md
    └── compiling-test-report/
        ├── SKILL.md
        └── templates/
            └── report-template.html
```

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for plugin development guidelines, structure requirements, versioning rules, and the review process.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

See [LICENSE.txt](../../LICENSE.txt)
