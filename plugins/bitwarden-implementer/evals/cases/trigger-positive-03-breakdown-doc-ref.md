# trigger-positive-03: breakdown-doc fallback path (user cannot provide a Jira key)

## Input

> I don't have a Jira key handy but the work is task 4 in bitwarden/tech-breakdowns/platform/PM-88888-notification-refactor/tasks.md. Do that one.

## Expectations

- Agent activates as `bitwarden-implementer`.
- First: attempts to get a Jira key from the user. If the user genuinely cannot provide one (as in this fixture), falls back to reading task 4 from the breakdown's `tasks.md`.
- Reads the breakdown's Specification and Plan sections as context.

## Pass criteria

- **Trigger:** agent selected is `bitwarden-implementer`.
- **Behavior:** asks for a Jira key OR acknowledges the user's stated inability to provide one before falling back.
- **Behavior:** breakdown doc is read; task 4 is identified before planning.
- **Behavior (negative):** `researching-jira-issues` is not invoked absent a Jira ID.

## Runs

| Run | Trigger | Behavior (ask/ack) | Behavior (read) | Behavior (no Jira) | Notes |
| --- | ------- | ------------------ | --------------- | ------------------ | ----- |
| 1   |         |                    |                 |                    |       |
| 2   |         |                    |                 |                    |       |
| 3   |         |                    |                 |                    |       |
