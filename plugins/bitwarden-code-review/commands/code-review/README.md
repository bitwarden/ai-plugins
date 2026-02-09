# Bitwarden Code Review Plugin

Automated code review for pull requests following Bitwarden engineering standards.

## Commands

### `/code-review [PR#]`

Review a pull request and post findings directly to GitHub.

**Arguments:**

- `PR#` - Pull request number (optional, uses current checkout if omitted)
- `PR URL` - Full GitHub PR URL (optional)

**What it does:**

- Analyzes all PR changes
- Checks for security issues, bugs, and standards violations
- Posts inline comments on specific lines
- Creates summary comment with findings
