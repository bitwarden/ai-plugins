# Test layers and the Bitwarden repo layout

What you need to **bucket** an observed test by layer and to know **where each layer lives**.
This is reference for inventorying existing coverage — it deliberately omits the
cheapest-sufficient assignment rules and anti-patterns (those belong to a forward-looking
recommender, not to this backward-looking inventory).

## The three layers (for bucketing observed tests)

1. **Unit** — tests a single function/class/module in isolation: pure logic, algorithms, edge
   cases, error handling. Fast, cheap setup, no real collaborators.
2. **Integration** — tests several units working together through real (or realistic)
   collaborators: a controller + service + in-memory/test database; a component rendered with its
   real children and a mocked network boundary; a view model against a real repository.
3. **E2E (end-to-end)** — drives the real, fully assembled system as a user would: real browser,
   device, backend. In a platform repo these are a thin top reserved for critical journeys; the
   cross-system journeys themselves live in the dedicated `test` repo, where E2E is the whole suite.

How the volume distributes across these layers describes a repo's _shape_ — a **pyramid** (broad
unit base, moderate integration, thin/absent E2E) or a **trophy** (focused unit base, heavy
integration bulge, thin E2E). Bitwarden's repos deliberately sit at different points; bucket each
observed test by what it actually does, not by an idealized shape.

## Each repo's stack and shape

A single feature often touches more than one repo, and **each repo follows its own test shape**.
Use this table as a **starting map** — when a repo is checked out, confirm the actual conventions
from its config first (`finding-coverage.md` → _Discovering a repo's test conventions (config-first)_), and read
the table as the last-resort default. For any repo not listed, infer its stack from the checkout
and **state the assumption** in the report.

| Repo                                     | Platform · stack · tooling                                                                                                                                                                                   | Shape                                       |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- |
| `bitwarden/server`                       | Backend / API · C# / .NET, ASP.NET Core, EF Core · xUnit; integration via `WebApplicationFactory` + test DB / in-memory providers                                                                            | **Pyramid** (unit-heavy)                    |
| `bitwarden/clients`                      | Web, Browser ext, Desktop, CLI · TypeScript, Angular, Electron, RxJS · Jest + `jest-mock-extended` + Angular TestBed (unit + shallow component); mocked HTTP at the boundary                                 | **Unit-heavy** (pyramid-leaning)            |
| `bitwarden/ios`                          | iOS · Swift / SwiftUI · XCTest (+ emerging Swift Testing); SnapshotTesting + ViewInspector for SwiftUI views; processor/coordinator tests with mocks                                                         | **Trophy + snapshot layer**                 |
| `bitwarden/android`                      | Android · Kotlin · JUnit5 + MockK + Turbine for ViewModels/logic; Compose UI tests run on the JVM via Robolectric                                                                                            | **Unit-heavy + JVM Compose-UI integration** |
| `bitwarden/sdk-internal`                 | Cross-platform SDK (powers clients via WASM, mobile via UniFFI) · Rust (cargo workspace), WASM + UniFFI bindings · `cargo test --workspace`; `mockall` + `wiremock` for the few HTTP/trait integration tests | **Pyramid** (strongly unit-heavy)           |
| `bitwarden/test`                         | Cross-platform E2E (web, desktop, browser ext, iOS, android, CLI, API) · C# / .NET · NUnit + Selenium WebDriver + Appium (mobile) + CliWrap (CLI), Page Object Model; drives real builds                     | **All E2E**                                 |
| `bitwarden/browser-interactions-testing` | Browser extension autofill (dedicated E2E suite) · TypeScript, Playwright, Docker Compose · Playwright form-fill against real Chromium extension builds                                                      | **All E2E** (autofill)                      |

## Where each layer lives — important

- **Unit and integration** tests live **alongside the code, inside each platform repo** (e.g.
  `server`'s xUnit projects, `clients`' `*.spec.ts` files, the iOS test targets, and
  `sdk-internal`'s Rust crates).
- **End-to-end (E2E) tests live in a dedicated `test` repository** — _not_ inside the platform
  repos. It sits as a sibling of `server` / `clients` / `ios` in the user's Bitwarden checkout root,
  so look for it next to whichever platform repo you're in (e.g. if `clients` is at
  `~/repos/Bitwarden/clients`, `test` is at `~/repos/Bitwarden/test`). Source:
  [`bitwarden/test`](https://github.com/bitwarden/test) — cite this URL only if no local sibling is
  found. If the `test` repo is not checked out, record E2E coverage as `unverified`.
- **Browser-extension autofill / form-fill E2E** also has a dedicated repo,
  [`bitwarden/browser-interactions-testing`](https://github.com/bitwarden/browser-interactions-testing).
  Note the **overlap**: the cross-platform `test` repo _also_ carries extension autofill coverage, so
  a given autofill journey may be tested in either (or both). When inventorying autofill E2E, check
  both repos and flag where coverage overlaps.
