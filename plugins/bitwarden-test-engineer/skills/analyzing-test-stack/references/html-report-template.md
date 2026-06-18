# HTML report template

Produce a **single self-contained HTML file**: all CSS inline in a `<style>` block, no
external/CDN _resource_ links (stylesheets, fonts, scripts, images), no required JavaScript,
no web fonts. Informational `<a href>` citations to public sources are fine and encouraged —
they are text, not loaded assets (see _Content rules_). It must render correctly opened
directly from disk and survive being attached to a ticket or PR.

You do not write the final file directly and you do not paste any CSS. Author a **content
fragment** (the full HTML below, but with only a stylesheet sentinel inside `<style>`), then run
the build script — it inlines the stylesheet and stamps the output filename. See _Building the
report_ at the end of this file.

## Styling — binding

Do **not** paste, retype, or trim any CSS. Inside the fragment's `<style>` element put exactly
one line — the sentinel `/* @@BITWARDEN_REPORT_STYLESHEET@@ */` — and the build script splices
in the canonical stylesheet (`../../../references/report-style.css`) verbatim. The report uses a
deliberately off-brand, low-key _data-report_ visual system (flat white paper, monospace for
data/labels/chrome, sans for prose, a sequential layer ramp). Do not re-pick colors, do not
invent additional layer tokens, do not reintroduce a brand skin, do not add
`<link>`/`@font-face`/CDN imports. The layer → token mapping (unit / integration / e2e) and the
badge → token mapping (assumption / warn / ok) are normative wherever rendered — chips,
distribution bars, table cells, and recommendation rows; your markup must use those exact class
names. See `../../../references/report-style-tokens.md` for the token → meaning contract.

Section headings are auto-numbered by CSS (`01 · …`) — write a plain `<h2>` per section
and do not hand-number. Wrap each wide table in `<div class="scroll">…</div>` so it
scrolls rather than overflows on narrow widths.

## Required sections, in order

Each section uses the **normative `id` listed below**. Do not rename, omit, or add
top-level sections — readers look these up by id.

Directly **inside `<main>`, before `#overview`**, emit a linked table of contents:
`<nav class="toc" aria-label="Sections">` holding one `<a href="#…">` per section below
(Overview, Summary, Evidence, Recommendations, Gaps), each anchoring its section id. It is a
`<nav>`, not a numbered section. (In the combined two-tab report the build script namespaces
these anchor links per tab, so a panel's ToC jumps within its own panel.)

1. **Header** (no id; `<header>` element) — report title, the change under analysis
   (ticket/PR/feature), and the date.
2. **`#overview`** — A short top-of-report synthesis written by the analyst, so a reader
   sees the bottom line without scrolling. It must contain: a 2–4 sentence recap of the
   recommended shape per platform; the top 3 open risks the reader must resolve before
   acting (drawn from `#gaps`, **ordered highest severity first**); and anchor links into
   `#recommendations` and `#gaps` for the underlying detail. The overview is additive —
   the per-behavior detail stays in `#recommendations`/`#gaps`.
3. **`#summary`** — Summary & recommended shape — 2–4 sentences, then the
   **layer-distribution chart** (the report's signature graphic) and a per-platform
   one-line shape list. Render the chart as a captioned `<figure class="dist">` (`Fig 1`)
   containing a `.legend` and one `.dist-row` per platform; each row has a `.dist-label`
   (the platform) and a `.bar` track holding one `.seg` per layer present, sized by
   `style="flex: <count>"` where `<count>` is the recommended test count at that layer
   (the browser normalizes; never hand-compute widths). Each `.seg` shows its count; the
   legend maps color → layer. Follow with `<ul class="shapes">`, one `<li>` per platform:
   a `.plat` name plus the one-line shape that matches the repo's actual practice
   (e.g. "server: unit-heavy pyramid, thin integration, no E2E; ios: integration +
   snapshot, no XCUITest"). No JS. See `../../../references/report-style-tokens.md`
   → _Graphics_ for the chart contract. The chart encodes recommended **shape** (counts per
   layer) only; risk severity is carried in the `#recommendations` table's Severity column,
   not in this graphic — leave the chart severity-blind.
4. **`#evidence`** — Evidence & sources — a table of which inputs were used (Jira / PR /
   CSV / tech breakdown / description) and, explicitly, **what was missing or
   unverifiable** (e.g. "`test` repo not checked out — existing E2E coverage
   unverified"). For PR inputs include the captured **head SHA** and **`owner/repo`** so
   per-test permalinks elsewhere in the report can be audited against the same commit.
5. **`#recommendations`** — Per-platform recommendations — for each affected platform, a
   table:
   `Behavior | Severity | Recommended layer | Tooling | Rationale | Evidence (linked)`. One
   row per behavior. When a behavior was extracted from a Jira item (its record carries a
   `source_issue`), the **Behavior** cell appends the linked issue key —
   `… behavior text … <a href="https://bitwarden.atlassian.net/browse/PM-1234">PM-1234</a>` — so
   the row points back at the requirement; a behavior with no Jira source carries no key (see
   `../../../references/input-sources.md` → _Citing Jira issues as links_). The **Severity** cell
   carries the behavior's risk severity
   (Critical / High / Medium / Low / Informative) per the `analyzing-test-stack` skill's
   `references/severity-risk.md`. Render it with the stylesheet's existing inline-code
   treatment — `<code>Critical</code>` — **not** a new color token: the layer ramp and the
   assumption/warn/ok badges are the only colored chips the styling system defines, and
   severity deliberately does not get its own hue. Mark a severity the analyst inferred
   (rather than read from a bug's Jira field) with
   `<span class="badge assumption">assumption</span>`. Use the layer → repo map; E2E rows
   must name the dedicated `test` repo as target.

   **The "Evidence (linked)" column is binding.** For every existing test cited as
   current coverage, render a GitHub permalink anchored to the captured commit SHA and
   line range — `<a href="https://github.com/<owner>/<repo>/blob/<SHA>/<path>#L<start>-L<end>">path/to/file.spec.ts</a>`.
   If a test cannot be linked (no remote, detached HEAD, private fork the agent
   couldn't reach), use `<span class="unlinkable">path/to/file.spec.ts — unlinkable: &lt;reason&gt;</span>`
   instead of fabricating a URL. These records come from the coverage inventory; the
   permalink production rules live in the `assessing-test-coverage` skill's
   `references/finding-coverage.md` → _Citing tests as GitHub permalinks_.

6. **`#gaps`** — Coverage gaps & imbalances — behaviors with no coverage, and any shape
   wrong for its repo observed (ice-cream-cone, over-unit-tested, trivial tests). **Order
   the list by severity**, highest first, so a Critical uncovered behavior leads and the
   reader resolves the worst-impact gaps first; Informative behaviors are recorded as
   out-of-scope rather than gaps. Each tied to evidence, and — where the gap behavior came from
   a Jira item — to its linked source key (same form as `#recommendations`). Findings you could
   not ground belong here, marked `unverified` with a one-line reason.

## Content rules

- Tables over prose for recommendations and evidence — they're meant to be scanned and
  acted on.
- Mark every assumption inline with `<span class="badge assumption">assumption</span>`
  so the reader can tell grounded calls from inferred ones.
- Flag unverifiable claims with `<span class="badge warn">unverified</span>` (e.g.
  E2E coverage claimed without the `test` repo checked out).
- **Hyperlink every GitHub or Atlassian source the report names.** Cited tests are GitHub
  permalinks (see the Evidence rule above), and if the report names the
  [Defect Severity Classification Guide](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2759229512/Severity)
  or any Jira/Confluence/GitHub artifact, anchor it to its URL rather than naming it in plain
  text. An informational `<a href>` to a GitHub/Atlassian page is **text, not a fetched
  resource** — it does not violate the "no remote resources" rule below (which targets loaded
  assets: CSS, fonts, scripts, CDN imports). Do not strip these links to honor the
  self-contained constraint.
- **Link every Jira item, and link each behavior to the Jira item it came from.** Any issue,
  epic, or child key named anywhere in the report (Overview, Summary, Evidence) is an `<a href>`
  to its browse URL — `<a href="https://bitwarden.atlassian.net/browse/PM-1234">PM-1234</a>`,
  never bare key text. And for every behavior in `#recommendations`/`#gaps` that was extracted
  from a Jira item (the record's `source_issue`), append the linked source key to the behavior
  cell so the reader can jump to the requirement. A behavior with no Jira source (PR-only)
  carries no key. See `../../../references/input-sources.md` → _Citing Jira issues as links_ for
  the link form. Never fabricate a key or URL.
- No tracking, no remote resources, no secrets. The file is shareable as-is. ("Remote
  resources" means assets the page loads — stylesheets, fonts, scripts, images, CDN imports —
  not informational `<a href>` citations, which are encouraged per the rule above.)
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
    <title>Test Stack Report — {{change}}</title>
    <style>
      /* @@BITWARDEN_REPORT_STYLESHEET@@ */
    </style>
  </head>
  <body>
    <header id="top">
      <p class="eyebrow">Test Stack Report</p>
      <h1>…the change under analysis…</h1>
      <p class="meta">…ticket/PR · status · team · date…</p>
    </header>
    <main>
      <nav class="toc" aria-label="Sections">
        <a href="#overview">Overview</a>
        <a href="#summary">Summary</a>
        <a href="#evidence">Evidence</a>
        <a href="#recommendations">Recommendations</a>
        <a href="#gaps">Gaps</a>
      </nav>
      <section id="overview">
        <h2>Overview</h2>
        …2–4 sentence recap of the recommended shape per platform; top 3 open
        risks; anchor links into #recommendations and #gaps…
      </section>
      <section id="summary">
        <h2>Summary &amp; recommended shape</h2>
        …2–4 sentences…
        <figure class="dist">
          <figcaption>
            Fig 1 · Recommended layer distribution by platform
          </figcaption>
          <div class="legend">
            <span class="key unit">unit</span>
            <span class="key integration">integration</span>
            <span class="key e2e">e2e</span>
          </div>
          <div class="dist-row">
            <span class="dist-label">bitwarden/server</span>
            <div class="bar">
              <span class="seg unit" style="flex:3">3</span>
              <span class="seg integration" style="flex:11">11</span>
              <span class="seg e2e" style="flex:1">1</span>
            </div>
          </div>
          <!-- one .dist-row per platform -->
        </figure>
        <ul class="shapes">
          <li>
            <span class="plat">bitwarden/server</span> — unit-heavy pyramid,
            thin integration, no E2E
          </li>
          <!-- one li per platform -->
        </ul>
      </section>
      <section id="evidence">
        <h2>Evidence &amp; sources</h2>
        <div class="scroll">
          …sources used + what was missing + commit SHA(s)…
        </div>
      </section>
      <section id="recommendations">
        <h2>Per-platform recommendations</h2>
        <div class="scroll">
          …per-platform tables: Behavior | Severity | Recommended layer |
          Tooling | Rationale | Evidence (linked)…
        </div>
      </section>
      <section id="gaps">
        <h2>Coverage gaps &amp; imbalances</h2>
        …gaps and trophy-wrong shapes; ungrounded findings marked unverified…
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
  --kind test-stack --slug <slug> --date <YYYY-MM-DD> \
  test-stack-report-<slug>.fragment.html
```

`<slug>` is a short kebab-case identifier for the change (ticket key / PR number / feature
name); `<date>` is the caller-provided date. The script splices in `report-style.css`, writes
`test-stack-report-<slug>-<date>-<HHMMSS>.html` to the current working directory (the `HHMMSS`
time suffix is stamped by the script, so each run is a fresh file — nothing is ever
overwritten), and prints the final filename. Delete the temporary fragment afterward, and
report the printed filename to the caller. Do not hand-assemble the final file or paste CSS as a
fallback — if the script errors, fix the fragment and re-run.
