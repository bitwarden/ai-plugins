# Test layers and how to assign one

A model for shaping automated test coverage across three layers — **unit**, **integration**,
**E2E**. How the volume distributes across them describes a repo's _shape_: a **pyramid** (broad
unit base, moderate integration, thin/absent E2E) suits backend and logic-heavy code; a **trophy**
(focused unit base, heavy integration bulge, thin E2E) suits application code where behavior emerges
from collaborators (UI components, view models). Integration is where each shape buys most of its
confidence — how _much_ of it a repo carries is what separates the two.

Neither shape is universally correct, and **this skill imposes neither.** Bitwarden's repos
deliberately sit at different points — some pyramid, some trophy, some a mix, two effectively
**all E2E**. Recommend the layer that fits the **target repo's actual practice** (mapped per repo
in `monorepo-layout.md`), not an idealized shape. A mix within or across repos is normal.

## The three layers (cheapest → most expensive)

1. **Unit** — tests a single function/class/module in isolation. Best for pure logic, algorithms,
   edge cases, and error handling where setup is cheap and the unit has real branching complexity.
   Fast and stable, but isolation lets integration bugs slip through.

2. **Integration** — the **confidence layer**. Tests several units working together through real
   (or realistic) collaborators: a controller + service + in-memory/test database; a component
   rendered with its real children and a mocked network boundary; a view model against a real
   repository. Exercises the wiring users depend on without the cost and flakiness of E2E.

3. **E2E (end-to-end)** — thin top in most repos, the **entire suite** in the dedicated E2E repos.
   Drives the real, fully assembled system as a user would: real browser, device, backend. Highest
   confidence per test, but slowest, most expensive, most flaky. In a platform repo, reserve it for
   a few **critical user journeys** (login, vault unlock, checkout) — not branch coverage. The
   cross-system journeys themselves live in the `test` repo, where E2E _is_ the strategy.

Static analysis (type checking, linters, formatters) sits below all three and is handled by
per-repo tooling — not recommended by this skill.

## How to assign a layer

Apply two rules together:

1. **Cheapest sufficient layer.** Pick the lowest-cost layer (unit < integration < E2E) that still
   buys the confidence the behavior requires:
   - Pure transformation, calculation, parsing, validation with real branching → **unit**.
   - Behavior that emerges from collaborators working together (HTTP handler + service +
     persistence; component + store + API boundary; view model + repository) → **integration**.
   - A behavior only meaningful as a full user journey across the real system → **E2E**, and only
     if genuinely critical.
   - Anything a type system, analyzer, or linter already guarantees → don't write a test for it.

2. **Honor the target repo's shape.** The cheapest-sufficient call lands inside the shape the repo's
   engineers actually maintain, so the same behavior resolves differently per repo: in `server` it
   lands in a unit-heavy pyramid; in `ios` in component/processor integration plus the snapshot
   layer; a cross-system journey lands as E2E in the dedicated `test` repo, never inside a platform
   repo. Cite the per-repo shape in `monorepo-layout.md` — and where a repo's real shape is unknown,
   say so rather than defaulting to a trophy.

## Anti-patterns to avoid (in any shape)

- **Ice-cream cone** — many E2E, few integration/unit. Slow, flaky, expensive. Wrong everywhere,
  including a pyramid repo that has started leaning on E2E for branch coverage.
- **Over-unit-testing** — exhaustive unit tests with heavy mocking that re-assert the mocks rather
  than real behavior; integration would buy more. The most common failure in unit-heavy repos.
- **Testing trivial code** — getters/setters, framework glue, type-guaranteed invariants. Cost
  without confidence.
- **E2E for branch coverage** — slow full-system tests covering edge cases that belong at unit or
  integration.
- **Forcing a foreign shape** — recommending an integration bulge for a pyramid repo (or vice
  versa) because a model says so. Match the repo, not the textbook.
