# Bitwarden repo layout, stacks, and the layer → repo map

Bitwarden's code spans several repositories. A single feature often touches more than
one, and each gets its own Testing Trophy. Treat the table below as a **starting map**,
not gospel — when a repo is checked out, read its `CLAUDE.md` and grep its existing tests
to confirm the actual conventions before recommending tooling.

## Platform repos and their stacks

| Repo (typical)      | Platform                       | Language / framework                | Static                                  | Unit / Integration tooling                                                                 |
| ------------------- | ------------------------------ | ----------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------ |
| `bitwarden/server`  | Backend / API                  | C# / .NET, ASP.NET Core, EF Core    | `dotnet build` analyzers, nullable refs | xUnit; integration via `WebApplicationFactory` + test DB / in-memory providers             |
| `bitwarden/clients` | Web, Browser ext, Desktop, CLI | TypeScript, Angular, Electron, RxJS | `tsc`, ESLint                           | Jest + Angular TestBed / Testing Library (unit + integration); mocked HTTP at the boundary |
| `bitwarden/ios`     | iOS                            | Swift / SwiftUI                     | SwiftLint, compiler                     | XCTest (unit + integration); XCUITest for on-device UI                                     |
| `bitwarden/android` | Android                        | Kotlin                              | ktlint/detekt, compiler                 | JUnit + Robolectric / Espresso (instrumented)                                              |

Exact repo names and tool versions drift — verify against the checkout. If a platform
isn't in this table, infer its stack from the repo and state the assumption in the report.

## Where each layer lives — important

- **Static, unit, integration** tests live **alongside the code, inside each platform
  repo** (e.g. `server`'s xUnit projects, `clients`' `*.spec.ts` files, the iOS test
  targets).
- **End-to-end (E2E) tests live in a dedicated, private `test` repository** — _not_
  inside the platform repos. Consequences for analysis:
  - An E2E recommendation always targets that separate `test` repo.
  - A coverage scout will **not** find existing E2E tests by searching `server`/`clients`/
    `ios`. It must look in the `test` repo, which the user may not have checked out.
  - If the `test` repo is unavailable, treat existing E2E coverage as **unverified** and
    say so explicitly in the report — do not assume it is absent or present.

## Mapping a behavior to a platform + layer

1. Identify which repo(s) the behavior lives in from the change surface (diff paths,
   ticket components, CSV team/area).
2. Within each repo, choose the layer per `testing-trophy.md` and name the concrete tool
   from the table above (confirmed against the checkout where possible).
3. For any cross-system journey worth E2E coverage, target the dedicated `test` repo and
   flag whether comparable E2E coverage already exists there.
