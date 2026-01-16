---
name: detecting-existing-threads
description: Detects existing PR review threads to prevent duplicate comments. Use BEFORE posting any inline comments. Fetches resolved and open threads, then matches against planned findings.
---

# Detecting Existing Threads

## Purpose

Prevent duplicate comments by detecting existing review threads before posting new findings.

## Required Tools

- `Read` - Read pre-fetched thread data from `/tmp/pr-threads.json`
- `Bash(gh pr view:*)` - Get general PR comments (fallback)
- `Bash(gh api graphql -f query=:*)` - Get resolved and open review threads (fallback)

## Step 0: Check for Pre-fetched Thread Data

**FIRST**, check if thread data was already provided in your prompt context:

- Look for a `<threads>` section in your input/prompt
- If present, use that data directly - **DO NOT make API calls**
- Skip to "Thread Matching Logic" section

**SECOND**, if no `<threads>` section in prompt, use the Read tool to check for the file:

- Attempt to read `/tmp/pr-threads.json` using the Read tool
- If file exists: Use its contents, skip to "Thread Matching Logic"
- If Read returns an error (file not found): Continue to Step 1 (fetch via API)

**Why this matters**: In GitHub Actions, the workflow pre-fetches threads to avoid redundant API calls. This step ensures we use that data when available.

## Step 1: Determine PR Number (Fallback)

Use this priority order:

1. **GitHub Actions environment**:
   - Check `GITHUB_EVENT_PATH` environment variable
   - Extract PR number from event payload: `.pull_request.number`
   - Get repo from `GITHUB_REPOSITORY` ("owner/repo" format)

2. **Conversation context**:
   - Direct number: "123" → use 123
   - PR URL: extract from `https://github.com/org/repo/pull/456`
   - Text reference: "PR #789" → extract 789

3. **Local review mode**:
   - No PR number available → skip thread detection entirely

## Step 2: Fetch Thread Data (Fallback)

**Only execute this step if Step 0 found no pre-fetched data.**

Capture BOTH comment sources:

```bash
# General PR comments
gh pr view <PR_NUMBER> --json comments

# Inline review threads (resolved + open)
gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          startLine
          diffSide
          comments(first: 10) {
            nodes {
              id
              body
              author { login }
              createdAt
            }
          }
        }
      }
    }
  }
}
' -f owner="<OWNER>" -f repo="<REPO>" -F pr="<PR_NUMBER>"
```

## Step 3: Parse Into Structure

Build this JSON structure from merged results:

```json
{
  "total_threads": 5,
  "threads": [
    {
      "location": "src/auth.ts:45",
      "severity": "CRITICAL",
      "issue_summary": "SQL injection risk in query builder",
      "resolved": false,
      "author": "claude",
      "path": "src/auth.ts",
      "line": 45
    }
  ]
}
```

**Severity detection from emoji prefix:**

- ❌ → `CRITICAL`
- ⚠️ → `IMPORTANT`
- ♻️ → `DEBT`
- 🎨 → `SUGGESTED`
- ❓ → `QUESTION`

## Thread Matching Logic

Before creating any new comment, check for matches:

| Match Type   | Criteria                   | Action              |
| ------------ | -------------------------- | ------------------- |
| **Exact**    | Same file + same line      | Use existing thread |
| **Nearby**   | Same file + line within ±5 | Use existing thread |
| **Content**  | Body similarity >70%       | Use existing thread |
| **No match** | None of above              | Create new comment  |

## Handling Matches

- **Issue persists unchanged** → Respond in existing thread
- **Issue resolved** → Note resolution, don't re-raise
- **Issue evolved** → Create new comment explaining change
