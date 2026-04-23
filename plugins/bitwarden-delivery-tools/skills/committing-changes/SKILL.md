---
name: committing-changes
description: Git commit conventions and workflow for Bitwarden repositories. Use when committing code, writing commit messages, or preparing changes for commit. Triggered by "commit", "git commit", "commit message", "prepare commit", "stage changes".
---

# Git Commit Conventions

## Commit Message Format

```
[PM-XXXXX] <type>: <imperative summary>

<optional body explaining why, not what>
```

### Rules

1. **Ticket prefix**: Always include `[PM-XXXXX]` matching the Jira ticket
2. **Type keyword**: Select from the table below. The keyword drives automatic `t:` label assignment via CI (`.github/scripts/label-pr.py` reads `.github/label-pr.json`). CI matches `<type>:` or `<type>(` in the lowercased title.

| Type           | Label               | Use for                                    |
| -------------- | ------------------- | ------------------------------------------ |
| `feat`         | `t:feature`         | New features or functionality              |
| `fix`          | `t:bug`             | Bug fixes                                  |
| `refactor`     | `t:tech-debt`       | Code restructuring without behavior change |
| `chore`        | `t:tech-debt`       | Maintenance, cleanup, minor tweaks         |
| `test`         | `t:tech-debt`       | Adding or updating tests                   |
| `perf`         | `t:tech-debt`       | Performance improvements                   |
| `docs`         | `t:docs`            | Documentation changes                      |
| `ci` / `build` | `t:ci`              | CI/CD and build system changes             |
| `deps`         | `t:deps`            | Dependency updates                         |
| `llm`          | `t:llm`             | LLM/Claude configuration changes           |
| `breaking`     | `t:breaking-change` | Breaking changes requiring migration       |
| `misc`         | `t:misc`            | Changes that do not fit other categories   |

CI also accepts aliases (e.g., `revert`, `bugfix`, `cleanup`). See `.github/label-pr.json` for the full mapping. **If the type cannot be confidently determined, ask the user.**

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

## Pre-Commit Quality Gate

Before staging, run the `perform-preflight` skill for the full quality gate checklist (tests, lint, security, architecture). Consult the repo's CLAUDE.md for platform-specific build and lint commands.
