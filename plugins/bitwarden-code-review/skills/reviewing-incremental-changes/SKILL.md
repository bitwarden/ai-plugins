---
name: reviewing-incremental-changes
description: Use this skill when re-reviewing a PR that already has comments or when responding to developer changes after initial review. Apply when PR threads exist or when reviewing force-pushed commits. Handles incremental reviews, detects addressed feedback, avoids duplicate comments, and focuses only on newly introduced issues.
---

# Reviewing Incremental Changes

## Scope Rules

| Scenario       | Review Scope                         | New Issues in Old Code? |
| -------------- | ------------------------------------ | ----------------------- |
| Initial review | All changed files                    | ✅ Yes                  |
| Re-review      | Only lines changed since last review | ❌ Prohibited           |

## Re-Review Requirements

1. Review ONLY files/lines changed since last review
2. Do not re-raise issues developer already addressed
3. Verify previous ❌ CRITICAL or ⚠️ IMPORTANT findings were actually fixed

## Responding After Human Replies

| Severity     | Action                                       |
| ------------ | -------------------------------------------- |
| ❌ CRITICAL  | May respond once if issue genuinely persists |
| ⚠️ IMPORTANT | May respond once if issue genuinely persists |
| ♻️ DEBT      | **NEVER** reopen                             |
| 🎨 SUGGESTED | **NEVER** reopen                             |
| ❓ QUESTION  | **NEVER** reopen                             |
