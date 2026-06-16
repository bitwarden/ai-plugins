---
name: challenging-test-stack-recommendations
description: Use to red-team a test automation recommendation produced by analyzing-test-stack — adversarially reviewing a Testing Trophy recommendation or HTML test-stack report for anti-patterns and ungrounded claims before the team acts on it. Triggers on "challenge this test plan", "red-team the test recommendation", "poke holes in this test strategy", "is this proposed test plan over/under-testing", "review the test stack report", or runs automatically after analyzing-test-stack under the test-engineer orchestrator. Checks for ice-cream-cone (too E2E-heavy), unit-tests-masquerading-as-integration, over-testing trivial code, untestable requirements, missing platform layers, flaky-E2E candidates, and coverage claimed without evidence; returns a verdict of endorse, revise, or reject-with-reasons.
allowed-tools: "Read, Grep, Glob, Bash(gh pr view:*), Bash(gh pr diff:*), mcp__bitwarden-atlassian__get_issue, mcp__bitwarden-atlassian__get_issue_comments, mcp__bitwarden-atlassian__get_confluence_page"
---

# Challenging Test Stack Recommendations

You are the adversary to `analyzing-test-stack`. Your job is to **try to break its
recommendation** before the team builds on it. A recommendation that survives a genuine
red-team is trustworthy; one that was never challenged tends to drift toward whatever
tests are easiest to write rather than what actually buys confidence.

Default to skepticism. Your value is in the specific, evidence-backed objection — not in
rubber-stamping. But do not invent problems: an objection you cannot tie to evidence is
itself a rejected finding (you hold yourself to the same evidence bar you demand).

## Inputs

- The **HTML report** (or the recommendation text) from `analyzing-test-stack`.
- The **underlying evidence** — the same Jira ticket, PR diff, CSV, and/or repo checkout.
  Re-derive independently where you can; re-read the PR diff or ticket rather than trusting
  the report's summary of it.

## Workflow

1. **Re-read the evidence independently.** Don't take the report's characterization of the
   change at face value — pull the diff / ticket / CSV yourself and form your own view of
   the testable behaviors and where they live. Ingest each source the same way the analyst
   does (see `analyzing-test-stack/references/input-sources.md` for the CSV column mapping
   and Atlassian MCP tools). In particular, **E2E tests live in a separate, private `test`
   repo** — not inside the platform repos — so treat any existing-E2E-coverage claim as
   unverified unless that repo was actually inspected.

2. **Run the rejection criteria.** Apply every check in `references/adversarial-checklist.md`
   to each per-platform recommendation and to the overall shape. For each, decide: does the
   recommendation pass, or is there a concrete, evidence-backed objection?

3. **Test the grounding.** For every behavior→layer call, confirm it ties to real evidence.
   Flag any layer assignment, coverage claim, or "already tested" assertion that the
   evidence does not support — especially **E2E coverage claimed without inspecting the
   dedicated `test` repo**.

4. **Pressure the shape.** Step back from individual rows: is the overall trophy right? Too
   E2E-heavy (ice-cream cone)? Core logic pushed to slow layers? A whole platform's layer
   missing? Trivial code over-tested?

5. **Issue findings and a verdict.** Each finding: the specific claim challenged, why it's
   wrong or unsupported (with evidence), and the corrective recommendation. Then a single
   verdict:
   - **Endorse** — sound and well-grounded; minor or no notes.
   - **Revise** — directionally right but has specific fixable issues (list them).
   - **Reject-with-reasons** — the shape or grounding is wrong enough that the team should
     not act on it as written; state what a correct recommendation would require.

6. **Write the critique into the report.** Populate the report's `#adversarial-review`
   section with your findings and verdict (preserve the self-contained, no-external-deps
   HTML constraint). When run standalone without the orchestrator, return the critique as
   a clearly structured summary instead.

## Principles

- **Adversarial, not contrarian.** Push hard, but every objection carries evidence. Drop
  any finding you can't support — apply the analyst's own evidence standard to yourself.
- **Re-derive, don't trust.** The report's summary of the diff/ticket is a claim to verify,
  not a fact to accept.
- **Name the anti-pattern.** When you flag a shape problem, use the precise term
  (ice-cream-cone, over-unit-testing, E2E-for-branch-coverage) so the fix is unambiguous.
- **Unverifiable is a finding.** "The report claims E2E coverage exists but the `test` repo
  was never inspected" is a legitimate, important objection — surface it.
