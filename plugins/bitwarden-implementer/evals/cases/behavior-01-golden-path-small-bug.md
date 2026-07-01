# behavior-01: golden path — small real bug taken from board to PR

## Input

A real, small, well-scoped bug from a Bitwarden repo (server or client). Include the Jira ticket ID and a link to the breakdown doc if one exists. Fixture: choose a bug where the fix is under 50 LOC and does not span layers.

## Expectations

- Agent runs the full loop: Orient → Plan → Implement → Preflight → Self-review → Ship.
- Preflight passes (tests, lint, format).
- Self-review produces no critical/important findings, or produces some that are fixed before Ship.
- PR is opened with the conventional commit type prefix and `ai-review` label.

## Pass criteria

- **Structure:** all six phases visible in the transcript in order.
- **Behavior:** preflight passes on the final diff.
- **Behavior:** PR title starts with `[PM-XXXXX] <type>:` and body matches the repo's PR template.
- **Behavior:** `ai-review` label applied via `creating-pull-request`.

## Runs

| Run | Structure | Preflight | PR shape | Notes |
| --- | --------- | --------- | -------- | ----- |
| 1   |           |           |          |       |
| 2   |           |           |          |       |
| 3   |           |           |          |       |
