# Coverage report template

The **inventory** report: what is already tested for a change, per platform, every cited test a
stable GitHub permalink. Build it against the shared contract in
`../../../references/report-template-common.md` (output constraints, styling/sentinel rule,
auto-numbering, ToC, the Header/Overview/Summary/Evidence sections, content rules, and the
skeleton) — **read that first**. This file covers only what is specific to the coverage report.
Build with `--kind test-coverage`; the invocation and filename rules are in
`../../../references/report-style-tokens.md` → _Building the report_.

This is the coverage counterpart to the `analyzing-test-stack` test-stack report; the two splice
the same stylesheet and follow the same shared contract, so they read as one instrument.

## Sections (in order)

ToC and section ids, in order: `#overview`, `#summary`, `#evidence`, `#coverage`, `#gaps`.

- **`#overview`** — recap **how well covered the change is per platform** (where observed tests
  concentrate, which layers are bare); the top 3 coverage gaps the reader should know about are
  drawn from `#gaps`; anchor into `#coverage` and `#gaps`. This report **describes** coverage — it
  does not recommend new tests or assign cheapest-sufficient layers (that is the test-stack
  report's job); say so in one line and, if a test-stack report was also produced, link to it.
- **`#summary`** — heading "Observed coverage shape". The distribution chart's `.seg flex:<count>`
  is the **count of observed tests** at each layer (not recommended counts); caption it
  `Fig 1 · Observed test coverage by platform`. The `.shapes` list gives each platform's observed
  shape (e.g. "server: 14 integration, 3 unit, 0 E2E observed"); a platform with no observed
  coverage still gets a row, shown empty.
- **`#coverage`** — per-platform tables, **one row per behavior** (not per test):
  `Behavior / surface | Layer | Tests (linked) | Count | Source | Notes`.
  - **Tests (linked)** renders the behavior's 1–3 representative tests as permalinks (binding), or
    the `.unlinkable` span when a test cannot be linked — never a fabricated URL. The exact link /
    `.unlinkable` markup and the permalink production rules are owned by `finding-coverage.md` →
    _Citing tests as GitHub permalinks_ and _When a test cannot be linked_ — follow it.
  - **Count** is the approximate number of tests covering that behavior at that layer — breadth
    without enumerating every test. Do not expand a well-covered behavior into dozens of rows.
  - **Layer** uses the matching layer chip. **Source** is `PR` (tests shipped in a linked/merged
    PR) or `pre-existing` (found by the targeted lookup) — keep the observed-vs-assumed
    distinction visible.
- **`#gaps`** — heading "Coverage gaps": behaviors/surfaces in the change with **no observed
  test**, each marked `<span class="badge warn">unverified</span>` with a one-line reason (no
  PR-observed test and no targeted hit; or `test` repo unavailable). The honest record of what is
  _not_ known to be covered — not a recommendation to add tests.

## Coverage section markup

Slot this between `#evidence` and `#gaps` in the shared skeleton:

```html
<section id="coverage">
  <h2>Observed coverage</h2>
  <div class="scroll">
    …per-platform behavior→test tables with linked evidence…
  </div>
</section>
```
