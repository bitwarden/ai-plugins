---
name: committing-changes
description: Git commit conventions and workflow for Bitwarden repositories, including how to word a commit for a security-sensitive change. Use when committing code, writing commit messages, or preparing changes for commit. Triggered by "commit", "git commit", "commit message", "prepare commit", "stage changes", "security fix", "security commit", "VULN".
---

# Git Commit Conventions

## Branch Check

Resolve the repository's default branch from the remote rather than assuming `main`. If the current branch is the default, ask for a branch name before staging or committing. Offer to suggest one and confirm before switching. If the default branch cannot be resolved, say so and confirm the current branch is intended before staging.

## Commit Message Format

```
[PM-XXXXX] <type>: <imperative summary>

<optional body explaining why, not what>
```

### Rules

1. **Ticket prefix**: Always include `[PM-XXXXX]` matching the Jira ticket
2. **Type keyword**: Read `${CLAUDE_PLUGIN_ROOT}/references/change-type-labels.md` for the full table of conventional commit types and their CI label mappings. **If the type cannot be confidently determined, ask the user.**

### Examples

```
[PM-12345] feat: Add biometric unlock timeout configuration

Users reported confusion about when biometric prompts appear.
This adds a configurable timeout setting to the security preferences.
```

Ambiguous cases — choosing between similar types:

```
# Refactor that also fixes a bug? Use the primary intent:
[PM-12345] fix: Resolve null pointer in vault sync retry logic

# Test-only change:
[PM-12345] test: Add unit tests for biometric timeout edge cases
```

### Followup Commits

Only the first commit on a branch needs the full format (ticket prefix, type keyword, body). Subsequent commits can use a short, descriptive summary with no prefix or body required.

```
Update error handling in login flow
```

---

## Security-Sensitive Changes

Before writing the message, check whether the change is security-relevant, following `${CLAUDE_PLUGIN_ROOT}/references/security-sensitive-changes.md`. If it is, retrieve the canonical policy named there and apply it to how the summary, body, and any ticket reference are worded — don't write the message the way you otherwise would. If the change is security-relevant and the policy can't be fetched, honor the stop condition that reference defines: stop rather than writing a security-fix message from memory.

---

## Pre-Commit Quality Gate

Before staging, run the `perform-preflight` skill for the full quality gate checklist (tests, lint, security, architecture). Consult the repo's CLAUDE.md for platform-specific build and lint commands.
