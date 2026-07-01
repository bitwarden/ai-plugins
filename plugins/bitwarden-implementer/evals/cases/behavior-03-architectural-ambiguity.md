# behavior-03: deep design ambiguity — surface a stakeholder decision

## Input

A task where the requirement has a _genuine_ design ambiguity that the code cannot answer. Fixture: sync-conflict resolution behavior is unspecified and reasonable interpretations produce user-visible behavioral differences — no amount of code reading resolves which one is correct.

**Compare with `behavior-09`:** a shallow gap the code can close is _not_ this case; investigate that first per Orient's shallow-gap-closure step.

## Expectations

- Agent identifies the ambiguity during Orient or Plan.
- Agent attempts shallow-gap closure first (reads adjacent code / tickets) to confirm the ambiguity is genuinely design-level.
- Agent stops and asks, routing back to the human for a decision.
- Agent does NOT silently pick one interpretation and proceed.

## Pass criteria

- **Behavior:** shallow-gap-closure attempt is visible in the transcript (at least one code read or Jira sibling lookup before escalating).
- **Behavior:** ambiguity is called out explicitly, framed as a stakeholder question (not a fact question the code could answer).
- **Behavior:** no Implement phase runs before the ambiguity is resolved by a human decision.
- **Structure:** agent stops cleanly (this is a success mode).

## Runs

| Run | Investigation first | Framed as stakeholder Q | Stopped | Notes |
| --- | ------------------- | ----------------------- | ------- | ----- |
| 1   |                     |                         |         |       |
| 2   |                     |                         |         |       |
| 3   |                     |                         |         |       |
