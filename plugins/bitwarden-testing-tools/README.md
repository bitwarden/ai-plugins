# Bitwarden Testing Tools Plugin

A set of test related skills for Bitwarden.

## Overview

A set of skills that support Bitwarden's testing and quality work with evidence grounded in our repos, layers, and where our tests actually live. Skills can be invoked individually and this plugin is designed to grow over time. See the table below for what ships today.

## Skills

| Skill                                    | What It Does                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `assessing-test-coverage`                | Determines what a change is **already tested by**. From a PR, Jira key, Tech Breakdown, or Testmo CSV, resolves the change surface, finds the existing tests PRs-first, buckets each by layer (unit / integration / E2E), cites it as a stable GitHub permalink, and records untested behaviors as gaps — writing a self-contained markdown report under `${CLAUDE_PLUGIN_DATA}/coverage-reports/`.                   |
| `writing-manual-test-cases`              | Authors the **new manual test cases** a change needs. From a Jira ticket, PR, or feature description, gap-checks the requirements, plans the scenario coverage for approval, then drafts Gherkin cases — each classified Smoke / Regression / Functional with a matching Automation Type. Delivers a plain-text file for review and a Testmo-importable CSV under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`. |
| `reading-mailcatcher-api`                | Reads Bitwarden emails via the Mailcatcher REST API for verification links, magic links, and tokens. Directly invocable.                                                                                                                                                                                                                                                                                              |
| `using-stripe-cli`                       | Queries read-only Stripe test data and advances an already-attached test clock via the `stripe_cli.py` wrapper.                                                                                                                                                                                                                                                                                                       |
| `scoping-playwright-application-context` | Returns a state-centric Application Context — real-user-reachable UI states with grounded verification points, and the flows that transition between them — the scoping artifact that precedes Playwright test-case authoring. Working context (changed files, routes, selectors) is used to derive the states, not emitted.                                                                                          |
| `mapping-services-under-test`            | Maps routes and the branch diff to the local services that must be running.                                                                                                                                                                                                                                                                                                                                           |
| `writing-playwright-test-cases`          | Builds Playwright test cases with a web-first policy from plan context, labeling external-trigger steps so the approver can see them.                                                                                                                                                                                                                                                                                 |

## Agents

| Agent                                   | Description                                                                                                             |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `playwright-test-context-gatherer`      | Acquires feature source content (Jira ticket, plan file, or free-form description) and extracts structured context.     |
| `playwright-application-context-scoper` | Reads the context, explores the affected codebases, and produces the state-centric Application Context.                 |
| `services-under-test-mapper`            | Reads the Application Context and maps changed file paths to the local services that need to be running.                |
| `playwright-test-case-writer`           | Reads the context and Application Context artifacts and builds grounded test cases via `writing-playwright-test-cases`. |

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

Two skills invoke an external tool, and only when you invoke that skill (nothing else in the plugin requires them):

- `using-stripe-cli` — the [Stripe CLI](https://docs.stripe.com/stripe-cli), authenticated once with `stripe login`.
- `reading-mailcatcher-api` — the local Mailcatcher service running (part of the Bitwarden `server` dev environment).

`scoping-playwright-application-context` does not drive a browser itself, but its `Reachable by playwright:` judgment — which decides whether a state needs a `[HUMAN]` step — is defined against the external `playwright-cli` skill, the browser driver the Playwright test pipeline uses to reach a state. Install `playwright-cli` when running that pipeline. The capability boundary it sits behind is documented in `references/playwright-tool-policy.md`.

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

```
Grab the verification link from the email Mailcatcher just received for qa+trial@example.com.
```

```
What's the status of test subscription sub_abc123, and is a test clock attached?
```

## Path variables

Skill and reference files in this plugin use two harness-substituted path variables, both officially supported by Claude Code. This is recorded here so reviewers do not flag `${CLAUDE_SKILL_DIR}` as undocumented — it is intentional, not a typo for `${CLAUDE_PLUGIN_ROOT}`:

- `${CLAUDE_PLUGIN_ROOT}` — the plugin root. Used for plugin-shared paths, e.g. one skill referencing another skill's script.
- `${CLAUDE_SKILL_DIR}` — the invoking skill's own directory. Used for a skill's own `references/…` files.

## References

- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
