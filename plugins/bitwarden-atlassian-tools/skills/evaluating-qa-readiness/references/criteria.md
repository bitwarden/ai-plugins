# QA Readiness Criteria

Detailed definitions of what each criterion checks and what counts as satisfied. The guiding question for every criterion is the same: **can a tester who has never spoken to the developer act on this?** If yes, it's present. If they'd have to ask a follow-up question to proceed, it's a gap.

These criteria check for the _presence and usability of information_, never the correctness of the work.

## Blocking criteria

A tester is genuinely stuck — or at high risk of testing the wrong thing — without these. Any one of them missing or unclear means the ticket is **not ready**.

### 1. Testing instructions

**Satisfied when** the ticket describes how to validate the change with enough specificity that a tester can follow it:

- Any setup or preconditions (account state, test data, org configuration) needed before the steps.
- The steps themselves, in order.
- The expected result — what the tester should observe if the change works.

For a **bug**, this means both the original broken behavior and what "fixed" looks like, so the tester can confirm the specific fix rather than a general smoke test.

**Not satisfied by**: "test the feature", "verify it works", or a link to steps that isn't accessible. Generic acceptance criteria are not the same as testing steps — AC says _what_ should be true, testing instructions say _how to check_.

### 2. Implementation notes

**Satisfied when** the ticket says what was changed and roughly where, at a level that tells QA what surface area to exercise and where regressions might hide. Examples: "changed the vault-item export to stream instead of buffering; touches the web and desktop export dialogs", or "fixed null-check in the autofill matcher for URLs without a scheme."

**Not satisfied by**: a PR link _alone_ with no summary — QA shouldn't have to read a diff to learn what to test. A one-line summary plus the PR link is fine.

### 3. Feature flag

**Satisfied when** the ticket makes the flag situation unambiguous:

- If the change is behind a flag: the flag's name/key **and** the state QA needs (enabled/disabled, and for which environment or account if relevant).
- If the change is not behind a flag: an explicit statement to that effect.

**Why silence is a gap**: without this, the tester can't tell whether the feature will even be visible in their environment, and a "passing" test against a flagged-off build is worse than no test. An explicit "not behind a flag" is a passing answer — the requirement is a clear answer, not a flag.

## Non-blocking criteria

QA can usually begin without these, but each one that's missing tends to cause a round-trip mid-test. Flag them so they get fixed, but don't block the handoff on them alone.

### 4. Acceptance criteria

**Satisfied when** there's a testable statement of what the change should accomplish — the conditions the tester (and the team) agree define "done."

**Note the overlap with testing instructions**: AC is the _what_, instructions are the _how_. A ticket can have strong AC and still be missing steps, or vice versa. Evaluate them independently.

### 5. Affected clients / platforms

**Satisfied when** the ticket names which clients (web vault, browser extension, desktop, mobile, CLI) and, where it matters, which OSes or browsers are in scope. This lets QA test the right surfaces instead of guessing or over-testing.

**Not satisfied by**: an implicit assumption. "It's a server change" counts if stated; leaving platform scope unsaid does not.

### 6. Linked PR or build

**Satisfied when** there's a link to the PR or a specific build/version where the change can be exercised. This is what lets QA actually get their hands on the change.

**Partial credit**: a PR link is good; a link to an installable build or a named version QA can pull is better. Either satisfies the criterion.

## Judgment notes

- **Where developers put things varies.** Some teams keep testing steps in a custom field, others in the description, others in a comment. Search all of them before calling something missing — a false "missing" erodes trust in the check faster than a missed gap.
- **Unclear is its own category.** When something is present but ambiguous (a flag named with no state, steps with no expected result), say what specifically is ambiguous. That's more useful than a binary pass/fail and more fair to the developer.
- **Don't reward the ticket's status.** "Ready for QA" is the assertion under test, not evidence. Evaluate the content as if the status label weren't there.
