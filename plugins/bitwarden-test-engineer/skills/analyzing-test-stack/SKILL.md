---
name: analyzing-test-stack
description: Use when recommending what test automation a feature, bugfix, or change needs and at which layer — from a Jira ticket, GitHub PR, test-case CSV, technical breakdown, and/or plain-language description — mapping each behavior to the cheapest sufficient layer (unit, integration, E2E) inside each repo's actual test shape, risk-weighted by defect severity. Triggers on "test stack", "test strategy", "test plan for this PR/ticket", "which test layers should this have", or "what tests does this Critical/High bug need". This is the forward-looking recommendation — it does NOT inventory what already exists; for that, use assessing-test-coverage (whose inventory this skill consumes).
allowed-tools: "Read, Write, Grep, Glob, AskUserQuestion, Skill, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/build-report.sh:*), mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql"
---

# Analyzing the Test Stack

Recommend the test automation layers a change should ship with — shaped to **each target repo's actual test practice**, not one universal model — and write the recommendation as a self-contained HTML report. You produce advice, not tests.

Assign each behavior the **cheapest sufficient layer** (unit → integration → E2E, pushing coverage down) landed inside each repo's real shape (pyramid, trophy, or all-E2E). The layer model is in `references/test-layers.md`; the per-repo shapes in `references/monorepo-layout.md` → _Each repo's test shape in practice_.

## Inputs

You may receive any combination of: a Jira key, a GitHub PR, a CSV of test cases, a technical breakdown, and/or a plain-language description — additive evidence. You also consume a **coverage inventory** (the existing-test records produced by `assessing-test-coverage`: permalink records + `unverified` gaps). Under the `test-strategist` agent this is gathered before this skill runs; if it is absent (run standalone), invoke `Skill(assessing-test-coverage)` for the change surface, or proceed and record all coverage as `unverified`. **Today's date is provided by the caller** for the report filename — don't read the clock; if none is supplied, ask via `AskUserQuestion`.

`../../references/input-sources.md` (shared with `assessing-test-coverage`) is the canonical guide for ingesting each source — Epic expansion, breakdown mining, CSV column mapping, the Jira/Confluence tooling ladder, and the missing-source-is-a-gap rule.

Carry each behavior's **risk severity** (impact, not urgency) alongside it; the model and how it calibrates coverage are in `references/severity-risk.md`.

## Workflow

1. **Resolve scope.** From the evidence, list the discrete testable behaviors and the platforms each touches. Map platforms to stacks, tooling, and the layer→repo split (including the sibling `test` repo for E2E) using `references/monorepo-layout.md`. **When the input is an Epic**, the behaviors come from the children's acceptance criteria and the diffs of any PRs linked from those children — record which children/PRs you actually inspected vs. only enumerated.

2. **Consume the coverage inventory.** What is already tested is established by `assessing-test-coverage`, not here — take its inventory (one record per behavior plus `unverified` gaps; the record shape and permalink rules live in that skill's `references/finding-coverage.md` → _Output contract_) as input. Treat _observed_ coverage as verified and everything else as a gap, never assumed covered. If none was supplied, invoke `Skill(assessing-test-coverage)` for the change surface to produce one. These records feed both the report's Evidence column and the gap analysis below.

3. **Assign the cheapest sufficient layer, weighted by severity.** For each behavior, pick the lowest layer that genuinely buys the needed confidence (reach higher only for a real browser/device, cross-service contract, or full user journey), with a one-line rationale; then check that confidence bar against the behavior's risk severity per `references/severity-risk.md` (severity sets _how much_ confidence is sufficient, not _which_ layer). Land each call inside the **target repo's shape** and name its concrete tooling, both per `references/monorepo-layout.md` → _Each repo's test shape in practice_.

4. **Find the gaps and the imbalance, ranked by severity.** Call out behaviors with no recommended coverage, and any existing shape that is wrong for its repo (e.g. E2E doing work integration should do, untested core logic, or a layer the repo doesn't even maintain). **Order gaps by severity** — a Critical behavior with no observed coverage is a top-priority gap and leads the list; Informative behaviors are recorded as out-of-scope rather than gaps. Be explicit about what evidence each gap rests on.

5. **Render the HTML report** per `references/html-report-template.md` (which builds on the shared `../../references/report-template-common.md`) — mechanical formatting, not reasoning. Write `#overview` yourself: recommended shape per platform and the top 3 open risks from `#gaps`, highest severity first. The template owns everything else (section IDs, the Severity column, the Evidence permalinks, the `--kind test-stack` build, and the filename contract).

## Principles

- **Ground every recommendation** in a specific requirement, diff hunk, CSV row, or observed test; treat only _observed_ coverage as verified, and mark anything inferred as an assumption.
