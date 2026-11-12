---
name: composing-abacus-pull-requests
description: Abacus land.pr slot for Bitwarden. Compose one pull request's title, body and labels for a change Abacus is about to land, following bitwarden-delivery-tools:applying-pr-conventions, with the ai-review label settled so the stage never stops to ask. Used by Abacus's land.pr workflow stage, not invoked by people directly.
allowed-tools: "Skill(bitwarden-delivery-tools:applying-pr-conventions)"
user-invocable: false
---

# Pull request content (Abacus land.pr, Bitwarden)

Abacus calls this from its `land.pr` stage, which gives you the change, the bead's title, its source (the issue or ticket the work tracks, or none), each acceptance criterion with its evidence, the review outcomes, and what the pull request body must hold.

1. Invoke `Skill(bitwarden-delivery-tools:applying-pr-conventions)` as its caller, composing for one pull request, and follow its title format, type keyword, `t:` label and template body rules. Pass it the stage's review outcomes, so it appends the `## 🤖 AI-assisted review` section.
2. **The stage's body requirements win.** Where the `land.pr` stage says what the body must hold (the title and Tracking, the Objective, the gherkin acceptance criteria with their test-name comments, the AI-assisted review and Review guidance sections), that shape wins over the template wherever the two differ. Keep the template's section headers wherever the stage doesn't replace them.
3. **The AI review label, settled here so the stage never stops to ask:** the answer to "Would you like to add an AI review label to this PR?" is `ai-review`, and it belongs only on a pull request created as a draft. `abacus-finalize` opens every pull request as a draft, so return it in `labels` alongside the resolved `t:` label, and record the answer as `Would you like to add an AI review label to this PR?: ai-review, since Abacus opens it as a draft (settled by the Bitwarden Abacus profile, bitwarden-abacus-tools:composing-abacus-pull-requests)`. If the stage says the pull request will not open as a draft, leave `ai-review` out and record `No label` with that reason.
4. Compose the content only. The stage records the title, body, labels and answers, and `abacus-finalize` opens the pull request and applies the labels. Never run `git push`, `gh pr create`, `gh pr edit`, or a `gh label` command that writes, and skip any step of the skill that would.

The commit for the same bead comes from `bitwarden-abacus-tools:commit-message`, which drops the ticket bracket the same way `applying-pr-conventions` does when there is no ticket, so a bead's commit subject and pull request title agree.
