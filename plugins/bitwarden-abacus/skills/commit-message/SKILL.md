---
name: commit-message
description: Abacus land.commit slot for Bitwarden. Compose one commit's subject and body for a change Abacus is about to land, following bitwarden-delivery-tools:committing-changes, with settled rules for work that has no Jira ticket and for followup commits. Used by Abacus's land.commit workflow stage, not invoked by people directly.
allowed-tools: "Skill(bitwarden-delivery-tools:committing-changes)"
---

# Commit message (Abacus land.commit, Bitwarden)

Abacus calls this from its `land.commit` stage, which gives you the change, the bead's title, its source (the issue
or ticket the work tracks, or none) and each acceptance criterion with its evidence.

1. Invoke `Skill(bitwarden-delivery-tools:committing-changes)` and follow its commit message format, type keyword and
   body rules.
2. **The ticket prefix, settled here so the stage never stops to ask:**
   - When the bead's source is a Jira ticket (a key such as `PM-1234`, or a `bitwarden.atlassian.net/browse/` link),
     use that key: `[PM-1234]`.
   - Otherwise (a GitHub issue, any other link, or no source), drop the bracket entirely:
     `<type>: <imperative summary>`. Never invent a ticket key or write a placeholder in its place.
3. **Every commit uses the full format.** The skill's followup-commit exemption (a short summary with no prefix or
   body after a branch's first commit) does not apply here: Abacus lands unattended, so each commit it makes carries
   the ticket prefix (when there is a ticket), the type keyword and a body, whatever precedes it on the branch.
4. Compose the message only. The Abacus stage records it, and `abacus-finalize` commits it and appends Abacus's own
   trailers, so leave trailers out. Skip the skill's steps that act: the stage already settles the branch (it is
   Abacus's) and the pre-commit checks (the gate and the reviewer have run), and staging or committing belongs to
   `abacus-finalize`.

Pull request titles are not covered here. Abacus's `land.pr` slot uses
`bitwarden-delivery-tools:applying-pr-conventions`, which drops the bracket the same way when there is no ticket, so a
bead's commit subject and pull request title agree.
