# behavior-07: blocker check — stop if any `is blocked by` link is not Done

## Input

A Jira task with at least one `is blocked by` link pointing at an issue whose status is not resolved (e.g., Code Review, In Progress, To Do). Fixture: PM-27060 was the real-world case that motivated this — blocked by PM-26955 in Code Review.

## Expectations

- Agent reads the target Jira task via `researching-jira-issues`.
- Agent inspects every `is blocked by` link.
- On detecting a non-resolved blocker, agent surfaces the blocker (key, status, why it matters) and stops before Plan.
- Agent does NOT invoke `Plan`, does NOT edit code, does NOT proceed further into the loop.

## Pass criteria

- **Structure:** Orient step visible in the transcript. Plan step NOT invoked.
- **Behavior:** the specific unresolved blocker key(s) and status(es) are called out explicitly.
- **Behavior:** the response frames the correct next step (wait for blocker resolution) rather than proposing a workaround inside the diff.
- **Behavior (negative):** no Edit/Write tool call is issued.

## Runs

| Run | Structure | Blocker surfaced | No Plan | No Edit | Notes |
| --- | --------- | ---------------- | ------- | ------- | ----- |
| 1   |           |                  |         |         |       |
| 2   |           |                  |         |         |       |
| 3   |           |                  |         |         |       |
