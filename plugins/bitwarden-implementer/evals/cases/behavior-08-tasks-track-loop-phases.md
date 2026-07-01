# behavior-08: tasks track loop phases

## Input

Any positive-trigger task where the loop is expected to run past Orient (fixture: a task with no blockers, a resolvable ambiguity, and small implementable scope).

## Expectations

- Agent creates one task per phase of the loop (Orient, Plan, Implement, Preflight, Self-review, Ship) before any other tool call in the workflow.
- Agent marks each task `in_progress` at the start of its phase and `completed` at the end.
- If the loop stops early (blocker check, deep ambiguity), remaining tasks stay as `pending` — they are not force-completed.

## Pass criteria

- **Structure:** exactly six `TaskCreate` calls occur before the first `Skill` or `Read` or `Bash` call.
- **Structure:** the tasks appear in `TaskList` in the order Orient → Plan → Implement → Preflight → Self-review → Ship.
- **Behavior:** every phase transition is bracketed by `TaskUpdate` calls — `completed` for the phase that just finished, `in_progress` for the phase starting next.
- **Behavior (early stop):** if the agent stops at Orient (e.g., blocker check trips), Orient is `completed`, and Plan through Ship remain `pending`. No task is marked completed that did not actually run.

## Runs

| Run | 6 tasks created up-front | Phase transitions bracketed | Early-stop leaves pending | Notes |
| --- | ------------------------ | --------------------------- | ------------------------- | ----- |
| 1   |                          |                             |                           |       |
| 2   |                          |                             |                           |       |
| 3   |                          |                             |                           |       |
