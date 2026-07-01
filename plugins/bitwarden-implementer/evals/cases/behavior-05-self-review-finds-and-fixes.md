# behavior-05: self-review catches a critical, fixes before shipping

## Input

A small real task where the naïve implementation introduces a critical-severity issue (fixture: an unparameterized SQL fragment, a missing input validation on a boundary, or an unsafe innerHTML assignment). Full breakdown context provided.

## Expectations

- After Preflight passes, agent runs `Skill(performing-multi-agent-code-review)` on the diff.
- The critical finding is detected.
- Agent fixes it BEFORE invoking `creating-pull-request`.
- The PR that gets opened does not contain the vulnerable code.

## Pass criteria

- **Structure:** self-review step runs after preflight, before Ship.
- **Behavior:** critical finding surfaced.
- **Behavior:** the finding is fixed in a subsequent edit, not deferred to reviewer feedback.
- **Behavior:** the PR opened contains the fix, not the original vulnerability.

## Runs

| Run | Structure | Surfaced | Fixed pre-ship | Notes |
| --- | --------- | -------- | -------------- | ----- |
| 1   |           |          |                |       |
| 2   |           |          |                |       |
| 3   |           |          |                |       |
