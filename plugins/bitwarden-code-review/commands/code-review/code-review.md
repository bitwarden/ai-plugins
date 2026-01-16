---
argument-hint: [PR#] | [PR URL] | (blank for current checkout)
allowed-tools: Read, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), Bash(git show:*), Bash(gh pr list:*), Bash(git log:*), Bash(git diff:*), "Bash(gh api graphql -f query=:*)", Grep, Glob, Task, Skill, mcp__github_inline_comment__create_inline_comment, mcp__github_comment__update_claude_comment
description: Review a GitHub pull request and post findings directly to GitHub
---

You must invoke the bitwarden-code-reviewer agent to perform a comprehensive code review of a GitHub pull request or local changes.

**Steps:**

1. **Check for pre-fetched thread context** (created by workflow):

   Use the Read tool to attempt reading `/tmp/pr-threads.json`:
   - If the file exists, capture its JSON content for the next step
   - If the file does not exist (Read returns an error), proceed without thread context (agent will fetch via API)

2. **Invoke the Task tool** with the following parameters:
   - `subagent_type`: "bitwarden-code-reviewer"
   - `description`: "Perform code review following Bitwarden engineering standards"
   - `prompt`: Use ONE of the following based on Step 1:

   **If `/tmp/pr-threads.json` existed**, include the thread data:

   ```
   Review the currently checked out pull request and post findings to GitHub.

   ## Existing PR Threads (Pre-fetched)

   The following threads already exist on this PR. Use this data to avoid duplicate comments.
   Do NOT re-fetch threads via API - this data is authoritative.

   <threads>
   [INSERT JSON CONTENT FROM /tmp/pr-threads.json HERE]
   </threads>
   ```

   **If file did NOT exist**, use the simple prompt:

   ```
   Review the currently checked out pull request and post findings to GitHub.
   ```

   **CRITICAL**:
   - Do NOT write any analysis before calling the Task tool
   - Do NOT attempt your own code review
   - The agent handles ALL review work and GitHub posting

3. After the agent completes, output: `REVIEW COMPLETE - NO FURTHER ACTION REQUIRED`
