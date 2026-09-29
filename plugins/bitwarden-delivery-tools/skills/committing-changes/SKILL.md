---
name: committing-changes
description: Git commit conventions and workflow for Bitwarden repositories. Use when committing code, writing commit messages, or preparing changes for commit. Triggered by "commit", "git commit", "commit message", "prepare commit", "stage changes".
allowed-tools: Skill(labeling-changes), Skill(applying-security-disclosure-policy)
---

# Git Commit Conventions

## Branch Check

Resolve the repository's default branch from the remote rather than assuming `main`. If the current branch is the default, ask for a branch name before staging or committing. Offer to suggest one and confirm before switching. If the default branch cannot be resolved, say so and confirm the current branch is intended before staging.

## Security-Sensitive Changes

Before writing the message, invoke `Skill(applying-security-disclosure-policy)` for this change. Say you are composing a commit message, and pass the current branch name and any ticket key you have. Skip the call when the caller passes a verdict it already settled, as `force-multiplier` does after its pilot. A settled `Yes` must come with its wording rules; if it doesn't, invoke the skill anyway.

Branch on the `Verdict:` line:

- **`Verdict: Stop`** — the policy couldn't be fetched. Stop, pass on the remedy it gives, and don't write the message from memory.
- **`Verdict: Yes`** — apply its wording rules to the summary, the body, and any ticket reference, then show the proposed message to the author for approval before committing. Skip the approval only when the caller says the author already approved this wording pattern.
- **`Verdict: No`** — write the message as usual.

The verdict holds for every commit on the change, followup commits included.

---

## Commit Message Format

```
[PM-XXXXX] <type>: <imperative summary>

<optional body explaining why, not what>
```

### Rules

1. **Ticket prefix**: Always include `[PM-XXXXX]` matching the Jira ticket
2. **Type keyword**: Invoke `Skill(labeling-changes)` to pick the conventional commit type.

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

Only the first commit on a branch needs the full format (ticket prefix, type keyword, body). Subsequent commits can use a short, descriptive summary with no prefix or body required. When the disclosure policy applied to the change, its wording rules still govern that summary.

```
Update error handling in login flow
```

---

## Pre-Commit Quality Gate

Before staging, run the `perform-preflight` skill for the full quality gate checklist (tests, lint, security, architecture). Consult the repo's CLAUDE.md for platform-specific build and lint commands.
