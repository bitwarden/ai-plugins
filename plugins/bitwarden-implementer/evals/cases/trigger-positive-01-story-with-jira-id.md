# trigger-positive-01: story with Jira ID (no breakdown mentioned)

## Input

> Implement PM-12345.

## Expectations

- Agent activates as `bitwarden-implementer`.
- First action invokes `Skill(researching-jira-issues)` on PM-12345.
- Agent asks the user whether the task has an associated tech breakdown before continuing.
- Does not immediately edit code before planning.

## Pass criteria

- **Trigger:** agent selected is `bitwarden-implementer`.
- **Structure:** an Orient step is visible before any Edit/Write tool call.
- **Behavior:** `Skill(researching-jira-issues)` invoked on PM-12345.
- **Behavior:** the agent asks about a breakdown (yes/no) rather than assuming one exists or doesn't.

## Runs

| Run | Trigger | Structure | Jira researched | Asked about breakdown | Notes |
| --- | ------- | --------- | --------------- | --------------------- | ----- |
| 1   |         |           |                 |                       |       |
| 2   |         |           |                 |                       |       |
| 3   |         |           |                 |                       |       |
