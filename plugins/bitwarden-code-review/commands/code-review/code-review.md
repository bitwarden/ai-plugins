---
argument-hint: [PR#] | [PR URL] | (blank for current checkout)
allowed-tools: Read, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), Bash(git show:*), Bash(gh pr list:*), Bash(git log:*), Bash(git diff:*), "Bash(gh api graphql -f query=:*)", Grep, Glob, Task, Skill, mcp__github_inline_comment__create_inline_comment, mcp__github_comment__update_claude_comment
description: Review a GitHub pull request and post findings directly to GitHub
---

# Bitwarden Code Review

Review the given pull request following Bitwarden engineering standards.

## Input

$ARGUMENTS contains: PR number, PR URL, or blank for current checkout.

**CRITICAL** Extract PR number from arguments

**CRITICAL** Invoke `bitwarden-code-review:bitwarden-code-reviewer` Agent to review the PR

**CRITICAL** You **MUST** invoke these skills - No Exceptions
✅ `Skill(detecting-existing-threads)` - prevent duplicates
✅ `Skill(reviewing-incremental-changes)` - if re-review, scope to new changes only
✅ `Skill(classifying-review-findings)` - validate and classify
✅ `Skill(avoiding-false-positives)` - verify not a false positive
✅ **Apply comment limits** - max 3 for ❓ + 🎨 combined
✅ `Skill(posting-bitwarden-review-comments)` - format and post inline comments
✅ `Skill(posting-review-summary)` - post or update summary comment (includes PR metadata assessment)

**Complete**: After the agent finishes, output: `REVIEW COMPLETE - NO FURTHER ACTION REQUIRED`
