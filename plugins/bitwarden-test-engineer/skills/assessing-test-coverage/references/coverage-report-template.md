# Coverage report template

Produce a **single self-contained HTML file** inventorying the existing test coverage for a
change: all CSS inline in a `<style>` block, no external/CDN links, no required JavaScript, no
web fonts. It must render correctly opened directly from disk and survive being attached to a
ticket or PR. This is the coverage counterpart to the `analyzing-test-stack` test-stack report;
the two share one visual system so they read as the same instrument.

Write it to the **current working directory** as
`test-coverage-report-<slug>-<date>.html` (slug = ticket key / PR number / feature name in
kebab-case; date = the caller-provided date, `YYYY-MM-DD`).

## Styling — binding

Inline the paste-ready stylesheet from `../../../references/report-style-tokens.md` (the
plugin-level `references/` directory) **verbatim** into the `<style>` block — the same styling
source the test-stack report uses, pasted identically so the two reports do not drift. Do
not re-pick colors, fonts, or layer tokens, and do not reintroduce a brand skin or any
`<link>`/`@font-face`/CDN import; the off-brand data-report system and the layer/badge token
mappings in that file are binding. The layer chips (`unit` / `integration` / `e2e`), the
badges (`assumption` / `warn` / `ok`), the distribution chart, and the `.unlinkable` span are
all defined there.

Section headings are auto-numbered by CSS (`01 · …`) — write a plain `<h2>` per section and do
not hand-number. Wrap each wide table in `<div class="scroll">…</div>`.

## Required sections, in order

Each section uses the **normative `id` listed below**. Do not rename, omit, or add top-level
sections — readers look these up by id.

1. **Header** (no id; `<header>` element) — report title ("Test Coverage Report"), the change
   under analysis (ticket/PR/feature), and the date.
2. **`#overview`** — A short top-of-report synthesis written so a reader sees the bottom line
   without scrolling. It must contain: a 2–4 sentence recap of how well covered the change is
   per platform (where observed tests concentrate, which layers are bare); the top 3 coverage
   gaps the reader should know about (drawn from `#gaps`); and anchor links into `#coverage`
   and `#gaps`. This report **describes** coverage — it does not recommend new tests or assign
   cheapest-sufficient layers (that is the test-stack report's job); say so in one line and, if
   a test-stack report was also produced, link to it.
3. **`#summary`** — Observed coverage shape — 2–4 sentences, then the **layer-distribution
   chart** rendered exactly per `../../../references/report-style-tokens.md` → _Graphics_, but
   with each `.seg`'s `flex:<count>` set to the **count of observed tests** at that layer for
   the platform (not recommended counts). Caption it `Fig 1 · Observed test coverage by platform`.
   Follow with `<ul class="shapes">`, one `<li>` per platform giving the one-line
   observed shape (e.g. "server: 14 integration, 3 unit, 0 E2E observed"). A platform with no
   observed coverage still gets a row, shown empty.
4. **`#evidence`** — Evidence & sources — a table of what was inspected (which repos/checkouts,
   which PRs read, whether the sibling `test` repo was available) and, explicitly, **what was
   missing or unverifiable** (e.g. "`test` repo not checked out — existing E2E coverage
   unverified"). For PR-sourced records include the captured **head SHA** and **`owner/repo`**
   so the per-test permalinks can be audited against the same commit.
5. **`#coverage`** — Observed coverage — for each affected platform, a table:
   `Behavior / surface | Layer | Test (linked) | Source | Notes`. One row per observed test.
   The **Test (linked)** column is binding: render a GitHub permalink anchored to the captured
   commit SHA and line range —
   `<a href="https://github.com/<owner>/<repo>/blob/<SHA>/<path>#L<start>-L<end>">path/to/file.spec.ts</a>`.
   If a test cannot be linked, use
   `<span class="unlinkable">path/to/file.spec.ts — unlinkable: &lt;reason&gt;</span>` instead
   of fabricating a URL. The **Layer** cell uses the matching layer chip. **Source** is `PR`
   (tests shipped in a linked/merged PR) or `pre-existing` (found by the targeted lookup) —
   keep the observed-vs-assumed distinction visible. Permalink production rules live in
   `finding-coverage.md` → _Citing tests as GitHub permalinks_.
6. **`#gaps`** — Coverage gaps — behaviors/surfaces in the change with **no observed test**,
   each marked `<span class="badge warn">unverified</span>` with a one-line reason (no
   PR-observed test and no targeted hit; or `test` repo unavailable). This is the honest
   record of what is _not_ known to be covered — it is not a recommendation to add tests.

## Content rules

- Tables over prose for the coverage inventory and evidence — they're meant to be scanned.
- Mark anything inferred without direct evidence with
  `<span class="badge assumption">assumption</span>`; confirmed observed coverage may carry
  `<span class="badge ok">ok</span>`.
- Flag unverifiable claims with `<span class="badge warn">unverified</span>` (e.g. E2E
  coverage claimed without the `test` repo checked out).
- Never present assumed coverage as observed, and never fabricate a permalink.
- No tracking, no remote resources, no secrets. The file is shareable as-is.

## Skeleton

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Test Coverage Report — {{change}}</title>
    <style>
      /* Paste the full paste-ready stylesheet from
         ../../../references/report-style-tokens.md here, verbatim. */
    </style>
  </head>
  <body>
    <header>
      <p class="eyebrow">Test Coverage Report</p>
      <h1>…the change under analysis…</h1>
      <p class="meta">…ticket/PR · status · team · date…</p>
    </header>
    <main>
      <section id="overview">
        <h2>Overview</h2>
        …2–4 sentence recap of observed coverage per platform; top 3 gaps;
        anchor links into #coverage and #gaps; one line noting this is a
        coverage inventory, not a recommendation…
      </section>
      <section id="summary">
        <h2>Observed coverage shape</h2>
        …2–4 sentences…
        <figure class="dist">
          <figcaption>Fig 1 · Observed test coverage by platform</figcaption>
          <div class="legend">
            <span class="key unit">unit</span>
            <span class="key integration">integration</span>
            <span class="key e2e">e2e</span>
          </div>
          <div class="dist-row">
            <span class="dist-label">bitwarden/server</span>
            <div class="bar">
              <span class="seg unit" style="flex:3">3</span>
              <span class="seg integration" style="flex:14">14</span>
            </div>
          </div>
          <!-- one .dist-row per platform; empty bar if none observed -->
        </figure>
        <ul class="shapes">
          <li>
            <span class="plat">bitwarden/server</span> — 14 integration, 3 unit,
            0 E2E observed
          </li>
          <!-- one li per platform -->
        </ul>
      </section>
      <section id="evidence">
        <h2>Evidence &amp; sources</h2>
        <div class="scroll">
          …repos inspected + PRs read + test-repo availability + what was
          missing + commit SHA(s)…
        </div>
      </section>
      <section id="coverage">
        <h2>Observed coverage</h2>
        <div class="scroll">
          …per-platform behavior→test tables with linked evidence…
        </div>
      </section>
      <section id="gaps">
        <h2>Coverage gaps</h2>
        …behaviors with no observed test, each marked unverified with a one-line
        reason…
      </section>
    </main>
  </body>
</html>
```
