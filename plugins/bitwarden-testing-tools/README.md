# Bitwarden Testing Tools Plugin

A set of test related skills for Bitwarden.

## Overview

A set of skills and agents that support Bitwarden's testing and quality work with evidence grounded in our repos, layers, and where our tests actually live. Skills can be invoked individually, and the planning-phase agents listed below turn a feature reference into grounded Playwright test-planning artifacts. This plugin is designed to grow over time. See the tables below for what ships today.

## Skills

| Skill                                    | What It Does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `assessing-test-coverage`                | Determines what a change is **already tested by**. From a PR, Jira key, Tech Breakdown, or Testmo CSV, resolves the change surface, finds the existing tests PRs-first, buckets each by layer (unit / integration / E2E), cites it as a stable GitHub permalink, and records untested behaviors as gaps — writing a self-contained markdown report under `${CLAUDE_PLUGIN_DATA}/coverage-reports/`.                                                                                                                                                         |
| `writing-manual-test-cases`              | Authors the **new manual test cases** a change needs. From a Jira ticket, PR, or feature description, gap-checks the requirements, plans the scenario coverage for approval, then drafts Gherkin cases — each classified Smoke / Regression / Functional with a matching Automation Type. Delivers a plain-text file for review and a Testmo-importable CSV under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`.                                                                                                                                       |
| `recommending-test-layers`               | Recommends **which tests to add and at which layer**. From a Jira key, Testmo CSV, an `assessing-test-coverage` report, a PR, or a feature description, places each behavior at its lowest sufficient deterministic layer (static / unit / component / contract), then adds non-deterministic layers (integration, E2E, smoke, synthetic monitoring, exploratory) where each one's trigger is met, grading criticality against Bitwarden's Severity guide. Writes a markdown recommendation report under `${CLAUDE_PLUGIN_DATA}/recommending-test-layers/`. |
| `mapping-services-under-test`            | Maps routes and the branch diff to the local services that must be running.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `scoping-playwright-application-context` | Returns a state-centric Application Context — real-user-reachable UI states with grounded verification points, and the flows that transition between them — the scoping artifact that precedes Playwright test-case authoring. Working context (changed files, routes, selectors) is used to derive the states, not emitted. Reusable states and flows live in curated per-domain catalogs under `references/known-flows/`; newly validated ones belong in the domain-appropriate catalog rather than being re-derived per run.                             |

## Agents

| Agent                                   | Description                                                                                                         |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `playwright-test-context-gatherer`      | Acquires feature source content (Jira ticket, plan file, or free-form description) and extracts structured context. |
| `playwright-application-context-scoper` | Reads the context, explores the affected codebases, and produces the state-centric Application Context.             |
| `services-under-test-mapper`            | Reads the Application Context and maps changed file paths to the local services that need to be running.            |

## Hooks

| Hook                          | Event                          | What It Does                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ----------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `restrict_planning_agents.py` | `PreToolUse` (`Bash`, `Skill`) | Limits the `playwright-application-context-scoper` and `services-under-test-mapper` agents' `Bash` to `scripts/repo-diff.sh`, and those two plus `playwright-test-context-gatherer` to their own skill, blocking anything else before permission rules are evaluated while the hook runs. Other agents and the main session are unaffected. Needs `python3` on `PATH`; see "Known limits of these controls" in `references/playwright-tool-policy.md`. |

## Cross-Plugin Integration

| Plugin                      | How It's Used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-atlassian-tools` | **Recommended** — the primary way to drive analysis from Jira tickets and linked Confluence requirements, via its `researching-jira-issues` skill and Atlassian MCP tools. `recommending-test-layers` also uses its `get_confluence_page` tool to grade criticality against the Bitwarden Defect Severity Classification Guide, for any input type. Optional by design: if absent, drive the analysis from the PR / CSV / tech-breakdown / description instead and grade criticality by judgment. A Jira ticket input, however, requires the plugin — without it, stop and ask the user to install and configure it. |

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
Should I add integration tests for the SsoController change, or are unit tests enough?
```

```
Recommend which tests to add and at which layer for PM-32009.
```

```
Scope the application context for the past-due billing banner change in clients and server.
```

```
Which local services do I need running for these tests, and what should I start?
```

## Path variables

Skill and reference files in this plugin use two harness-substituted path variables, both officially supported by Claude Code:

- `${CLAUDE_PLUGIN_ROOT}` — the plugin root. Used for plugin-shared paths, e.g. one skill referencing another skill's script.
- `${CLAUDE_SKILL_DIR}` — the invoking skill's own directory. Used for a skill's own `references/…` files.

## References

- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
