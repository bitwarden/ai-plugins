# Coverage report template

Produce a **single self-contained HTML file** inventorying the existing test coverage for a
change: all CSS inline in a `<style>` block, no external/CDN links, no required JavaScript, no
web fonts. It must render correctly opened directly from disk and survive being attached to a
ticket or PR. This is the coverage counterpart to the `analyzing-test-stack` test-stack report;
the two share one visual system so they read as the same instrument.

You do not write the final file directly and you do not paste any CSS. Author a **content
fragment** (the full HTML below, but with only a stylesheet sentinel inside `<style>`), then run
the build script — it inlines the stylesheet and stamps the output filename. See _Building the
report_ at the end of this file.

## Styling — binding

Do **not** paste, retype, or trim any CSS. Inside the fragment's `<style>` element put exactly
one line — the sentinel `/* @@BITWARDEN_REPORT_STYLESHEET@@ */` — and the build script splices
in the canonical stylesheet (`../../../references/report-style.css`) verbatim. It is the same
styling source the test-stack report uses, spliced identically so the two reports do not drift.
Do not re-pick colors, fonts, or layer tokens, and do not reintroduce a brand skin or any
`<link>`/`@font-face`/CDN import; the off-brand data-report system and the layer/badge token
mappings are binding. The layer chips (`unit` / `integration` / `e2e`), the badges
(`assumption` / `warn` / `ok`), the distribution chart, and the `.unlinkable` span are all
defined in the stylesheet; your markup must use those exact class names. See
`../../../references/report-style-tokens.md` for the token → meaning contract.

Section headings are auto-numbered by CSS (`01 · …`) — write a plain `<h2>` per section and do
not hand-number. Wrap each wide table in `<div class="scroll">…</div>`.

## Required sections, in order

Each section uses the **normative `id` listed below**. Do not rename, omit, or add top-level
sections — readers look these up by id.

Directly **inside `<main>`, before `#overview`**, emit a linked table of contents:
`<nav class="toc" aria-label="Sections">` holding one `<a href="#…">` per section below
(Overview, Summary, Evidence, Coverage, Gaps), each anchoring its section id. It is a `<nav>`,
not a numbered section. (In the combined two-tab report the build script namespaces these anchor
links per tab, so a panel's ToC jumps within its own panel.)

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
   `Behavior / surface | Layer | Tests (linked) | Count | Source | Notes`. **One row per
   behavior**, not per test — match the per-behavior coverage records. When a behavior's record
   carries a `source_issue`, the **Behavior / surface** cell appends the linked issue key —
   `… behavior … <a href="https://bitwarden.atlassian.net/browse/PM-1234">PM-1234</a>` — so the
   row points back at the requirement it came from (see `../../../references/input-sources.md` →
   _Citing Jira issues as links_); a behavior with no Jira source carries no key. The **Tests (linked)**
   column renders the behavior's 1–3 representative permalinks (binding), anchored to the
   captured commit SHA and line range —
   `<a href="https://github.com/<owner>/<repo>/blob/<SHA>/<path>#L<start>-L<end>">path/to/file.spec.ts</a>`;
   the **Count** column gives the approximate number of tests covering that behavior at that
   layer (breadth without enumerating every test). Do not expand a well-covered behavior into
   dozens of rows — that bloats the report and is not what a reader needs.
   If a representative test cannot be linked, use
   `<span class="unlinkable">path/to/file.spec.ts — unlinkable: &lt;reason&gt;</span>` instead
   of fabricating a URL. The **Layer** cell uses the matching layer chip. **Source** is `PR`
   (tests shipped in a linked/merged PR) or `pre-existing` (found by the targeted lookup) —
   keep the observed-vs-assumed distinction visible. Permalink production rules live in
   `finding-coverage.md` → _Citing tests as GitHub permalinks_.
6. **`#gaps`** — Coverage gaps — behaviors/surfaces in the change with **no observed test**,
   each marked `<span class="badge warn">unverified</span>` with a one-line reason (no
   PR-observed test and no targeted hit; or `test` repo unavailable), and — where the behavior
   came from a Jira item — its linked source key (same form as `#coverage`). This is the honest
   record of what is _not_ known to be covered — it is not a recommendation to add tests.

## Content rules

- Tables over prose for the coverage inventory and evidence — they're meant to be scanned.
- Mark anything inferred without direct evidence with
  `<span class="badge assumption">assumption</span>`; confirmed observed coverage may carry
  `<span class="badge ok">ok</span>`.
- Flag unverifiable claims with `<span class="badge warn">unverified</span>` (e.g. E2E
  coverage claimed without the `test` repo checked out).
- Never present assumed coverage as observed, and never fabricate a permalink.
- **Link every Jira item, and link each behavior to the Jira item it came from.** Any issue,
  epic, or child key named anywhere (Overview, Summary, Evidence) is an `<a href>` to its browse
  URL — `<a href="https://bitwarden.atlassian.net/browse/PM-1234">PM-1234</a>`, never bare key
  text. For every behavior row in `#coverage`/`#gaps` whose behavior was extracted from a Jira
  item (the record's `source_issue`), append the linked source key to the behavior cell so the
  reader can jump to the requirement; a behavior with no Jira source carries no key. See
  `../../../references/input-sources.md` → _Citing Jira issues as links_. Never fabricate a key
  or URL. An informational `<a href>` citation is text, not a loaded asset — it does not violate
  the no-remote-resources rule below.
- No tracking, no remote resources, no secrets. The file is shareable as-is.
- Keep the fixed **back-to-top** control from the skeleton — the `<a class="to-top" href="#top">`
  after `</main>` paired with `id="top"` on `<header>`. It floats with the reader and jumps to
  the top of the report from anywhere; it is CSS-only (styled by the stylesheet's `.to-top`
  rule, no JavaScript). Do not drop either half or the anchor breaks.

## Skeleton

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Test Coverage Report — {{change}}</title>
    <style>
      /* @@BITWARDEN_REPORT_STYLESHEET@@ */
    </style>
  </head>
  <body>
    <header id="top">
      <p class="eyebrow">Test Coverage Report</p>
      <h1>…the change under analysis…</h1>
      <p class="meta">…ticket/PR · status · team · date…</p>
    </header>
    <main>
      <nav class="toc" aria-label="Sections">
        <a href="#overview">Overview</a>
        <a href="#summary">Summary</a>
        <a href="#evidence">Evidence</a>
        <a href="#coverage">Coverage</a>
        <a href="#gaps">Gaps</a>
      </nav>
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
    <a class="to-top" href="#top" aria-label="Back to top">Top</a>
  </body>
</html>
```

## Building the report

Write the fragment above (with the `/* @@BITWARDEN_REPORT_STYLESHEET@@ */` sentinel as the only
content of `<style>`) to a temporary path, then run the build script:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/build-report.sh" \
  --kind test-coverage --slug <slug> --date <YYYY-MM-DD> \
  test-coverage-report-<slug>.fragment.html
```

`<slug>` is a short kebab-case identifier for the change (ticket key / PR number / feature
name); `<date>` is the caller-provided date. The script splices in `report-style.css`, writes
`test-coverage-report-<slug>-<date>-<HHMMSS>.html` to the current working directory (the
`HHMMSS` time suffix is stamped by the script, so each run is a fresh file — nothing is ever
overwritten), and prints the final filename. Delete the temporary fragment afterward, and
report the printed filename to the caller. Do not hand-assemble the final file or paste CSS as a
fallback — if the script errors, fix the fragment and re-run.
