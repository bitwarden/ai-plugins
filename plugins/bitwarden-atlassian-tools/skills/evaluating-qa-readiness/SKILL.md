---
name: evaluating-qa-readiness
description: Use whenever someone wants to check whether a Jira ticket is ready to hand to QA — "Is PROJ-123 ready for QA?", "QA-check PROJ-123", "Does PROJ-123 have everything QA needs?", "Review PROJ-123 before I move it to Ready for QA", "Is this story ready to test?", or any request to validate that a story/bug has the information a tester needs before testing starts. Reads the ticket via the read-only Atlassian MCP and reports, per objective criterion, what QA needs that is present or missing — feature flag state, testing instructions, implementation notes, acceptance criteria, affected clients, and a linked PR/build — plus a ready-to-paste comment the developer can act on. Use this proactively when a developer says they are moving a ticket to Ready for QA, even if they don't say "QA readiness."
---

# Evaluating QA Readiness

When a ticket moves to **Ready for QA**, the tester should not have to hunt down the developer to learn how to test it. This skill checks a Jira ticket for the concrete, objectively-verifiable pieces of information QA needs _before_ testing starts, so gaps get fixed by the implementer instead of turning into back-and-forth later.

**This is a completeness check, not a quality judgment.** You are checking whether the _information_ a tester needs is present and usable — not whether the fix is correct, whether the acceptance criteria are good, or whether the design is right. Those are QA's and the team's calls. Staying inside that boundary is what keeps this check objective and trustworthy: a developer should be able to look at any "missing" flag and agree it's genuinely absent.

## Workflow

### Step 1: Read the ticket

Use the `get_issue` MCP tool with the issue key. It defaults to expanding `renderedFields` and `names`, giving you HTML-rendered field values and human-readable custom-field display names — you need both, because feature-flag and implementation info often live in custom fields, not the description.

Then use `get_issue_comments` — developers frequently drop testing steps, flag names, or "how to test" notes in a comment rather than editing the description. Treat comments as a first-class source, not an afterthought.

If the description or comments reference a PR, build, or Confluence page, note it; use `get_issue_remote_links` to catch linked PRs and pages that aren't inline. You are looking for _evidence that the information exists somewhere on the ticket_, wherever the developer put it.

### Step 2: Evaluate each criterion

Judge each criterion against everything you gathered — description, all custom fields, comments, and links. For each, decide one of:

- **Present** — the information is there and a tester could act on it.
- **Missing** — no trace of it anywhere on the ticket.
- **Unclear** — something is there but it's ambiguous or incomplete (e.g. a flag is mentioned but not its name, or "test the usual flows" with no steps). Treat unclear as a gap worth flagging, but describe _what_ is ambiguous rather than just calling it absent — that's more actionable and more fair to the developer.

Read the criteria definitions and what counts as satisfied in `references/criteria.md`. In short:

**Blocking** (a tester is genuinely stuck without these):

1. **Testing instructions** — how to validate the change: setup/preconditions, steps, and expected result. For a bug, this includes what "fixed" looks like versus the original broken behavior.
2. **Implementation notes** — what was changed and where, at enough detail for a tester to know what surface area to exercise.
3. **Feature flag** — whether the change sits behind a flag. If it does, the flag's name/key **and** the state QA needs it in (on/off) to test. If it doesn't, the ticket should say so — "not behind a flag" is a valid, passing answer. Silence is the gap, because the tester otherwise can't tell whether they're testing the right thing.

**Non-blocking** (QA can usually start, but these save round-trips):

4. **Acceptance criteria** — a testable statement of what the change should do.
5. **Affected clients/platforms** — which clients (web, browser extension, desktop, mobile, CLI) / OSes / browsers are in scope, so QA tests the right surfaces.
6. **Linked PR or build** — a PR link or a build/version where the change can actually be exercised.

Distinguishing blocking from non-blocking matters: a ticket missing only a PR link is _nearly_ ready and shouldn't be treated the same as one with no testing instructions at all. The verdict should reflect that difference so developers fix the things that actually stop testing first.

### Step 3: Report

Use this structure:

```
## QA Readiness: <ISSUE-KEY> — <summary>
**Verdict:** Ready for QA | Not ready — N blocking gap(s) | Nearly ready — N non-blocking gap(s)

| Criterion | Status | Notes |
|---|---|---|
| Testing instructions | ✅ Present / ❌ Missing / ⚠️ Unclear | <evidence or what's missing> |
| Implementation notes | ... | ... |
| Feature flag | ... | ... |
| Acceptance criteria | ... | ... |
| Affected clients/platforms | ... | ... |
| Linked PR/build | ... | ... |
```

Rules for the verdict:

- **Not ready** if any _blocking_ criterion is Missing or Unclear.
- **Nearly ready** if all blocking criteria pass but one or more _non-blocking_ ones don't.
- **Ready for QA** only if everything passes.

In the Notes column, cite the evidence when something passes (where you found it — "steps in description", "flag name in comment by @dev") and state specifically what's absent when it doesn't. Vague notes ("needs more detail") aren't actionable; "no expected result given for the reset-password step" is.

### Step 4: Draft the developer ask

If there are any gaps, produce a short comment the QA (or the tool user) can paste onto the ticket to ping the developer. Address only the gaps — don't restate what's already there. Keep it collegial and specific; the goal is to make it trivial for the developer to fill the holes:

```
Before this is ready for QA, could you add:
- **Feature flag:** is this behind a flag? If so, which flag and what state should it be in to test?
- **Testing instructions:** steps to validate, including expected result.
```

If nothing is missing, say so plainly and skip the draft comment — no need to manufacture busywork.

## Boundaries and honesty

- The Atlassian MCP here is **read-only**. You cannot post the comment or change the ticket — you produce the draft for a human to post. Say so if the user expects it to be posted.
- If `get_issue` fails or the key doesn't exist, report that plainly rather than guessing at contents.
- Never infer that a criterion is satisfied from the issue _type_ or _status_ alone. A ticket marked "Ready for QA" is exactly the case where you should still check — that status is the claim you're verifying, not evidence.
- If a custom field name suggests it holds relevant info (anything mentioning "flag", "test", "QA", "implementation", "platform") but it's empty, that's a Missing signal worth noting by name.

## Examples

### examples/sample_evaluation.md

A worked example: reading a Story, finding testing steps in a comment but no feature-flag information, and producing the report plus a targeted developer ask.
