---
name: perform-preflight
description: Quality gate checklist to run before committing or creating a PR. Use when finishing implementation, checking work quality, or preparing to commit. Triggered by "preflight", "self review", "ready to commit", "check my work", "quality gate".
---

# Preflight Checklist

Run this checklist before committing or creating a PR. Consult the repo's CLAUDE.md for platform-specific commands (test runner, linter, formatter).

**Required before opening a PR:** the `/bitwarden-code-review:code-review-local` command must be run and its findings addressed. A PR is not ready to submit until this gate passes — see the Code Review section below.

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

## Code Review

Required before opening a PR — this is a submission blocker, not an optional step.

- [ ] Run `/bitwarden-code-review:code-review-local` over the change
- [ ] Review every finding it writes to the local review files
- [ ] Address CRITICAL and IMPORTANT findings, or record why each is being deferred
- [ ] Re-run after substantive changes so the review reflects what will actually be submitted

If you are preparing a PR and have not run `/bitwarden-code-review:code-review-local`, stop and run it before continuing.

## On Failure

If any check fails, fix the issue before proceeding. For test failures, diagnose the root cause rather than skipping. For lint/format failures, run the repo's auto-fix command if available. If a check cannot be resolved, flag it to the user with the specific failure output.
