# Test shape: pyramid, trophy, and where Bitwarden's repos actually sit

A model for shaping automated test coverage across three layers — **unit**, **integration**,
**E2E**. Two classic shapes describe how the volume is distributed across those layers:

- **Testing Pyramid** — a broad **unit** base, a smaller **integration** layer, a thin (often
  absent) **E2E** cap. Optimizes for fast, stable, cheap-to-maintain coverage. The natural fit
  for backend and logic-heavy code where units have real branching complexity.
- **Testing Trophy** — a focused **unit** base, a **heavy integration** bulge where most
  confidence is bought, a thin **E2E** cap. The fit for application code where behavior emerges
  from collaborators (UI components, view models) and an isolated unit proves little.

Neither shape is universally "correct," and **this skill does not impose one on every repo.**
Bitwarden's repos deliberately sit at different points — some pyramid, some trophy, some a mix,
and two are effectively **all E2E**. Recommend the layer that fits the **target repo's actual
practice** (mapped per repo in `monorepo-layout.md`), not an idealized shape. A "funky mix" of
pyramid and trophy within or across repos is normal and fine.

## The three layers (cheapest → most expensive)

1. **Unit** — focused. Tests a single function/class/module in isolation. Best for pure
   logic, algorithms, edge cases, and error handling where setup is cheap and the unit
   has real branching complexity. Fast and stable, but isolation can let integration
   bugs slip through.

2. **Integration** — the **confidence layer**: the trophy's bulge and the pyramid's middle.
   Tests several units working together through real (or realistic) collaborators: a
   controller + service + in-memory or test database, a component rendered with its real
   child components and a mocked network boundary, a view model against a real repository.
   It exercises the wiring users actually depend on without the cost and flakiness of full
   E2E. How _much_ of it a repo carries is what separates a trophy (a lot) from a pyramid
   (a moderate middle).

3. **E2E (end-to-end)** — thin top in most repos, the **entire suite** in the dedicated E2E
   repos. Drives the real, fully assembled system the way a user would: real browser, real
   device, real backend. Highest confidence per test, but slowest, most expensive, and most
   flaky. In a platform repo, reserve it for a small number of **critical user journeys**
   (e.g. login, vault unlock, checkout) — not for branch coverage. The cross-system journeys
   themselves live in the `test` repo, where E2E _is_ the strategy.

## The two shapes

```
   Pyramid (e.g. server)              Trophy (e.g. ios)

      ┌─────────┐                       ┌───────────┐
      │   E2E   │  thin / none          │    E2E    │   thin top
   ┌──┴─────────┴──┐                 ┌──┴───────────┴──┐
   │  Integration  │  moderate       │   Integration   │   HEAVY
   └──┬─────────┬──┘              ┌──┴─────────────────┴──┐
   │     Unit      │  BROAD base   │        Unit           │  focused
   └───────────────┘              └───────────────────────┘
```

Static analysis (type checking, linters, formatters) sits below both shapes and is handled by
per-repo tooling — not recommended by this skill.

## How to assign a layer

Apply two rules together:

1. **Cheapest sufficient layer.** Pick the lowest-cost layer (unit < integration < E2E) that
   still buys the confidence the behavior requires:
   - Pure transformation, calculation, parsing, validation logic with real branching → **unit**.
   - Behavior that emerges from collaborators working together (HTTP handler + service +
     persistence; component + store + API boundary; view model + repository) → **integration**.
   - A behavior only meaningful as a full user journey across the real system → **E2E**, and
     only if it is genuinely critical.
   - Anything a type system, analyzer, or linter already guarantees → don't write a test for it.

2. **Honor the target repo's shape.** The cheapest-sufficient call lands inside the shape the
   repo's engineers actually maintain. The same kind of behavior resolves differently per repo:
   in `server` it lands in a unit-heavy pyramid; in `ios` it lands in component/processor
   integration tests plus the repo's snapshot layer; a cross-system journey lands as E2E in the
   dedicated `test` repo, never inside a platform repo. Recommend what that repo maintains today,
   citing the per-repo shape in `monorepo-layout.md` — and where a repo's real shape is unknown,
   say so rather than defaulting to the trophy.

## Anti-patterns to avoid (in any shape)

- **Ice-cream cone** — many E2E tests, few integration/unit. Slow, flaky, expensive to maintain.
  Wrong everywhere, including in a pyramid repo that has started leaning on E2E for branch coverage.
- **Over-unit-testing** — exhaustive unit tests with heavy mocking that re-assert the mocks
  rather than real behavior; integration would buy more. The most common failure in unit-heavy repos.
- **Testing trivial code** — tests for getters/setters, framework glue, or type-guaranteed
  invariants. Cost without confidence.
- **E2E for branch coverage** — using slow full-system tests to cover edge cases that belong
  at the unit or integration layer.
- **Forcing a foreign shape** — recommending an integration bulge for a repo that runs a unit
  pyramid (or vice versa) just because a model says so. Match the repo, not the textbook.
