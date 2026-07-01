# behavior-06: orient with breakdown + sibling epic tasks

## Input

A Jira task (PM-12345) that belongs to an epic (PM-99999) which has an associated tech breakdown. When asked "is there a breakdown?", the user answers yes and provides the breakdown location.

## Expectations

- Agent invokes `Skill(researching-jira-issues)` on PM-12345.
- Agent asks about the breakdown, gets a yes, then:
  - Reads the breakdown's Specification and Plan sections.
  - Fetches the sibling Jira tasks in epic PM-99999 (either via a JQL search on the epic link, or by reading each child task named in the breakdown's `tasks.md`).
- Only after this full orient does Plan/Implement proceed.

## Pass criteria

- **Structure:** Orient step includes all three: the target task, the breakdown doc, and the sibling epic tasks.
- **Behavior:** at least one sibling epic task is fetched — the agent must not treat the target task in isolation when a breakdown exists.
- **Behavior:** if a sibling task has in-flight or conflicting work, the agent surfaces the collision before proceeding to Implement.

## Runs

| Run | Structure | Siblings fetched | Collisions surfaced | Notes |
| --- | --------- | ---------------- | ------------------- | ----- |
| 1   |           |                  |                     |       |
| 2   |           |                  |                     |       |
| 3   |           |                  |                     |       |
