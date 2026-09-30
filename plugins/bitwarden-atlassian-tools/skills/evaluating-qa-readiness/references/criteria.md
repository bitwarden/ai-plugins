# QA Readiness Criteria

Detailed definitions of what each criterion checks and what counts as satisfied. The guiding question for every criterion is the same: **can a tester who has never spoken to the developer act on this?** If yes, it's present. If they'd have to ask a follow-up question to proceed, it's a gap.

These criteria check for the _presence and usability of information_, never the correctness of the work.

## Blocking criteria

A tester is genuinely stuck — or at high risk of testing the wrong thing — without these. Any one of them missing or unclear means the ticket is **not ready**.

### 1. Testing notes

Testing notes are a callout, not a script. Testers know how to exercise routine functionality; what they need from the developer is what to focus on and anything they wouldn't otherwise know.

**Satisfied when** a tester can tell what to validate — from a QA notes field, a comment, or the description together with the AC — and anything non-obvious is called out. Examples of things worth a callout: special setup or seed data, async/batched/scheduled processing (so "still running" isn't mistaken for "broken"), cloud vs. self-hosted differences, or a regression area outside the obvious surface.

For a **bug**, what "fixed" looks like should be clear, so the tester can confirm the specific fix rather than a general smoke test.

**Do not flag as a gap**: the absence of numbered steps, exact tool/table/query names, or timings, when the notes already identify the area and the expected outcome. "Delete an org and confirm its event logs are removed; deletion is batched so large orgs take longer" is Present.

**Not satisfied by**: nothing at all, or "test the feature" / "verify it works" with no indication of what the feature does or what outcome to expect.

### 2. Implementation notes

**Satisfied when** the ticket says what was changed and roughly where, at a level that tells QA what surface area to exercise and where regressions might hide. Examples: "changed the vault-item export to stream instead of buffering; touches the web and desktop export dialogs", or "fixed null-check in the autofill matcher for URLs without a scheme."

**Not satisfied by**: a PR link _alone_ with no summary — QA shouldn't have to read a diff to learn what to test. A one-line summary plus the PR link is fine.

### 3. Settled scope

**Satisfied when** there's no open question about what the ticket covers. Most tickets pass this without comment.

**Not satisfied when** a comment says the description is inaccurate or out of date, questions what's in scope, or records a scope change, and nothing afterwards (an edited description, updated AC, or a later comment giving the answer) resolves it. A tester working from the description would test the wrong thing, or wouldn't know whether a behavior is in or out of scope.

This checks whether the scope is _stated_, not whether it's the right scope. Cite the comment that raised the question and when, so the developer can find it.

### 4. Feature flag

**Satisfied when** the ticket makes the flag situation unambiguous:

- If the change is behind a flag: the flag's name/key **and** the state QA needs (enabled/disabled, and for which environment or account if relevant).
- If the change is not behind a flag: an explicit statement to that effect.

**Why silence is a gap**: without this, the tester can't tell whether the feature will even be visible in their environment, and a "passing" test against a flagged-off build is worse than no test. An explicit "not behind a flag" is a passing answer — the requirement is a clear answer, not a flag.

**Inference is allowed for state.** If exactly one flag is named for the change and no explicit on/off state is given, the reasonable default is "enable it to exercise the new behavior" — don't flag the state as a gap just because it wasn't spelled out. Only treat the state as genuinely Unclear when there's a real reason the correct state isn't obvious: multiple flags or environments that could behave differently, a flag that gates removal/deprecation (where "off" is the interesting state), or the ticket itself raises a question about rollout (e.g., cloud vs. self-hosted needing different treatment). The bar is "would a competent tester actually be stuck," not "is every detail spelled out."

## Non-blocking criteria

QA can usually begin without these, but each one that's missing tends to cause a round-trip mid-test. Flag them so they get fixed, but don't block the handoff on them alone.

### 5. Acceptance criteria

**Satisfied when** there's a testable statement of what the change should accomplish — the conditions the tester (and the team) agree define "done."

**Note the overlap with testing notes**: AC states what should be true; testing notes point at what to focus on and anything non-obvious. Strong AC often makes brief testing notes sufficient.

### 6. Affected clients / platforms

**Satisfied when** the ticket names which clients (web vault, browser extension, desktop, mobile, CLI) and, where it matters, which OSes or browsers are in scope. This lets QA test the right surfaces instead of guessing or over-testing.

**Not satisfied by**: an implicit assumption. "It's a server change" counts if stated; leaving platform scope unsaid does not.

### 7. Linked PR or build

**Satisfied when** there's a link to the PR or a specific build/version where the change can be exercised. This is what lets QA actually get their hands on the change.

**Partial credit**: a PR link is good; a link to an installable build or a named version QA can pull is better. Either satisfies the criterion.

**Where to look.** Most PRs are linked automatically by Jira's GitHub integration (branch naming or smart commits) and appear in the ticket's Development panel, not in the description or remote links. `get_issue` surfaces that panel as a **Development** entry under "Additional Fields" — e.g. `Pull requests: 1 (MERGED); Branches: 1`. A pull request count there satisfies this criterion; it gives counts and state, not URLs, which is fine. Also check the description, comments, and `get_issue_remote_links` for manually-added links.

**When nothing turns up.** If there's no Development entry and no link anywhere else, report it Missing. If the ticket clearly has code work (status past In Progress, a testing branch set) but the output has no Development entry at all, say the PR wasn't found rather than asserting none exists — some projects don't expose the field.

## Judgment notes

- **Where developers put things varies.** Some teams keep testing notes in a custom field, others in the description, others in a comment. Search all of them before calling something missing — a false "missing" erodes trust in the check faster than a missed gap.
- **Unclear is its own category.** When something is present but ambiguous (a flag mentioned but not named, notes with no expected outcome), say what specifically is ambiguous. That's more useful than a binary pass/fail and more fair to the developer.
- **Don't reward the ticket's status.** "Ready for QA" is the assertion under test, not evidence. Evaluate the content as if the status label weren't there.
