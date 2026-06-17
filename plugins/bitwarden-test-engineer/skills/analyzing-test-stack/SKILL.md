---
name: analyzing-test-stack
description: Use when recommending what test automation a feature, bugfix, or change needs and at which layer — analyzing a Jira ticket, GitHub PR, exported test-case CSV, technical breakdown, and/or plain-language description, then mapping each behavior to the cheapest sufficient Testing Trophy layer (unit, integration, E2E) per platform, risk-weighted by each behavior's defect severity (impact, not urgency), and emitting a self-contained HTML report. Triggers on "what tests should this have", "which test layers", "test stack", "test strategy", "test trophy", "test plan for this PR/ticket", "what should we test for this tech breakdown", "are these tests at the right level", "risk-based test coverage", "what tests does this Critical/High bug need", or "rank coverage gaps by severity".
allowed-tools: "Read, Write, Grep, Glob, AskUserQuestion, Skill, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), mcp__bitwarden-atlassian__get_issue, mcp__bitwarden-atlassian__search_issues, mcp__bitwarden-atlassian__get_issue_comments, mcp__bitwarden-atlassian__get_issue_remote_links, mcp__bitwarden-atlassian__get_confluence_page, mcp__bitwarden-atlassian__search_confluence, mcp__bitwarden-atlassian__search_confluence_cql"
---

# Analyzing the Test Stack

Recommend the test automation layers a change should ship with, shaped as a **Testing Trophy**, and write the recommendation as a self-contained HTML report. You produce advice, not tests.

The Testing Trophy (read `references/testing-trophy.md` for the full model): a focused **unit** layer for pure logic and edge cases, a **heavy integration** layer where most confidence is bought, and a **thin E2E** layer reserved for critical end-to-end journeys. The guiding rule is _write tests at the cheapest layer that still buys the confidence the behavior requires_ — push coverage down the trophy, not up.

## Inputs

You may receive any combination of: a Jira key, a GitHub PR, a CSV export of test cases, a technical breakdown document, and/or a plain-language description. Treat them as additive evidence. You also consume a **coverage inventory** — the existing-test records produced by the `assessing-test-coverage` skill (permalink records + `unverified` gaps). Under the `bitwarden-test-engineer` agent this is gathered for you before this skill runs; if it is absent (e.g. run standalone), invoke `Skill(assessing-test-coverage)` for the affected change surface, or proceed and record all coverage as `unverified`. **Today's date is provided by the caller** — use it for the report filename; do not attempt to read the clock. If no date is supplied, ask via `AskUserQuestion` rather than guessing.

`../../references/input-sources.md` (a plugin-level reference shared with `assessing-test-coverage`) is the canonical guide for how to ingest each source — Epic expansion, breakdown mining, CSV column mapping, and the rule that a missing source is recorded as a gap rather than blocking the analysis. At a glance:

- **Jira** — extract testable behaviors and acceptance criteria; Epics/Features expand to their children before extraction.
- **GitHub PR** — extract the change surface, API touched, and any tests already present.
- **CSV** — bucket rows by apparent layer and automation status.
- **Technical breakdown** — often the richest single input; its scope checklist already enumerates the platforms and surfaces.
- **Description** — use directly when no artifact exists.

If a source you'd expect is missing, proceed with what you have and **record the gap** in the report — never block on a missing input.

Alongside the behaviors, carry each behavior's **risk severity** — the impact a defect in it would have, per Bitwarden's severity guide. `references/severity-risk.md` is the canonical model: where severity comes from (the Jira severity field for bugs; an assessment against the guide's criteria for features/PRs/breakdowns) and how it calibrates the recommendation. Severity is the dial that turns "cheapest sufficient layer" into a risk-weighted call — it decides how completely a behavior must be covered and how hard a missing test counts as a gap. Weight by severity (impact), not priority (urgency). **Security-sensitive behaviors (crypto, auth, threat-model-relevant paths) are at least Critical regardless of the guide's table** — see the reference's source-of-truth note.

## Workflow

1. **Resolve scope.** From the evidence, list the discrete testable behaviors and the platforms each touches. Map platforms to stacks, tooling, and the layer→repo split (including the sibling `test` repo for E2E) using `references/monorepo-layout.md`. **When the input is an Epic**, the behaviors come from the children's acceptance criteria and the diffs of any PRs linked from those children — record which children/PRs you actually inspected vs. only enumerated.

2. **Consume the coverage inventory.** What is already tested is established by the `assessing-test-coverage` skill, not here — take its inventory as input: the permalink records for observed tests (each `{ path, line range, owner_repo, sha, layer, permalink }`, or path-only with an `unlinkable` reason) and the `unverified` gaps. Treat _observed_ coverage as verified and everything else as a gap, never assumed covered. If no inventory was supplied, invoke `Skill(assessing-test-coverage)` for the affected change surface to produce one; do not re-derive coverage-finding or permalink rules here (they live in that skill's `references/finding-coverage.md`). These records feed both the report's Evidence column and the gap analysis below.

3. **Assign the cheapest sufficient layer, weighted by severity.** For each behavior, pick the lowest trophy layer that genuinely buys the needed confidence, with a one-line rationale — then check the confidence bar against the behavior's risk severity per `references/severity-risk.md`. Severity sets _how much_ confidence is sufficient, not _which_ layer: a Critical behavior must cover its material failure modes (and, if it is a genuine end-to-end critical flow, claim the thin E2E layer the trophy reserves for exactly that), while a Low behavior earns minimal coverage and never an E2E test. Prefer integration over E2E and unit over integration unless the behavior truly requires the higher layer (real browser/device, cross-service contract, full user journey). Name concrete tooling per platform (see `references/monorepo-layout.md`).

4. **Find the gaps and the imbalance, ranked by severity.** Call out behaviors with no recommended coverage, and any existing shape that is trophy-wrong (e.g. E2E doing work integration should do, or untested core logic). **Order gaps by severity** — a Critical behavior with no observed coverage is a top-priority gap and leads the list; Informative behaviors are recorded as out-of-scope rather than gaps. Be explicit about what evidence each gap rests on.

5. **Write the HTML report.** Build a single self-contained HTML file (inline CSS, no external/CDN dependencies, no JS required) following `references/html-report-template.md`. **Inline the canonical stylesheet from `../../references/report-style-tokens.md` verbatim** — the plugin-level styling source shared with the coverage report; do not re-pick colors, fonts, or layer tokens; the off-brand data-report visual system and the layer/badge mappings in that file are binding. Use the normative section IDs (`#overview`, `#summary`, `#evidence`, `#recommendations`, `#gaps`). Write `#overview` yourself as a short top-of-report synthesis: a 2–4 sentence recap of the recommended shape per platform, the top 3 open risks the reader should resolve before acting (drawn from `#gaps`, **highest severity first**), and anchor links into `#recommendations` and `#gaps`. The per-platform recommendations table carries a **Severity** column per behavior. Write the report to the **current working directory** as `test-stack-report-<slug>-<date>.html`, where `<slug>` is a short kebab-case identifier for the change (ticket key, PR number, or feature name) and `<date>` is the caller-provided date. The Per-platform recommendations table's Evidence column must contain a GitHub permalink (or an explicit `unlinkable` note) for every cited existing test.

## Principles

- **Ground every recommendation.** Each behavior→layer call ties to a specific requirement, diff hunk, CSV row, or observed test. Mark anything inferred without evidence as an assumption.
- **Cheapest sufficient layer wins.** Confidence pushed down the trophy is cheaper to write, faster to run, and less flaky.
- **Severity sets the bar, not the layer.** Weight each behavior's coverage by the impact a defect in it would have, per `references/severity-risk.md` — severity decides how completely a behavior is covered and how high its gap ranks, never which layer is "cheapest sufficient." It is impact, not priority (urgency).
- **Per-platform, not one-size.** A feature spanning server, web, and mobile gets a distinct shape per platform — their stacks and risks differ.
- **Honesty about coverage.** Never present assumed coverage as verified. "I could not inspect the `test` repo" is a finding, not a failure.
