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
- [ ] DI/injection and error handling follow repo convention
- [ ] String resources added to the correct location (if applicable)

## On Failure

If any check fails, fix the issue before proceeding. For test failures, diagnose the root cause rather than skipping. For lint/format failures, run the repo's auto-fix command if available. If a check cannot be resolved, flag it to the user with the specific failure output.
