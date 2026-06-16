---
name: analyzing-test-stack
description: Use when recommending what test automation a feature, bugfix, or change needs and at which layer — analyzing a change from a Jira ticket, a GitHub PR, an exported test-case CSV, a technical breakdown document (a Confluence tech breakdown), and/or a plain-language description, then mapping each behavior to the cheapest sufficient Testing Trophy layer (static, unit, integration, E2E) per platform and emitting a self-contained HTML report. Triggers on "what tests should this have", "which test layers", "test stack", "test strategy", "test trophy", "test plan for this PR/ticket", "what should we test for this tech breakdown", or "are these tests at the right level". This is the recommender; its adversarial counterpart is challenging-test-stack-recommendations, which red-teams the output.
allowed-tools: "Read, Write, Grep, Glob, AskUserQuestion, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), mcp__bitwarden-atlassian__get_issue, mcp__bitwarden-atlassian__search_issues, mcp__bitwarden-atlassian__get_issue_comments, mcp__bitwarden-atlassian__get_issue_remote_links, mcp__bitwarden-atlassian__get_confluence_page, mcp__bitwarden-atlassian__search_confluence, mcp__bitwarden-atlassian__search_confluence_cql"
---

# Analyzing the Test Stack

Recommend the test automation layers a change should ship with, shaped as a **Testing Trophy**, and write the recommendation as a self-contained HTML report. You produce advice, not tests.

The Testing Trophy (read `references/testing-trophy.md` for the full model): a thin **static** base, a focused **unit** layer for pure logic and edge cases, a **heavy integration** layer where most confidence is bought, and a **thin E2E** layer reserved for critical end-to-end journeys. The guiding rule is _write tests at the cheapest layer that still buys the confidence the behavior requires_ — push coverage down the trophy, not up.

## Inputs

You may receive any combination of: a Jira key, a GitHub PR, a CSV export of test cases, a technical breakdown document, and/or a plain-language description. Treat them as additive evidence. **Today's date is provided by the caller** — use it for the report filename; do not attempt to read the clock.

Read `references/input-sources.md` for how to ingest each source:

- **Jira** — via the `mcp__bitwarden-atlassian__*` tools (or the `bitwarden-atlassian-tools:researching-jira-issues` skill if available). Extract testable behaviors and acceptance criteria. If the MCP is unavailable, ask the user to paste requirements rather than failing.
- **GitHub PR** — `gh pr view` / `gh pr diff` to read the change surface, public API touched, and any tests already present.
- **CSV** — an exported set of test cases. The expected columns and how to bucket rows by layer are documented in `references/input-sources.md`.
- **Technical breakdown** — a Bitwarden Tech Breakdown Confluence page (the artifact produced by the `bitwarden-delivery-tools:writing-tech-breakdowns` skill). Fetch via `mcp__bitwarden-atlassian__get_confluence_page`. This is often the richest single input: its scope checklist already enumerates the platforms and surfaces the change touches, and its specification child pages define the interfaces to test against. See `references/input-sources.md` for how to mine it.
- **Description** — use directly when no artifact exists.

If a source you'd expect is missing, proceed with what you have and **record the gap** in the report — never block on a missing input.

## Workflow

1. **Resolve scope.** From the evidence, list the discrete testable behaviors and the platforms each touches. Map platforms to stacks and tooling using `references/monorepo-layout.md`. Note that **E2E tests live in a separate, private `test` repo** — never inside the platform repos — so E2E recommendations target that repo and existing E2E coverage may be unverifiable if it isn't checked out.

2. **Assess current coverage.** For each affected area, determine what is already tested and where. From a PR diff, note tests included in the change. From a CSV, bucket existing cases by apparent layer and automation status. From a repo checkout, grep the established test conventions. Distinguish _observed_ coverage from _assumed_ coverage.

3. **Assign the cheapest sufficient layer.** For each behavior, pick the lowest trophy layer that genuinely buys the needed confidence, with a one-line rationale. Prefer integration over E2E and unit over integration unless the behavior truly requires the higher layer (real browser/device, cross-service contract, full user journey). Name concrete tooling per platform (see `references/monorepo-layout.md`).

4. **Find the gaps and the imbalance.** Call out behaviors with no recommended coverage, and any existing shape that is trophy-wrong (e.g. E2E doing work integration should do, or untested core logic). Be explicit about what evidence each gap rests on.

5. **Write the HTML report.** Build a single self-contained HTML file (inline CSS, no external/CDN dependencies, no JS required) following `references/html-report-template.md`. Write it to the **current working directory** as `test-stack-report-<slug>-<date>.html`, where `<slug>` is a short kebab-case identifier for the change (ticket key, PR number, or feature name) and `<date>` is the caller-provided date. Report sections, in order: Summary & recommended shape; Evidence & sources (with what was missing); Per-platform recommendations (behavior → layer → tooling → rationale); Coverage gaps; and a placeholder **Adversarial Review** section the counterpart skill fills in.

6. **Hand off for adversarial review.** Your recommendation is not final until `challenging-test-stack-recommendations` has red-teamed it. When invoked under the orchestrator this happens automatically; when invoked standalone, tell the user the adversarial pass is available and recommended.

## Principles

- **Ground every recommendation.** Each behavior→layer call ties to a specific requirement, diff hunk, CSV row, or observed test. Mark anything inferred without evidence as an assumption.
- **Cheapest sufficient layer wins.** Confidence pushed down the trophy is cheaper to write, faster to run, and less flaky.
- **Per-platform, not one-size.** A feature spanning server, web, and mobile gets a distinct shape per platform — their stacks and risks differ.
- **Honesty about coverage.** Never present assumed coverage as verified. "I could not inspect the `test` repo" is a finding, not a failure.
