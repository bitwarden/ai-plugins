# Bitwarden Testing Tools Plugin

A set of test related skills for Bitwarden.

## Overview

A set of skills that support Bitwarden's testing and quality work with evidence grounded in our repos, layers, and where our tests actually live. Skills can be invoked individually and this plugin is designed to grow over time. See the table below for what ships today.

## Skills

| Skill                           | What It Does                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `assessing-test-coverage`       | Determines what a change is **already tested by**. From a PR, Jira key, Tech Breakdown, or Testmo CSV, resolves the change surface, finds the existing tests PRs-first, buckets each by layer (unit / integration / E2E), cites it as a stable GitHub permalink, and records untested behaviors as gaps — writing a self-contained markdown report under `${CLAUDE_PLUGIN_DATA}/coverage-reports/`.                   |
| `writing-manual-test-cases`     | Authors the **new manual test cases** a change needs. From a Jira ticket, PR, or feature description, gap-checks the requirements, plans the scenario coverage for approval, then drafts Gherkin cases — each classified Smoke / Regression / Functional with a matching Automation Type. Delivers a plain-text file for review and a Testmo-importable CSV under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`. |
| `reading-mailcatcher-api`       | Reads Bitwarden emails via the Mailcatcher REST API for verification links, magic links, and OTP codes. Directly invocable.                                                                                                                                                                                                                                                                                           |
| `using-stripe-cli`              | Queries read-only Stripe test data and advances an already-attached test clock via the `stripe_cli.py` wrapper.                                                                                                                                                                                                                                                                                                       |
| `scoping-playwright-test-cases` | Surveys changed files, routes, selectors, and verification points across affected repositories into a States and Flows document.                                                                                                                                                                                                                                                                                      |
| `mapping-services-under-test`   | Maps routes and the branch diff to the local services that must be running.                                                                                                                                                                                                                                                                                                                                           |

## Agents

| Agent                              | Description                                                                                                         |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `playwright-test-context-gatherer` | Acquires feature source content (Jira ticket, plan file, or free-form description) and extracts structured context. |
| `playwright-test-case-scoper`      | Reads the context, explores the affected codebases, and produces the Application Context.                           |
| `services-under-test-mapper`       | Reads the Application Context and maps changed file paths to the local services that need to be running.            |

## Cross-Plugin Integration

| Plugin                      | How It's Used                                                                                                                                                                                                                                                                                                                                                                                             |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-atlassian-tools` | **Recommended** — the primary way to drive analysis from Jira tickets and linked Confluence requirements, via its `researching-jira-issues` skill and Atlassian MCP tools. Optional by design: if absent, drive the analysis from the PR / CSV / tech-breakdown / description instead. A Jira ticket input, however, requires the plugin — without it, stop and ask the user to install and configure it. |

## Installation

```bash
/plugin install bitwarden-testing-tools@bitwarden-marketplace
```

For Jira-backed analysis, install the Atlassian tools alongside it:

```bash
/plugin install bitwarden-atlassian-tools@bitwarden-marketplace
```

## Usage

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

## References

- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
