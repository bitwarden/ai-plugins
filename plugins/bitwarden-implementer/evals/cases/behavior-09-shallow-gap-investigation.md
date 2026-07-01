# behavior-09: shallow gap — investigate before stopping

## Input

A thinly-specified Jira task whose answer lives in the code, not in the human's head. Fixture based on the real-world PM-35093 pattern: task says "add support for the FedRAMP environment in the `appLinkHost()` allowlist" without specifying the domain name, the shape of the allowlist, or the pattern to follow. The information _is_ present in the codebase (the existing `.com` / `.eu` / `.pw` entries reveal the pattern) — the task is under-specified only because the reader is expected to grep for it.

## Expectations

- Agent recognizes the gap during Orient.
- Agent investigates the code surface (greps `appLinkHost`, reads the allowlist, reads adjacent environment config).
- Agent investigates adjacent Jira tickets in the epic and linked issues for FedRAMP references.
- Agent surfaces what it learned and proposes a shape for the change, then either:
  - Proceeds to Plan with a well-defined shape (if the code-derived answer is complete), or
  - Surfaces only the remaining _stakeholder-required_ decision (e.g., "the pattern is clear; I need to know the exact FedRAMP domain string").

## Pass criteria

- **Behavior:** at least one code-search or code-read tool call before any human-directed question.
- **Behavior:** the agent's summary of what it found is concrete — cites file(s), pattern(s), and the specific delta needed.
- **Behavior:** the human is only asked about the residual _design decision_, not about facts the code already answered.
- **Behavior (negative):** the agent does NOT immediately stop-and-surface on encountering thin specification.

## Runs

| Run | Investigated first | Concrete summary | Only deep question surfaced | Notes |
| --- | ------------------ | ---------------- | --------------------------- | ----- |
| 1   |                    |                  |                             |       |
| 2   |                    |                  |                             |       |
| 3   |                    |                  |                             |       |
