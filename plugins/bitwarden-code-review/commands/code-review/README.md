# Bitwarden Code Review Plugin

Automated code review for pull requests following Bitwarden engineering standards.

## Commands

### `/code-review [PR#]`

Review a pull request and post findings directly to GitHub.

**Arguments:**

- `PR#` — pull request number. Optional; when omitted the command resolves one from the workflow's `PR NUMBER:` line or a `pr_number` in the pre-fetched threads file.

If no number can be resolved from any of those, the command does not guess at the checkout — it reports that the pull request could not be identified. Use `/code-review-local` when you want the review written to local files instead of posted.

**What it does:**

- Analyzes all PR changes
- Checks for security issues, bugs, and standards violations
- Posts inline comments on specific lines
- Creates summary comment with findings
