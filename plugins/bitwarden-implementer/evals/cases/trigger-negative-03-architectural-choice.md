# trigger-negative-03: architectural choice

## Input

> Should we use Dapper or EF Core for the org-token migration? Walk me through the trade-offs.

## Expectations

- Agent does NOT activate as `bitwarden-implementer`.
- Response routes to a planning-shaped path (surface the question back to a human for architectural decision), NOT an implementation loop.

## Pass criteria

- **Trigger:** `bitwarden-implementer` is not selected.
- **Behavior:** no Implement, Preflight, or Ship phase is proposed.
- **Behavior:** the response frames the ask as an architectural decision that requires human input, not an implementation task.
