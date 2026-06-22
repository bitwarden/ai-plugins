# Bitwarden repo layout, stacks, and the layer → repo map

Bitwarden's code spans several repositories. A single feature often touches more than
one, and **each repo follows its own test shape** — pyramid, trophy, or all-E2E (the shapes
themselves are defined in `test-layers.md`). Treat the table below as a **starting map**, not
gospel — when a repo is checked out, confirm the actual conventions from its config first (the
`assessing-test-coverage` skill's `references/finding-coverage.md` → _Discovering a repo's
test conventions_), and read the table as the last-resort default.

Establishing what a change is **already tested** by — finding existing coverage and citing
it as permalinks — is a separate job owned by the `assessing-test-coverage` skill. This file
covers only the repo/stack map and the rules for mapping a behavior to the layer it _should_
live at.

## Each repo's test shape in practice

Each repo's stack and the shape it actually maintains — not a one-size trophy. Recommend the
layer that fits the repo's real distribution (see `test-layers.md` for the shapes), landed inside
that shape and named with the concrete tool below. Each shape was **confirmed against a local
checkout**; exact repo names and tool versions drift, so re-verify against the checkout, and for
any repo not listed, infer its stack and shape from the checkout and **state the assumption** in
the report.

| Repo                                     | Platform · stack · tooling                                                                                                                                                                                                                                                                                                                               | Shape                                       | What that means for recommendations                                                                                                                                                                                                                                 |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden/server`                       | Backend / API · C# / .NET, ASP.NET Core, EF Core · xUnit; integration via `WebApplicationFactory` + test DB / in-memory providers                                                                                                                                                                                                                        | **Pyramid** (unit-heavy)                    | Broad unit base (~5:1 over integration), a meaningful integration layer, **no E2E in-repo**. Default behaviors to unit; reserve integration for endpoint/persistence wiring.                                                                                        |
| `bitwarden/clients`                      | Web, Browser ext, Desktop, CLI · TypeScript, Angular, Electron, RxJS · Jest + `jest-mock-extended` + Angular TestBed (unit + shallow component); mocked HTTP at the boundary — _no_ Testing Library                                                                                                                                                      | **Unit-heavy** (pyramid-leaning)            | ~1,000+ colocated `*.spec.ts`; TestBed component tests mock their children (shallow, not deep integration). Push logic to unit; treat true component-integration as the deliberate step up. No E2E in-repo.                                                         |
| `bitwarden/ios`                          | iOS · Swift / SwiftUI · XCTest (+ emerging Swift Testing); SnapshotTesting + ViewInspector for SwiftUI views; processor/coordinator tests with mocks                                                                                                                                                                                                     | **Trophy + snapshot layer**                 | Component/processor/coordinator tests with mocks dominate (integration-leaning); the **snapshot-testing** layer for SwiftUI views is first-class; lighter pure-unit layer; **no systematic XCUITest**. Recommend snapshot coverage for view changes explicitly.     |
| `bitwarden/android`                      | Android · Kotlin · JUnit5 + MockK + Turbine for ViewModels/logic; Compose UI tests run on the JVM via Robolectric                                                                                                                                                                                                                                        | **Unit-heavy + JVM Compose-UI integration** | ~558 JVM `src/test` files: a unit base plus a substantial Compose-UI integration tier on the JVM. **All JVM `src/test` — no `androidTest`/Espresso, no screenshot testing, no E2E in-repo.** Don't recommend device-instrumented or screenshot tests here.          |
| `bitwarden/sdk-internal`                 | Cross-platform SDK (core logic powering clients via WASM, mobile via UniFFI) · Rust (cargo workspace, ~50 crates), WASM + UniFFI (Swift/Kotlin) bindings · `cargo test --workspace` (no nextest; cargo-llvm-cov for coverage); `mockall` + `wiremock` for the few HTTP/trait integration tests; binding surfaces consumed by `clients`, `ios`, `android` | **Pyramid** (strongly unit-heavy)           | ~97% inline `#[cfg(test)]` unit tests (crypto/encoding/parsing logic, deterministic, no mocks) vs ~3% in `tests/` dirs; mocks only where HTTP or cross-module orchestration matters. **No E2E.** Default to unit; integration only for binding/orchestration flows. |
| `bitwarden/test`                         | Cross-platform E2E (web, desktop, browser ext, iOS, android, CLI, API) · C# / .NET · NUnit + Selenium WebDriver (web/desktop/ext) + Appium (mobile) + CliWrap (CLI), Page Object Model; drives real builds                                                                                                                                               | **All E2E**                                 | The cross-system journeys themselves. Everything here is E2E by definition — never recommend unit/integration in this repo.                                                                                                                                         |
| `bitwarden/browser-interactions-testing` | Browser extension autofill (dedicated E2E suite) · TypeScript, Playwright, Docker Compose · Playwright form-fill against real Chromium extension builds; static-page + live-site scenarios                                                                                                                                                               | **All E2E** (autofill)                      | The autofill counterpart to `test`; E2E only.                                                                                                                                                                                                                       |

## Where each layer lives — important

- **Unit and integration** tests live **alongside the code, inside each platform
  repo** (e.g. `server`'s xUnit projects, `clients`' `*.spec.ts` files, the iOS test
  targets, and `sdk-internal`'s Rust crates, whose `cargo test` suites sit next to the
  code they cover).
- **End-to-end (E2E) tests live in a dedicated `test` repository** — _not_ inside the
  platform repos. It sits as a sibling of `server` / `clients` / `ios` in the user's
  Bitwarden checkout root, so look for it next to whichever platform repo you're in
  (e.g. if `clients` is at `~/repos/Bitwarden/clients`, `test` is at
  `~/repos/Bitwarden/test`). Source: [`bitwarden/test`](https://github.com/bitwarden/test) — cite this URL
  in the report only if no local sibling is found.
- **Browser-extension autofill / form-fill E2E** also has a dedicated repo,
  [`bitwarden/browser-interactions-testing`](https://github.com/bitwarden/browser-interactions-testing) —
  Playwright driving real extension builds against static pattern pages and live sites
  (Chromium today). Note the **overlap**: the cross-platform `test` repo _also_ carries
  extension autofill coverage, so a given autofill journey may be tested in either (or
  both). When recommending or inventorying autofill E2E, check both repos and flag where
  coverage overlaps or where one is the better home, rather than assuming a single owner.

## Mapping a behavior to a platform + layer

1. Identify which repo(s) the behavior lives in from the change surface (diff paths,
   ticket components, CSV team/area).
2. Within each repo, choose the layer per `test-layers.md` (the cheapest sufficient layer)
   **landed inside that repo's shape** from _Each repo's test shape in practice_ above — a
   pyramid repo like `server` or `sdk-internal` resolves toward unit; `ios` toward its
   component + snapshot practice — and name the concrete tool from the table above (confirmed
   against the checkout where possible).
3. For any cross-system journey worth E2E coverage, target the dedicated `test` repo;
   for browser-extension autofill / form-fill journeys, also consider
   `browser-interactions-testing`. Coverage for autofill can live in either repo, so
   check both and flag any overlap or comparable existing E2E coverage (per the coverage
   inventory from `assessing-test-coverage`).

Existing coverage to compare these recommendations against — including the GitHub permalinks
the report's Evidence column requires — comes from the `assessing-test-coverage` skill's
coverage inventory (`references/finding-coverage.md` → _Citing tests as GitHub permalinks_
and _Output contract_), not from this file.
