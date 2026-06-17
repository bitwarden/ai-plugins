# The Testing Trophy

A model for shaping automated test coverage, contrasted with the older Testing Pyramid. The trophy weights **integration** tests most heavily,
because they buy the most confidence per unit of cost and maintenance for typical
application code.

## The three layers (base → top)

1. **Unit** — focused. Tests a single function/class/module in isolation. Best for pure
   logic, algorithms, edge cases, and error handling where setup is cheap and the unit
   has real branching complexity. Fast and stable, but isolation can let integration
   bugs slip through.

2. **Integration** — **the heaviest layer; the trophy's bulge.** Tests several units
   working together through real (or realistic) collaborators: a controller + service +
   in-memory or test database, a component rendered with its real child components and a
   mocked network boundary, a view model against a real repository. This is where most
   confidence is bought because it exercises the wiring users actually depend on, without
   the cost and flakiness of full E2E.

3. **E2E (end-to-end)** — thin top. Drives the real, fully assembled system the way a
   user would: real browser, real device, real backend. Highest confidence per test, but
   slowest, most expensive, and most flaky. Reserve for a small number of **critical user
   journeys** (e.g. login, vault unlock, checkout) — not for branch coverage.

## The shape

```
        ┌───────────┐
        │    E2E    │      thin top — critical journeys only
     ┌──┴───────────┴──┐
     │   Integration   │   HEAVY — most confidence bought here
     └──┐           ┌──┘
        │   Unit    │      focused — pure logic & edge cases
        └───────────┘
```

Static analysis (type checking, linters, formatters) sits below the trophy and is handled by per-repo tooling — not recommended by this skill.

## How to assign a layer

Pick the **cheapest layer that still buys the confidence the behavior requires**:

- Pure transformation, calculation, parsing, validation logic with real branching → **unit**.
- Behavior that emerges from collaborators working together (HTTP handler + service +
  persistence; component + store + API boundary; view model + repository) → **integration**.
- A behavior only meaningful as a full user journey across the real system → **E2E**, and
  only if it is genuinely critical.
- Anything a type system, analyzer, or linter already guarantees → don't write a test
  for it.

## Anti-patterns to avoid

- **Ice-cream cone** — the trophy inverted: many E2E tests, few integration/unit. Slow,
  flaky, expensive to maintain.
- **Over-unit-testing** — exhaustive unit tests with heavy mocking that re-assert the
  mocks rather than real behavior; integration would buy more.
- **Testing trivial code** — tests for getters/setters, framework glue, or
  type-guaranteed invariants. Cost without confidence.
- **E2E for branch coverage** — using slow full-system tests to cover edge cases that
  belong at the unit or integration layer.
