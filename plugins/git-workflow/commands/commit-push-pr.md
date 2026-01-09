---
allowed-tools: Read, Bash(git checkout -b:*), Bash(git add:*), Bash(git status:*), Bash(git push:*), Bash(git commit:*), Bash(gh pr create:*)
description: Commit, push, and open a PR
---

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`

## Your task

Based on the above changes:

1. Create a new branch if on main
2. Create a single commit with an appropriate message
3. Push the branch to origin
4. Read the PR template at `.github/PULL_REQUEST_TEMPLATE.md`
5. Create a pull request using `gh pr create` with:
   - Title: Ask the user for the Jira ticket URL (from bitwarden.atlassian.net) and extract the ID (e.g., "PM-1" or "CL-1000"). Then use that ID to form the title in the format "[JIRA-ID] Short descriptive title"
   - Body: Following the template structure with the tracking link in the 🎟️ Tracking section and auto-generated objective in the 📔 Objective section
6. You have the capability to call multiple tools in a single response. You MUST do all of the above in a single message. Do not use any other tools or do anything else. Do not send any other text or messages besides these tool calls.
