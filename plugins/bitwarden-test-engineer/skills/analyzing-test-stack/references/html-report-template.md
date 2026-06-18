# Test-stack report template

The **recommendation** report: per-platform test-layer recommendations, risk-weighted by
severity. Build it against the shared contract in
`../../../references/report-template-common.md` (output constraints, styling/sentinel rule,
auto-numbering, ToC, the Header/Overview/Summary/Evidence sections, content rules, and the
skeleton) — **read that first**. This file covers only what is specific to the test-stack report.
Build with `--kind test-stack`; the invocation and filename rules are in
`../../../references/report-style-tokens.md` → _Building the report_.

## Sections (in order)

ToC and section ids, in order: `#overview`, `#summary`, `#evidence`, `#recommendations`, `#gaps`.

- **`#overview`** — recap the **recommended shape per platform**; the top 3 open risks the reader
  must resolve before acting are drawn from `#gaps`, **ordered highest severity first**; anchor
  into `#recommendations` and `#gaps`.
- **`#summary`** — heading "Summary & recommended shape". The distribution chart's
  `.seg flex:<count>` is the **recommended** test count at each layer; caption it
  `Fig 1 · Recommended layer distribution by platform`. The `.shapes` list gives each platform's
  recommended shape matched to its repo's actual practice (e.g. "server: unit-heavy pyramid, thin
  integration, no E2E; ios: integration + snapshot, no XCUITest").
- **`#recommendations`** — per-platform tables, one row per behavior:
  `Behavior | Severity | Recommended layer | Tooling | Rationale | Evidence (linked)`.
  - **Severity** carries the behavior's risk severity (Critical / High / Medium / Low /
    Informative) per `severity-risk.md`, rendered with the stylesheet's inline-code treatment —
    `<code>Critical</code>`, **not** a new color token (the layer ramp and assumption/warn/ok
    badges are the only colored chips the system defines; severity deliberately gets no hue). Mark
    a severity the analyst inferred (rather than read from a bug's Jira field) with
    `<span class="badge assumption">assumption</span>`.
  - Use the layer → repo map; **E2E rows must name the dedicated `test` repo** as target.
  - **The "Evidence (linked)" column is binding.** For every existing test cited as current
    coverage, render the behavior's representative test(s) as GitHub permalinks — or, when a test
    cannot be linked, the `.unlinkable` span instead of a fabricated URL. These records come from
    the coverage inventory; the exact link / `.unlinkable` markup and the permalink production
    rules are owned by the `assessing-test-coverage` skill's `references/finding-coverage.md` →
    _Citing tests as GitHub permalinks_ and _When a test cannot be linked_ — follow it.
- **`#gaps`** — heading "Coverage gaps & imbalances": behaviors with no coverage, and any shape
  wrong for its repo (ice-cream-cone, over-unit-tested, trivial tests). **Order by severity**,
  highest first, so a Critical uncovered behavior leads; Informative behaviors are recorded as
  out-of-scope rather than gaps. Each tied to evidence; findings you could not ground are marked
  `<span class="badge warn">unverified</span>` with a one-line reason.

## Recommendations section markup

Slot this between `#evidence` and `#gaps` in the shared skeleton:

```html
<section id="recommendations">
  <h2>Per-platform recommendations</h2>
  <div class="scroll">
    …per-platform tables: Behavior | Severity | Recommended layer | Tooling |
    Rationale | Evidence (linked)…
  </div>
</section>
```
