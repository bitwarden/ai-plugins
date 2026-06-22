# Bitwarden Test Engineer Plugin

## Overview

A test engineering toolkit for Bitwarden. It hosts role-specific testing agents. Today it
ships one — the **test strategist** (`test-strategist`), the test-_planning_ role:
it recommends what to test, at which layer, and why, and inventories what is already tested.
It does not author, run, or maintain the tests, nor do exploratory/manual QA. The plugin is
designed to grow additional roles over time (for example an SDET or a QA engineer).

### First role: the test strategist

Given a change — a feature, bugfix, refactor, or migration — the agent recommends
**what to test, at which layer, and why**, shaped to **each repo's actual test practice**.
Two ideas drive it: each behavior is tested at the cheapest layer that buys the confidence it
needs (unit, integration, or E2E), and how those layers are weighted is decided per repo — a
unit-heavy pyramid (`server`, `clients`, `sdk-internal`, `android`), an integration/snapshot
trophy (`ios`), or a wholly all-E2E repo (the dedicated `test` repo,
`browser-interactions-testing`). E2E is "thin" only _within_ a platform repo; the dedicated
`test` repo is entirely E2E by design.

It ingests whatever evidence is available — a Jira ticket (via the Atlassian MCP), a GitHub
PR (via `gh`), an exported test-case CSV, and/or a plain-language description — fans out
subagents to gather it, assesses what is **already tested** (the `assessing-test-coverage`
skill, which inventories existing tests, cites each as a GitHub permalink, and writes a
coverage report), then runs the analyst skill (`analyzing-test-stack`), which produces the
test-stack recommendation. Both skills emit a self-contained HTML report.

## Where each layer lives

Unit and integration tests live alongside the code inside each platform repo
(e.g. `bitwarden/server`, `bitwarden/clients`, `bitwarden/ios`). **End-to-end tests live
in a dedicated, private `test` repository** — not inside the platform repos — so E2E
recommendations target that separate repo, and existing E2E coverage is treated as
unverified when that repo isn't checked out.

## Agents

| Agent             | What It Does                                                                                                                                                                                                                                                                         |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `test-strategist` | Classifies the inputs for a change (Jira, PR, CSV, description), fans out subagents to gather evidence, assesses existing coverage (`assessing-test-coverage`), then runs `analyzing-test-stack` — emitting a self-contained coverage report and a self-contained test-stack report. |

## Skills

| Skill                     | What It Does                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `assessing-test-coverage` | The backward-looking inventory. Determines what is **already tested** for a change — scoped to the change surface, PR-first then a targeted lookup — buckets each observed test by layer, cites it as a stable GitHub permalink, flags untested behaviors as gaps, and writes a self-contained HTML coverage report. Feeds `analyzing-test-stack`; usable standalone to audit current coverage. |
| `analyzing-test-stack`    | The recommender. Consumes the coverage inventory, then maps each testable behavior in a change to the cheapest sufficient test layer per platform, inside each repo's actual shape, names concrete tooling, surfaces coverage gaps and shape-wrong tests (ice-cream-cone, over-testing, missing platform layers), and writes a self-contained HTML report into a per-change report directory.   |

## Cross-Plugin Integration

| Plugin                      | How It's Used                                                                                                                                                                                                                                                                |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-atlassian-tools` | Optional but recommended. Provides the `mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__*` server used to read Jira tickets and linked Confluence requirements. If absent, the plugin degrades gracefully — paste requirements or rely on the PR/CSV/description. |

## Installation

```bash
/plugin install bitwarden-test-engineer@bitwarden-marketplace
```

For Jira-backed analysis, install the Atlassian tools alongside it:

```bash
/plugin install bitwarden-atlassian-tools@bitwarden-marketplace
```

## Usage

The agent activates when you ask what test coverage a change needs, which
automation layers to add, how to shape a test plan, or whether existing tests are at the
right level:

```
I'm picking up PM-12345 next sprint. What test coverage should this feature have?
```

```
Does bitwarden/server#5821 have the right tests, or is it leaning too hard on end-to-end?
```

```
Here's our exported test cases CSV for the new item types import/export work (PM-32009) —
which of these should be automated and at what layer?
```

Each run produces a per-change directory `test-engineer-report-<slug>-<date>/` holding the
self-contained HTML reports: `coverage.html` (what is already tested — observed tests per layer,
each cited as a GitHub permalink, plus gaps), `recommended.html` (the per-platform recommendation
and its coverage-gap findings), and `combined.html` (the primary deliverable — both on one two-tab
page). Re-running on the same change and date refreshes the reports in that directory. They share
one off-brand data-report visual system so they read as the same instrument.

## References

- [Claude Code Agents](https://code.claude.com/docs/en/agents)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [The Testing Trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
