# Bitwarden repo layout, stacks, and the layer → repo map

Bitwarden's code spans several repositories. A single feature often touches more than
one, and each gets its own Testing Trophy. Treat the table below as a **starting map**,
not gospel — when a repo is checked out, confirm the actual conventions from its config
first (the `assessing-test-coverage` skill's `references/finding-coverage.md` →
_Discovering a repo's test conventions_), and read the table as the last-resort default.

Establishing what a change is **already tested** by — finding existing coverage and citing
it as permalinks — is a separate job owned by the `assessing-test-coverage` skill. This file
covers only the repo/stack map and the rules for mapping a behavior to the layer it _should_
live at.

## Platform repos and their stacks

| Repo (typical)      | Platform                       | Language / framework                | Unit / Integration tooling                                                                 |
| ------------------- | ------------------------------ | ----------------------------------- | ------------------------------------------------------------------------------------------ |
| `bitwarden/server`  | Backend / API                  | C# / .NET, ASP.NET Core, EF Core    | xUnit; integration via `WebApplicationFactory` + test DB / in-memory providers             |
| `bitwarden/clients` | Web, Browser ext, Desktop, CLI | TypeScript, Angular, Electron, RxJS | Jest + Angular TestBed / Testing Library (unit + integration); mocked HTTP at the boundary |
| `bitwarden/ios`     | iOS                            | Swift / SwiftUI                     | XCTest (unit + integration); XCUITest for on-device UI                                     |
| `bitwarden/android` | Android                        | Kotlin                              | JUnit + Robolectric / Espresso (instrumented)                                              |

Exact repo names and tool versions drift — verify against the checkout. If a platform
isn't in this table, infer its stack from the repo and state the assumption in the report.

## Where each layer lives — important

- **Unit and integration** tests live **alongside the code, inside each platform
  repo** (e.g. `server`'s xUnit projects, `clients`' `*.spec.ts` files, the iOS test
  targets).
- **End-to-end (E2E) tests live in a dedicated `test` repository** — _not_ inside the
  platform repos. It sits as a sibling of `server` / `clients` / `ios` in the user's
  Bitwarden checkout root, so look for it next to whichever platform repo you're in
  (e.g. if `clients` is at `~/repos/Bitwarden/clients`, `test` is at
  `~/repos/Bitwarden/test`). Source: `https://github.com/bitwarden/test` — cite this URL
  in the report only if no local sibling is found.

## Mapping a behavior to a platform + layer

1. Identify which repo(s) the behavior lives in from the change surface (diff paths,
   ticket components, CSV team/area).
2. Within each repo, choose the layer per `testing-trophy.md` and name the concrete tool
   from the table above (confirmed against the checkout where possible).
3. For any cross-system journey worth E2E coverage, target the dedicated `test` repo and
   flag whether comparable E2E coverage already exists there (per the coverage inventory
   from `assessing-test-coverage`).

Existing coverage to compare these recommendations against — including the GitHub permalinks
the report's Evidence column requires — comes from the `assessing-test-coverage` skill's
coverage inventory (`references/finding-coverage.md` → _Citing tests as GitHub permalinks_
and _Output contract_), not from this file.
