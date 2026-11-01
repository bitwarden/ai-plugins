---
name: perform-preflight
description: Quality gate checklist to run before committing or creating a PR. Use when finishing implementation, checking work quality, or preparing to commit. Triggered by "preflight", "self review", "ready to commit", "check my work", "quality gate".
---

# Preflight Checklist

Run this checklist before committing or creating a PR. Consult the repo's CLAUDE.md for platform-specific commands (test runner, linter, formatter).

## Tests

- [ ] Run tests for affected modules (consult CLAUDE.md for commands)
- [ ] New code has test coverage
- [ ] No existing tests broken

## Code Quality

- [ ] Lint and format pass (consult CLAUDE.md for commands)
- [ ] No TODO comments without Jira ticket references
- [ ] Public APIs documented per repo convention (KDoc, DocC, XML docs, etc.)

## Bitwarden Security

- [ ] Zero-knowledge architecture preserved — no unencrypted vault data logged, persisted, or transmitted
- [ ] Sensitive data uses platform-appropriate secure storage (consult CLAUDE.md Security Rules)
- [ ] No sensitive data in log statements

## Architecture

- [ ] Changes follow patterns in CLAUDE.md and architecture docs
- [ ] Dependency injection and error handling follow repo convention
- [ ] String resources added to the correct location (if applicable)

## Owning-Team Review

Run this section when the branch changes a module another team owns in `CODEOWNERS`, and `bitwarden-owning-team-review` is installed.

- [ ] Run `/bitwarden-owning-team-review:classify-owning-team-review local`
- [ ] For each file that needs the owning team, contact that team with the classifier's explanation, or move the change out of this branch
- [ ] Split files that need only any engineer into their own PR when that keeps routine work out of the owning team's queue

A file that needs the owning team is not a failure. It means the owning team reviews that part of the change, and they hear about it before the PR opens rather than after.

## On Failure

If any check fails, fix the issue before proceeding. For test failures, diagnose the root cause rather than skipping. For lint/format failures, run the repo's auto-fix command if available. If a check cannot be resolved, flag it to the user with the specific failure output.
