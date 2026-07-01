# trigger-positive-02: bug fix from the board

## Input

> Take PM-67890 to PR — it's the vault sync race condition bug we tracked down yesterday.

## Expectations

- Agent activates as `bitwarden-implementer`.
- Same loop applies: Orient → Plan → Implement → Preflight → Self-review → Ship.
- Reproduction step visible during Implement (bugs require reproducing before fixing).

## Pass criteria

- **Trigger:** agent selected is `bitwarden-implementer`.
- **Structure:** Orient/Plan visible before Implement.
- **Behavior:** attempts to reproduce the bug (test case or manual repro) before writing the fix.

## Runs

| Run | Trigger | Structure | Behavior | Notes |
| --- | ------- | --------- | -------- | ----- |
| 1   |         |           |          |       |
| 2   |         |           |          |       |
| 3   |         |           |          |       |
