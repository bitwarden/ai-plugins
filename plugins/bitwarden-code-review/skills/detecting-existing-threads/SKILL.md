---
name: detecting-existing-threads
description: Detects existing PR review threads to prevent duplicate comments. Use BEFORE posting any inline comments. Fetches resolved and open threads, then matches against planned findings.
---

# Detecting Existing Threads

## Purpose

Prevent duplicate comments by detecting existing review threads before posting new findings.

## Required Tools

- `Bash(gh pr view:*)` - Get general PR comments
- `Bash(gh api graphql*reviewThreads*-f owner=*-f repo=*-F pr=*:*)` - Get resolved threads
- `Bash(./scripts/get-review-threads.sh:*)` - Script wrapper

## Step 1: Determine PR Number

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

## Step 2: Fetch Thread Data

Capture BOTH comment sources:

```bash
# General PR comments
gh pr view <PR_NUMBER> --json comments

# Inline resolved review threads (REQUIRED - gh pr view misses these)
./scripts/get-review-threads.sh <PR_NUMBER> <OWNER> <REPO>
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
