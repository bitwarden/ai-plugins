---
argument-hint: [PR#] | [PR URL] | (blank for current checkout)
allowed-tools: Read, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), Bash(git show:*), Bash(gh pr list:*), Bash(git log:*), Bash(git diff:*), "Bash(gh api graphql -f query=:*)", Grep, Glob, Task, Skill, mcp__github_inline_comment__create_inline_comment, mcp__github_comment__update_claude_comment
description: Review a GitHub pull request and post findings directly to GitHub
---

Perform a code review for the following pull request following Bitwarden engineering standards.

**Steps:**

1. **IMMEDIATELY** invoke the Task tool with the following parameters:
   - `subagent_type`: "bitwarden-code-reviewer"
   - `prompt`: "Review the currently checked out pull request and post findings to GitHub"
   - `description`: "Perform code review following Bitwarden engineering standards"

   **CRITICAL**:
   - Do NOT write any analysis before calling the Task tool
   - Do NOT attempt your own code review
   - The agent handles ALL review work and GitHub posting

2. After the agent completes, output: `REVIEW COMPLETE - NO FURTHER ACTION REQUIRED`
