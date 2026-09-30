---
name: evaluating-qa-readiness
description: Use whenever the user wants to check whether a Jira ticket is ready to hand to QA — "Is PROJ-123 ready for QA?", "QA-check PROJ-123", "Does PROJ-123 have everything QA needs?", or any request to validate that a story or bug has what a tester needs before testing starts. Reports which pieces are present or missing and posts a comment on the ticket asking the developer to fill the gaps. Use proactively when the user says they are moving a ticket to Ready for QA, even without the words "QA readiness."
allowed-tools: Read, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__add_issue_comment
---

# Evaluating QA Readiness

When a ticket moves to **Ready for QA**, the tester should not have to hunt down the developer to learn how to test it. This skill checks a Jira ticket for the concrete, objectively-verifiable pieces of information QA needs _before_ testing starts, so gaps get fixed by the implementer instead of turning into back-and-forth later.

**This is a completeness check, not a quality judgment.** Check whether the _information_ a tester needs is present and usable — not whether the fix is correct, whether the acceptance criteria are good, or whether the design is right. Those are QA's and the team's calls. Staying inside that boundary is what keeps this check objective and trustworthy: a developer should be able to look at any "missing" flag and agree it's genuinely absent.

## Workflow

### Step 1: Read the ticket

Use the `get_issue` MCP tool with the issue key. It defaults to expanding `renderedFields` and `names`, which surfaces HTML-rendered field values and human-readable custom-field display names — both matter, because feature-flag and implementation info often live in custom fields, not the description.

Then use `get_issue_comments` — developers frequently drop testing notes, flag names, or "how to test" notes in a comment rather than editing the description. Treat comments as a first-class source, not an afterthought.

For linked PRs, look first at the **Development** entry under "Additional Fields" in the `get_issue` output. It summarizes Jira's Development panel — the PRs, branches, commits, and builds the GitHub integration links automatically via branch naming or smart commits, which is how most PRs get linked (e.g. `Pull requests: 1 (MERGED); Branches: 1`). It carries counts and PR state, not URLs, and that is enough to count a PR as linked. Also note any PR, build, or Confluence page referenced in the description or comments, and use `get_issue_remote_links` to catch manually-added links. The goal is _evidence that the information exists somewhere on the ticket_, wherever the developer put it.

### Step 2: Evaluate each criterion

Judge each criterion against everything gathered — description, all custom fields, comments, and links. For each, decide one of:

- **Present** — the information is there and a tester could act on it.
- **Missing** — no trace of it anywhere on the ticket.
- **Unclear** — something is there but it's ambiguous or incomplete (e.g. a flag is mentioned but not its name, or "test the usual flows" with no expected outcome). Treat unclear as a gap worth flagging, but describe _what_ is ambiguous rather than just calling it absent — that's more actionable and more fair to the developer.

Read the criteria definitions and what counts as satisfied in `references/criteria.md`. In short:

**Blocking** (a tester is genuinely stuck without these):

1. **Testing notes** — enough for a tester to know what to validate, plus a callout for anything non-obvious (special setup or data, async or batched processing, environment differences). A step-by-step script is _not_ required; a QA note that describes the area to exercise, together with the AC, is sufficient. For a bug, what "fixed" looks like should be clear.
2. **Implementation notes** — what was changed and where, at enough detail for a tester to know what surface area to exercise.
3. **Settled scope** — no open question about what the ticket covers. If a comment says the description is wrong, out of date, or asks what's in scope, and neither the description, AC, nor a later comment resolves it, the tester doesn't know what to test.
4. **Feature flag** — whether the change sits behind a flag. If it does, the flag's name/key **and** the state QA needs it in (on/off) to test. If it doesn't, the ticket should say so — "not behind a flag" is a valid, passing answer. Silence on whether a flag exists at all is the gap. Silence on _state_ is not automatically a gap: if exactly one flag is named, default to assuming "enable it to test" and only flag the state as unclear when something about the ticket makes the right state genuinely ambiguous (see `references/criteria.md`).

**Non-blocking** (QA can usually start, but these save round-trips):

5. **Acceptance criteria** — a testable statement of what the change should do.
6. **Affected clients/platforms** — which clients (web, browser extension, desktop, mobile, CLI) / OSes / browsers are in scope, so QA tests the right surfaces.
7. **Linked PR or build** — a PR link or a build/version where the change can actually be exercised.

Distinguishing blocking from non-blocking matters: a ticket missing only a PR link is _nearly_ ready and shouldn't be treated the same as one with no testing notes at all. The verdict should reflect that difference so developers fix the things that actually stop testing first.

### Step 3: Report

Use this structure:

```
## QA Readiness: <ISSUE-KEY> — <summary>
**Verdict:** Ready for QA | Not ready — N blocking gap(s) | Nearly ready — N non-blocking gap(s)

| Criterion | Status | Notes |
|---|---|---|
| Testing notes | ✅ Present / ❌ Missing / ⚠️ Unclear | <evidence or what's missing> |
| Implementation notes | ... | ... |
| Settled scope | ... | ... |
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

For **Linked PR/build**, a Development entry with a pull request count is Present — cite it ("1 merged PR in Development panel"). If there is no Development entry and nothing in the description, comments, or remote links, it's Missing. The one hedge: if the `get_issue` output has no Development entry at all while the ticket plainly has code work (e.g. status past In Progress, a "Testing Branch" field set), say the PR wasn't found rather than asserting none exists, since some projects don't expose that field.

### Step 4: Draft the developer ask

If there are any gaps, write a short comment asking the developer to fill them. Address only the gaps — don't restate what's already there. Keep it collegial and specific; the goal is to make it trivial for the developer to fill the holes.

**Ask for the gap, not for exhaustive detail.** The ask should name what's missing, not dictate how thoroughly the developer must answer it. Don't demand step-by-step scripts, exact tool/table/query names, or timing specifics — a competent tester doesn't need a walkthrough of routine functionality, just a callout for anything non-obvious. And don't ask questions the ticket already lets you answer yourself — e.g. don't ask "what state should the flag be in?" when only one flag is named and "enable to test" is the obvious inference; ask about state only when it's genuinely ambiguous.

**Only include gaps that are real.** Before adding a line, ask whether the tester would actually be stuck without the answer. If not, leave it out of the comment even when the table marks it Unclear — a short comment with one real ask gets answered; a list of four with three nitpicks gets ignored.

**Write it as plain text.** `add_issue_comment` posts plain text, so Markdown (`**bold**`, `-` bullets, backticks) shows up literally on the ticket. Separate each ask with a blank line — the tool turns blank lines into separate paragraphs. Open with `QA readiness check:` so the developer knows where the comment came from and later runs can recognize it:

```
QA readiness check: before this is ready for QA, could you add the following?

Feature flag: is this behind a flag? If so, which one?

Scope: the April comment says the description is inaccurate. Could you update it (or add AC) so it's clear what's in scope?
```

If nothing is missing, say so plainly and don't post anything — no need to manufacture busywork.

### Step 5: Post the comment

Post the draft to the ticket with `add_issue_comment`, passing the issue key, the plain-text body, and `dryRun: false`. The tool defaults to a dry run, so without `dryRun: false` nothing is posted. QA shouldn't have to copy and paste the ask; posting it is the default.

Don't post when:

- **The user asked not to.** "Don't post", "just show me", "dry run", or "preview" means show the draft instead. If they asked for a preview, call the tool with `dryRun: true` and show the result.
- **The same ask is already on the ticket.** Check the comments from Step 1 for an earlier `QA readiness check:` comment. If it raised the same gaps and nothing after it answers them, don't post a duplicate. Say that the gaps were already raised, and when. If the gaps have changed since then, post a new comment covering only what's still open.

After posting, report it under the table: `Posted a comment on <ISSUE-KEY> (comment id <id>)`, followed by the comment text, so the user can see exactly what the developer received.

If the post fails, show the draft so the user can post it by hand, and say why it failed:

- **`Refusing to comment: ATLASSIAN_JIRA_WRITE_TOKEN is not set`** — this install is read-only. Say that setting a write-scoped token as `ATLASSIAN_JIRA_WRITE_TOKEN` lets the skill post comments itself (see the plugin README for scopes).
- **Any other error** — relay the tool's error message as returned, including any scope hint it adds.

## Boundaries and honesty

- The only write this skill makes is the one comment in Step 5. It never edits the ticket's fields, changes its status, or reassigns it, even when the verdict is Not ready.
- Post at most one comment per run.
- If `get_issue` fails or the key doesn't exist, report that plainly rather than guessing at contents. Never post a comment built from a ticket you couldn't read.
- Never infer that a criterion is satisfied from the issue _type_ or _status_ alone. A ticket marked "Ready for QA" is exactly the case where you should still check — that status is the claim you're verifying, not evidence.
- If a custom field name suggests it holds relevant info (anything mentioning "flag", "test", "QA", "implementation", "platform") but it's empty, note it by name. A clearly-relevant field left empty is Unclear rather than Missing — the ticket neither answers the question nor disclaims it.

## Examples

### examples/sample_evaluation.md

A worked example: a Bug whose PR is found through the Development field, whose single named flag is assumed enabled, and whose short QA note is accepted as enough, but which is not ready because a comment left the scope unresolved. Shows the report and the one-ask comment posted to the ticket.
