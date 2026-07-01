# trigger-negative-04: plan-only ask (no implementation intent)

## Input

> Draft an implementation plan for PM-12345. Don't write any code yet — I want to review the approach first.

## Expectations

- Agent does NOT activate as `bitwarden-implementer` (this is planning without implementation intent).
- Response routes to the built-in `Plan` agent directly.

## Pass criteria

- **Trigger:** `bitwarden-implementer` is not selected.
- **Behavior:** `Plan` agent is referenced instead.
- **Behavior (negative):** no Implement, Preflight, or Ship phase is proposed.
