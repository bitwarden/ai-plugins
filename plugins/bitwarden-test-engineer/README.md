# Bitwarden Test Engineer Plugin

## Overview

A test engineering toolkit for Bitwarden. An orchestrator analyzes a request and
dispatches specialized skills across the testing discipline — test strategy and planning,
automation, exploratory testing, and quality assessment. The plugin is designed to grow:
new testing skills are added over time, and **every analytic skill ships with an
adversarial counterpart** that red-teams its output before it reaches you. An unchallenged
test plan tends to drift toward whatever is easiest to do rather than what actually buys
confidence; the adversary exists to catch that.

### First capability: test-stack analysis

Given a change — a feature, bugfix, refactor, or migration — the orchestrator recommends
**what to test, at which layer, and why**, shaped as a **Testing Trophy**: a thin
static-analysis base, a focused unit layer, a heavy integration layer where most confidence
is bought, and a thin E2E layer reserved for critical user journeys.

It ingests whatever evidence is available — a Jira ticket (via the Atlassian MCP), a GitHub
PR (via `gh`), an exported test-case CSV, and/or a plain-language description — fans out
subagents to gather it, runs the analyst skill (`analyzing-test-stack`) to produce a
self-contained HTML report, then automatically runs its adversarial counterpart
(`challenging-test-stack-recommendations`) to red-team the recommendation and consolidate a
single report.

## Where each layer lives

Static, unit, and integration tests live alongside the code inside each platform repo
(e.g. `bitwarden/server`, `bitwarden/clients`, `bitwarden/ios`). **End-to-end tests live
in a dedicated, private `test` repository** — not inside the platform repos — so E2E
recommendations target that separate repo, and existing E2E coverage is treated as
unverified when that repo isn't checked out.

## Agent

| Agent                        | What It Does                                                                                                                                                                                                                            |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test-engineer-orchestrator` | Classifies the inputs for a change (Jira, PR, CSV, description), fans out subagents to gather evidence, runs `analyzing-test-stack`, then automatically runs `challenging-test-stack-recommendations` and consolidates a single report. |

## Skills

| Skill                                    | What It Does                                                                                                                                                                                                                                                                                                                                         |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `analyzing-test-stack`                   | The recommender. Maps each testable behavior in a change to the cheapest sufficient Testing Trophy layer per platform, names concrete tooling, surfaces coverage gaps, and writes a self-contained HTML report to the current working directory.                                                                                                     |
| `challenging-test-stack-recommendations` | The adversarial counterpart. Re-derives the evidence independently and red-teams the recommendation against known anti-patterns (ice-cream-cone, unit-masquerading-as-integration, over-testing, untestable requirements, missing platform layers, flaky-E2E, ungrounded coverage), then returns a verdict: endorse, revise, or reject-with-reasons. |

## Cross-Plugin Integration

| Plugin                      | How It's Used                                                                                                                                                                                                                               |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-atlassian-tools` | Optional but recommended. Provides the `mcp__bitwarden-atlassian__*` server used to read Jira tickets and linked Confluence requirements. If absent, the plugin degrades gracefully — paste requirements or rely on the PR/CSV/description. |

## Installation

```bash
/plugin install bitwarden-test-engineer@bitwarden-marketplace
```

For Jira-backed analysis, install the Atlassian tools alongside it:

```bash
/plugin install bitwarden-atlassian-tools@bitwarden-marketplace
```

## Usage

The orchestrator activates when you ask what test coverage a change needs, which
automation layers to add, how to shape a test plan, or whether existing tests are at the
right level:

```
I'm picking up PM-12345 next sprint. What test coverage should this feature have?
```

```
Does bitwarden/server#5821 have the right tests, or is it leaning too hard on end-to-end?
```

```
Here's our exported test cases CSV for the billing migration — which of these should be
automated and at what layer?
```

Each run produces a self-contained `test-stack-report-<slug>-<date>.html` in the current
working directory, containing the per-platform recommendation and the adversarial review.

## References

- [Claude Code Agents](https://code.claude.com/docs/en/agents)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [The Testing Trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
