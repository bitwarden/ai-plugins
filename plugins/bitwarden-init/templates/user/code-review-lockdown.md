## Code Review Rules

### Mutations — locked down by default

**NEVER** perform any of these mutations against a GitHub PR, regardless of which skill is running:

- Close, merge, or reopen a PR
- Publish a draft PR or convert a published PR to draft
- Approve, request changes, or submit any review status
- Alter labels, reviewers, assignees, title, or description

### Data retrieval — READ-ONLY tools only

- **ALWAYS** use `gh pr diff`, `gh pr view`, `gh pr checks`, and `gh api` for PR data.
- **NEVER** use `WebFetch` or `WebSearch` to retrieve PR diffs, metadata, comments, or any GitHub PR content.
