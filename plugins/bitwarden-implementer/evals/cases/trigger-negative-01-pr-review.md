# trigger-negative-01: PR review of a teammate's work

## Input

> Review PR #12345 — check for code quality issues and anything that might bite us in production.

## Expectations

- Agent does NOT activate as `bitwarden-implementer`.
- Response routes to `bitwarden-code-review` or the review skill set.

## Pass criteria

- **Trigger:** `bitwarden-implementer` is not selected.
- **Behavior:** `bitwarden-code-review` or a review-oriented skill is referenced instead.
