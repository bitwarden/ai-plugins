# Bitwarden Test Toolkit Plugin

A toolkit of test related skills for Bitwarden.

## Overview

A toolkit of skills that support Bitwarden's testing and quality work with evidence grounded in our repos, layers, and where our tests actually live. Skills can be invoked individually and the toolkit is designed to grow over time. See the table below for what ships today.

## Skills

| Skill                     | What It Does                                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `assessing-test-coverage` | Determines what a change is **already tested by**. From a PR, Jira key, Tech Breakdown, or Testmo CSV, resolves the change surface, finds the existing tests PRs-first, buckets each by layer (unit / integration / E2E), cites it as a stable GitHub permalink, and records untested behaviors as gaps — writing a self-contained markdown report under `${CLAUDE_PLUGIN_DATA}/coverage-reports/`. |

## Cross-Plugin Integration

| Plugin                      | How It's Used                                                                                                                                                                                                                                                                                                                                                                                             |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-atlassian-tools` | **Recommended** — the primary way to drive analysis from Jira tickets and linked Confluence requirements, via its `researching-jira-issues` skill and Atlassian MCP tools. Optional by design: if absent, drive the analysis from the PR / CSV / tech-breakdown / description instead. A Jira ticket input, however, requires the plugin — without it, stop and ask the user to install and configure it. |

## Installation

```bash
/plugin install bitwarden-test-toolkit@bitwarden-marketplace
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

## References

- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
