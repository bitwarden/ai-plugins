# Bitwarden Testing Tools Plugin

A set of test related skills for Bitwarden.

## Overview

This plugin holds Bitwarden's testing and quality tooling in two families.

**Standalone analysis skills** are invoked directly and work on their own. `assessing-test-coverage` determines what a change is already tested by.

**The web test pipeline** is driven by one entry point, `start-playwright-test`, which orchestrates six agents to take a Jira ticket, implementation plan, or feature description and turn it into a full Playwright test run against a local dev environment. Its component skills are composed by that pipeline rather than invoked directly, with one exception: `reading-mailcatcher-api` is also useful on its own for reading a single Bitwarden email outside a test run.

## Prerequisites

**Required Claude Code skill:** Install the `playwright-cli` skill before using the web test pipeline. Four components declare a `playwright-cli` dependency in their own frontmatter: `checking-localhost-web-health`, `running-playwright-tests`, `localhost-web-health-checker`, and `playwright-test-runner`. Render verification and all browser test execution depend on it.

**Bitwarden dev environment:** Start all required services before invoking `start-playwright-test`. The pipeline only verifies; it never starts, builds, or stops services.

- **Dev infrastructure (containers)**: start Bitwarden's mssql, mailcatcher, and azurite containers via either Docker Compose (`server/dev/docker-compose.yml`) or .NET Aspire (`server/AppHost`).
- **Application services**: start the web frontend (`clients` Nx workspace, `nx serve web --configuration=commercial`), plus the .NET services your test will touch (typically `Api`, `Identity`, and depending on scope `Billing`, `billing-pricing`, `Admin` / Bitwarden Portal, `Notifications`, `Events`, `Icons`).

The `checking-localhost-web-health` skill confirms Docker dev containers, application `/alive` endpoints, and the Angular bootstrap before tests begin. If anything is missing it halts with a hint pointing to what to start.

## Skills

| Skill                                    | What It Does                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `assessing-test-coverage`                | Determines what a change is **already tested by**. From a PR, Jira key, Tech Breakdown, or Testmo CSV, resolves the change surface, finds the existing tests PRs-first, buckets each by layer (unit / integration / E2E), cites it as a stable GitHub permalink, and records untested behaviors as gaps, writing a self-contained markdown report under `${CLAUDE_PLUGIN_DATA}/coverage-reports/`.                    |
| `writing-manual-test-cases`              | Authors the **new manual test cases** a change needs. From a Jira ticket, PR, or feature description, gap-checks the requirements, plans the scenario coverage for approval, then drafts Gherkin cases — each classified Smoke / Regression / Functional with a matching Automation Type. Delivers a plain-text file for review and a Testmo-importable CSV under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`. |
| `start-playwright-test`                  | Orchestration skill; the only pipeline entry point. Dispatches the six agents below in an eight-task pipeline and renders an HTML report.                                                                                                                                                                                                                                                                             |
| `reading-mailcatcher-api`                | Reads Bitwarden emails via the Mailcatcher REST API for verification links, magic links, and tokens. Directly invocable, and also used by the pipeline.                                                                                                                                                                                                                                                               |
| `using-stripe-cli`                       | Queries read-only Stripe test data and advances an already-attached test clock via the `stripe_cli.py` wrapper.                                                                                                                                                                                                                                                                                                       |
| `scoping-playwright-application-context` | Returns a state-centric Application Context — real-user-reachable UI states with grounded verification points, and the flows that transition between them — the scoping artifact that precedes Playwright test-case authoring. Working context (changed files, routes, selectors) is used to derive the states, not emitted.                                                                                          |
| `mapping-services-under-test`            | Maps routes and the branch diff to the local services that must be running.                                                                                                                                                                                                                                                                                                                                           |
| `writing-playwright-test-cases`          | Builds Playwright test cases with a web-first policy from plan context, labeling external-trigger steps so the approver can see them.                                                                                                                                                                                                                                                                                 |
| `checking-localhost-web-health`          | Verifies Docker dev containers via preflight, application services via the health-check script, and Angular bootstrap via render verification. Halts on the first failure.                                                                                                                                                                                                                                            |
| `running-playwright-tests`               | Calls the `playwright-cli` skill with guardrails and screenshots, governing tool policy, screenshot naming, toast capture, and setup-step execution.                                                                                                                                                                                                                                                                  |

## Agents

| Agent                                   | Description                                                                                                                                      |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `playwright-test-context-gatherer`      | Acquires feature source content (Jira ticket, plan file, or free-form description) and extracts structured context.                              |
| `playwright-application-context-scoper` | Reads the context, explores the affected codebases, and produces the Application Context.                                                        |
| `services-under-test-mapper`            | Reads the Application Context and maps its routes, together with the branch's changed file paths, to the local services that need to be running. |
| `playwright-test-case-writer`           | Reads the context and Application Context artifacts and builds grounded test cases via `writing-playwright-test-cases`.                          |
| `localhost-web-health-checker`          | Reads the test plan and dispatches `checking-localhost-web-health`. Halts the run on any failure. Never starts or stops services.                |
| `playwright-test-runner`                | Calls the `playwright-cli` skill to execute test cases with guardrails and screenshots, returning structured results.                            |

In the pipeline these six agents are dispatched by `start-playwright-test`. Each agent's description also stands on its own, so an agent can be invoked directly, but doing so outside the pipeline is harmless and produces nothing useful, since each expects artifact paths the pipeline's earlier steps create. There is no frontmatter field that hides an agent from direct invocation, and the one documented mechanism — a `permissions.deny` rule of the form `Agent(<name>)` — applies to the whole session, so it would block the pipeline's own dispatch along with direct invocation.

## Cross-Plugin Integration

| Plugin                      | How It's Used                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-atlassian-tools` | **Recommended** for `assessing-test-coverage` and `start-playwright-test` alike, the primary way to drive analysis from Jira tickets and linked Confluence requirements, via its `researching-jira-issues` skill and Atlassian MCP tools. Optional by design: if absent, drive the analysis from the PR / CSV / tech-breakdown / description instead. A Jira ticket input, however, requires the plugin; without it, stop and ask the user to install and configure it. |
| `playwright-cli`            | **Required** for the web test pipeline. `checking-localhost-web-health`, `running-playwright-tests`, and the `playwright-test-runner` agent all reach it as `Skill(playwright-cli)` for render verification and browser test execution. Not needed for `assessing-test-coverage`.                                                                                                                                                                                       |

## Installation

```bash
/plugin install bitwarden-testing-tools@bitwarden-marketplace
```

For Jira-backed analysis, install the Atlassian tools alongside it:

```bash
/plugin install bitwarden-atlassian-tools@bitwarden-marketplace
```

For the web test pipeline, also install `playwright-cli`. Restart Claude Code after installing for the plugin to become active.

Two skills need an external tool, and only when you invoke that skill (nothing else in the plugin requires them):

- `using-stripe-cli` — the [Stripe CLI](https://docs.stripe.com/stripe-cli), authenticated once with `stripe login`.
- `reading-mailcatcher-api` — the local Mailcatcher service running (part of the Bitwarden `server` dev environment).

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
Grab the verification link from the email Mailcatcher just received for qa+trial@example.com.
```

```
What's the status of test subscription sub_abc123, and is a test clock attached?
```

### The web test pipeline

Invoke the orchestration skill:

```bash
/start-playwright-test <jira-ticket-id | feature-plan-path | feature-description> [--confirm]
```

The first argument is the source the test run is built from: a Jira ticket key, a Jira browse URL, or a path to an implementation plan. When it is one of those, anything typed after it reaches the orchestrator as extra guidance, which it folds into the instructions it gives each agent. If the first argument is none of those, the whole input is read as a plain description of the feature to test.

**Examples:**

```bash
/start-playwright-test PM-1234
/start-playwright-test https://bitwarden.atlassian.net/browse/PM-1234
/start-playwright-test PM-1234 focus on the owner role
/start-playwright-test ~/code/bitwarden/server/plans/PM-1234-billing-ui.md
/start-playwright-test "exempt orgs from billing automation when the flag is set" --confirm
```

**Flags:**

- `--confirm`: pause after the test plan is built and display the test cases for review before executing.

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

Skill and reference files in this plugin use two harness-substituted path variables, both officially supported by Claude Code. This is recorded here so reviewers do not flag `${CLAUDE_SKILL_DIR}` as undocumented — it is intentional, not a typo for `${CLAUDE_PLUGIN_ROOT}`:

- `${CLAUDE_PLUGIN_ROOT}` — the plugin root. Used for plugin-shared paths, e.g. one skill referencing another skill's script.
- `${CLAUDE_SKILL_DIR}` — the invoking skill's own directory. Used for a skill's own `references/…` files.

## References

- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
