---
argument-hint: [PR#] | [PR URL] | (blank for current checkout)
allowed-tools: Read, Write, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), Bash(git show:*), Bash(gh pr list:*), Bash(git log:*), Bash(git diff:*), "Bash(gh api graphql -f query=:*)", Grep, Glob, Task, Skill, mcp__github_inline_comment__create_inline_comment, mcp__github_comment__update_claude_comment
description: Review a GitHub pull request and post findings directly to GitHub
---

You must invoke the bitwarden-code-review:bitwarden-code-reviewer agent to perform a comprehensive code review of a GitHub pull request or local changes.

**Steps:**

1. **Check for pre-fetched thread context** (created by workflow):

   Use the Read tool to attempt reading `/tmp/pr-threads.json`:
   - If the file exists, capture its JSON content for the next step
   - If the file does not exist (Read returns an error), proceed without thread context

2. **Detect sticky comment context** (for agent mode):

   The workflow may provide a sticky comment ID for updating a placeholder summary comment.
   Check these sources in order:

   a. **From prompt context:** Look for `STICKY COMMENT ID:` followed by a numeric ID in the surrounding prompt/arguments. Extract the ID.

   b. **From thread data fallback:** If not found above AND `/tmp/pr-threads.json` exists, search the general PR comments for a comment whose body contains `<!-- bitwarden-code-review -->`. Extract its `id`.

   If a sticky comment ID is found, you are in **agent mode** — include the sticky comment context in the agent prompt (see Step 3).

3. **Invoke the Task tool** with the following parameters:
   - `subagent_type`: "bitwarden-code-review:bitwarden-code-reviewer"
   - `description`: "Perform code review following Bitwarden engineering standards"
   - `prompt`: Build the prompt based on Steps 1 and 2:

   **If sticky comment ID was found (agent mode)**, include the sticky comment context:

   ```
   Review the currently checked out pull request and post findings to GitHub.

   ## Sticky Comment Context

   A placeholder summary comment (ID: [INSERT COMMENT ID]) exists on this PR with marker `<!-- bitwarden-code-review -->`.
   Write your final review summary to /tmp/review-summary.md using the Write tool.
   The workflow will update the placeholder comment with this file's contents.
   Do NOT use mcp__github_comment__update_claude_comment — it is not available in agent mode.
   ```

   **If `/tmp/pr-threads.json` existed**, also include the thread data:

   ```
   ## Existing PR Threads (Pre-fetched)

   The following threads already exist on this PR. Use this data to avoid duplicate comments.
   Do NOT re-fetch threads via API - this data is authoritative.

   <threads>
   [INSERT JSON CONTENT FROM /tmp/pr-threads.json HERE]
   </threads>
   ```

   **If neither sticky comment nor threads were found**, use the simple prompt:

   ```
   Review the currently checked out pull request and post findings to GitHub.
   ```

   **CRITICAL**:
   - Do NOT write any analysis before calling the Task tool
   - Do NOT attempt your own code review
   - The agent handles ALL review work and GitHub posting
