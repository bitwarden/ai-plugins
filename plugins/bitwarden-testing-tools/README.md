# Bitwarden Testing Tools Plugin

A set of test related skills for Bitwarden.

## Overview

A set of skills that support Bitwarden's testing and quality work with evidence grounded in our repos, layers, and where our tests actually live. Skills can be invoked individually and this plugin is designed to grow over time. See the table below for what ships today.

## Skills

| Skill                             | What It Does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `assessing-test-coverage`         | Determines what a change is **already tested by**. From a PR, Jira key, Tech Breakdown, or Testmo CSV, resolves the change surface, finds the existing tests PRs-first, buckets each by layer (unit / integration / E2E), cites it as a stable GitHub permalink, and records untested behaviors as gaps, writing a self-contained markdown report under `${CLAUDE_PLUGIN_DATA}/coverage-reports/`. For a story, it also reviews the existing Testmo cases in the story's client folders and New Release, and recommends retire or update for each case the story changes, with the AC or plan item behind it. It checks each automated case's Automation Type against the `[Description]` IDs in code, and lists possible duplicates and cases owned by other teams. It reads Testmo through Testmo's official MCP server in read-only mode, checks automation through the bundled `bitwarden-test-automation` server, and never writes to Testmo or code. |
| `writing-manual-test-cases`       | Authors the **new manual test cases** a change needs. From a Jira ticket, PR, or feature description, gap-checks the requirements, plans the scenario coverage for approval, then drafts Gherkin cases — each classified Smoke / Regression / Functional with a matching Automation Type. Delivers a plain-text file for review and a Testmo-importable CSV under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `recommending-test-layers`        | Recommends **which tests to add and at which layer**. From a Jira key, Testmo CSV, an `assessing-test-coverage` report, a PR, or a feature description, places each behavior at its lowest sufficient deterministic layer (static / unit / component / contract), then adds non-deterministic layers (integration, E2E, smoke, synthetic monitoring, exploratory) where each one's trigger is met, grading criticality against Bitwarden's Severity guide. Writes a markdown recommendation report under `${CLAUDE_PLUGIN_DATA}/recommending-test-layers/`.                                                                                                                                                                                                                                                                                                                                                                                                |
| `assessing-requirement-readiness` | Judges whether a Jira story is **READY to build and test**; given an epic, enumerates its child stories and judges each. Checks each acceptance criterion for clarity, testability, and completeness, reads linked issues, sibling stories, and any Figma design, and returns READY or NOT READY with the specific gaps to fix. Reviews only and does not write the specification.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `designing-test-plans`            | Designs the **tests a READY story or epic needs**, derived from its acceptance criteria. Gates on `assessing-requirement-readiness` first, then maps each acceptance criterion to the tests that cover it, with traceability from criterion to test. Designs only and writes no test code.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `setting-up-regression-runs`      | Sets up the **QA manual regression runs for a release** in Testmo. Picks the `partial` or `full` release profile, applies any per-release exclusions, and hands the profile's shipped specs to `bitwarden-testmo-tools`' `creating-test-runs` skill, which dry-runs them for review, creates them linked to the release milestone, and lists the multi-configuration runs that still need a manual Testmo UI pass.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |

## Cross-Plugin Integration

| Plugin                      | How It's Used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-atlassian-tools` | **Recommended** — the primary way to drive analysis from Jira tickets and linked Confluence requirements, via its `researching-jira-issues` skill and Atlassian MCP tools. `recommending-test-layers` also uses its `get_confluence_page` tool to grade criticality against the Bitwarden Defect Severity Classification Guide, for any input type. Optional by design: if absent, drive the analysis from the PR / CSV / tech-breakdown / description instead and grade criticality by judgment. A Jira ticket input, however, requires the plugin — without it, stop and ask the user to install and configure it. |

`assessing-requirement-readiness` and `designing-test-plans` also require `bitwarden-atlassian-tools`. The readiness skill reads the story with `get_issue` and gets linked issues and Confluence context through `researching-jira-issues`, and its input is always a Jira story or epic key. Without the plugin, stop and ask the user to install and configure it.

`setting-up-regression-runs` requires `bitwarden-testmo-tools`, which owns the Testmo API access and run-creation script. Without it, stop and ask the user to install it.

## Installation

```bash
/plugin install bitwarden-testing-tools@bitwarden-marketplace
```

For Jira-backed analysis, install the Atlassian tools alongside it:

```bash
/plugin install bitwarden-atlassian-tools@bitwarden-marketplace
```

To set up regression runs, install the Testmo tools as well:

```bash
/plugin install bitwarden-testmo-tools@bitwarden-marketplace
```

## Testmo MCP Server

`assessing-test-coverage` reads Testmo through Testmo's official MCP server. You need a Testmo seat and your own API key. Create the key in Testmo under My profile & settings, then API access.

Add the server in read-only mode, named exactly `testmo`. The skill's allowed tools expect that name.

First open your shell profile (for example `~/.zshrc`) in a text editor and add the line `export TESTMO_TOKEN=<your key>`. Use the editor, not `echo` or another command. A command would save the key in your shell history. Then open a new terminal.

```bash
claude mcp add testmo "https://testmo.sembi.com/mcp?mode=read-only&INSTANCE-URL=bitwarden.testmo.net" --transport http --scope user --header 'Authorization: Bearer ${TESTMO_TOKEN}'
claude mcp list        # testmo should show Connected, with no warning about TESTMO_TOKEN
```

The single quotes matter. Claude Code saves `${TESTMO_TOKEN}`, not the key, in `~/.claude.json` and reads the key from your environment each time it starts. Without the server, the skill reports that Testmo was not checked and finishes the code side.

## Test Automation MCP Server

The plugin bundles a read-only MCP server, `bitwarden-test-automation`, at `mcp/bitwarden-test-automation-mcp-server/`. Its one tool, `find_automated_cases`, takes Testmo case IDs and reports which ones are automated in `bitwarden/test`. It reads the repo through your `gh` login and needs no Testmo key. It refuses to start if `NODE_TLS_REJECT_UNAUTHORIZED` is `0`.

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
Set up the full regression runs for the "2026.8.0 Manual Regression" milestone.
```

## References

- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
