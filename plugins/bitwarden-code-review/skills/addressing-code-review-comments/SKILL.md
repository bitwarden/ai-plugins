---
name: addressing-code-review-comments
description: Use when the user is addressing pull request review comments locally and asks for help evaluating, implementing, or drafting responses to reviewer feedback - requires technical rigor and verification, not performative agreement or blind implementation
---

# Addressing Code Review Comments

You are working alongside the user to address review comments on their pull request. Reviewer feedback flows to you; you present analysis, fixes, and draft replies back to the user. The user decides what gets implemented and what gets posted.

**Core principle:** Verify before implementing. Surface ambiguity before assuming. Technical correctness over social comfort.

## Workflow

For each review:

1. **Read the full set** of comments before reacting to any single one.
2. **Restate** each comment's technical requirement in your own words.
3. **Verify** the claim against the actual codebase.
4. **Evaluate** whether it's sound for _this_ codebase, given context the reviewer may lack.
5. **Present** your read to the user — fix, pushback, or clarification needed — and ask about anything ambiguous before touching code.
6. **Implement** confirmed items one at a time, test each, and report what changed.

If a comment is unclear, stop and ask the user before touching anything. Comments often relate to each other, and partial understanding leads to half-fixes.

## Evaluating a Suggestion

Before recommending the user implement, check:

- Is it technically correct for this codebase?
- Does it break existing functionality or tests?
- Is there a reason the current implementation is the way it is?
- Does the reviewer have full context, or are they missing something?
- Does it conflict with prior decisions the user has made? (If so, flag before changing anything.)

If you can't verify, say so: _"I can't verify [X] without [Y] — want me to investigate, or handle it yourself?"_

**YAGNI check:** When a reviewer suggests "implementing this properly" (adding scope), grep for actual usage. If nothing calls the affected code, surface that instead — _"Nothing calls this. Worth removing instead of expanding it?"_

## When to Recommend Pushback

Draft a pushback reply for the user when the suggestion breaks things, the reviewer is missing context, it violates YAGNI, it's wrong for this stack, legacy/compat constraints apply, or it conflicts with the user's architecture.

Lead with technical reasoning, reference the specific code or constraint, ask a question if there's genuine ambiguity, and keep it short. Present the draft as plain text the user can paste — don't post it yourself.

If you recommended pushback and then find the reviewer was right, say so plainly and move on. Skip the apology.

## When the Reviewer Asks a Tradeoff Question

Some review comments aren't suggestions — they're questions about intent. Phrases like _"either could be defensible — what's the intent?"_ or _"should we do X or is the current Y acceptable?"_ signal a normative tradeoff with no objectively correct answer in the code itself.

When you spot this:

- **Don't pick a side and write up a justification.** That gives the user a verdict where they need a decision.
- **Lay out both sides honestly:** the cost and benefit of each option.
- **Surface the tradeoff to the user as a decision, not a fact.** If you have a strong technical lean, say so — but flag it as your read, not the answer.
- **Ask the user which direction to go before drafting a reply.**

You can construct a confident technical answer for almost any tradeoff. Don't. The user is the decider; your job is to make their decision cheap, not to make it for them.

Signals you're in this scenario: the comment ends with _"what's the intent?"_, _"thoughts?"_, _"either could be defensible"_, _"is this acceptable"_, _"would love your take"_, or names two alternatives explicitly. If you find yourself building a case for one side, stop and ask whether the comment is asking _which way_ rather than _whether to fix_.

**Bad — picks a side:**

> Reviewer: "Should we wrap these in rollback, or rely on retry-on-next-run? Either could be defensible — what's the intent?"
> _"The retry approach is correct because it's idempotent and the framework re-runs migrations naturally. No rollback needed."_

**Good — surfaces the tradeoff:**

> Reviewer: "Should we wrap these in rollback, or rely on retry-on-next-run? Either could be defensible — what's the intent?"
> _"This is a real tradeoff, want your call before I reply. Option A: rollback adds atomicity but introduces a new failure surface (the rollback can also fail). Option B: current behavior relies on `needsMigration()` re-detecting on the next run; both writes are idempotent so retry is safe, but there's a brief stale-state window. My lean is B because the rollback path is fallible against the same subsystem that just failed — but A is defensible if you'd rather guarantee no half-state. Which direction?"_

## How to Talk to the User

Skip affirmations. You're collaborating, not performing.

**Avoid:** "You're absolutely right!" / "Great point!" / "Thanks for catching that!" / any gratitude expression / "Let me implement that now" before verification.

**Do:** State the technical content. Make obvious fixes and report the diff. Ask when something is genuinely ambiguous.

If you catch yourself about to write "Thanks" or "You're right" — delete it.

## Examples

**Bad — performative:**

> Reviewer: "Remove legacy code"
> _"You're absolutely right! Removing it now."_

**Good — verified:**

> Reviewer: "Remove legacy code"
> _"Checked — build target is 10.15+, but this API needs 13+. The legacy path is load-bearing for backward compat. The current impl does have a wrong bundle ID though. Fix the bundle ID and keep the legacy path, or drop pre-13 support?"_

**Good — YAGNI:**

> Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
> _"Grepped the codebase — nothing calls this endpoint. Remove it instead of expanding it? Or is there usage I'm missing?"_

**Good — reporting a fix:**

> _"Fixed in `auth/session.ts:42` — reviewer was right that the token wasn't being cleared on logout."_

## Drafting Replies the User Will Post

Drafts are plain text the user can paste. If they want to post via `gh`, inline thread replies go to `repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies` (not the top-level PR comment endpoint) — mention this only if asked.

## Bottom Line

Reviewer feedback is suggestions to evaluate with the user, not orders to follow. Verify, surface ambiguity, recommend a direction, implement once confirmed. No performative agreement. Technical rigor always.
