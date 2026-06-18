# Report HTML — shared authoring contract

Both self-contained HTML reports the `bitwarden-test-engineer` plugin emits — the
`analyzing-test-stack` **test-stack report** and the `assessing-test-coverage` **coverage
report** — are authored against this shared contract, so the two read as one instrument. Each
skill's own template (`html-report-template.md` / `coverage-report-template.md`) covers only what
differs: its section set, its per-platform table columns, and its recommend-vs-inventory framing.
**Read this file first, then that template.**

## Output constraints

Produce a **single self-contained HTML file**: all CSS inline in a `<style>` block, no
external/CDN _resource_ links (stylesheets, fonts, scripts, images), no required JavaScript, no
web fonts. Informational `<a href>` citations to public sources are fine and encouraged — they
are text, not loaded assets (see _Content rules_). It must render correctly opened directly from
disk and survive being attached to a ticket or PR.

You do not write the final file directly and you do not paste any CSS. Author a **content
fragment** (the full HTML document below, but with only a stylesheet sentinel inside `<style>`),
then run the build script. The build mechanics — invocation, output filename, and the `HHMMSS`
freshness stamp — live in `report-style-tokens.md` → _Building the report_ (the single source of
truth); your template only names its `--kind`.

## Styling — binding

Do **not** paste, retype, or trim any CSS. Inside the fragment's `<style>` element put exactly
one line — the sentinel `/* @@BITWARDEN_REPORT_STYLESHEET@@ */` — and the build script splices in
the canonical stylesheet (`report-style.css`) verbatim, identically for both
reports so they cannot drift. The report uses a deliberately off-brand, low-key _data-report_
visual system (flat white paper, monospace for data/labels/chrome, sans for prose, a sequential
layer ramp). Do not re-pick colors, do not invent layer tokens, do not reintroduce a brand skin,
do not add `<link>`/`@font-face`/CDN imports. The layer → token mapping (unit / integration /
e2e) and the badge → token mapping (assumption / warn / ok) are normative wherever rendered —
chips, distribution bars, table cells, and data rows; your markup must use those exact class
names. See `report-style-tokens.md` for the token → meaning contract.

Section headings are auto-numbered by CSS (`01 · …`) — write a plain `<h2>` per section and do
not hand-number. Wrap each wide table in `<div class="scroll">…</div>` so it scrolls rather than
overflows on narrow widths.

## Table of contents

Directly **inside `<main>`, before `#overview`**, emit a linked table of contents:
`<nav class="toc" aria-label="Sections">` holding one `<a href="#…">` per section in the report
(your template lists them), each anchoring its section id. It is a `<nav>`, not a numbered
section. (In the combined two-tab report the build script namespaces these anchor links per tab,
so a panel's ToC jumps within its own panel.)

## Sections common to both reports

Each section uses its **normative `id`** — do not rename, omit, or add top-level sections;
readers look these up by id. The four below are shared; your template defines the report-specific
data section (`#recommendations` or `#coverage`) and the `#gaps` contents, and adds framing notes
for the shared ones (e.g. whether the chart shows recommended or observed counts).

1. **Header** (no id; `<header>` element) — report title, the change under analysis
   (ticket/PR/feature), and the date.
2. **`#overview`** — a short top-of-report synthesis written by the author so a reader sees the
   bottom line without scrolling: a 2–4 sentence recap per platform, the top 3 items the reader
   should resolve (drawn from `#gaps`), and anchor links into the detail sections. Additive — the
   per-behavior detail stays in the tables below. (Your template says what the recap and the
   top-3 are _about_.)
3. **`#summary`** — 2–4 sentences, then the **layer-distribution chart** (the report's signature
   graphic) and a per-platform one-line shape list. Render the chart as a captioned
   `<figure class="dist">` (`Fig 1`) containing a `.legend` and one `.dist-row` per platform;
   each row has a `.dist-label` (the platform) and a `.bar` track holding one `.seg` per layer
   present, sized by `style="flex: <count>"` — the raw count, which the browser normalizes (never
   hand-compute widths). Each `.seg` shows its count; the legend maps color → layer. The unit
   segment carries dark text (`--on-unit`), integration and e2e white (`--on-deep`). Follow with
   `<ul class="shapes">`, one `<li>` per platform: a `.plat` name plus the one-line shape. No JS.
   See `report-style-tokens.md` → _Graphics_ for the chart contract. The chart
   encodes **shape** (counts per layer) only — it is severity-blind. (Your template says whether
   the counts are _recommended_ or _observed_ and supplies the caption.)
4. **`#evidence`** — a table of which inputs were used and, explicitly, **what was missing or
   unverifiable** (e.g. "`test` repo not checked out — existing E2E coverage unverified"). For PR
   inputs include the captured **head SHA** and **`owner/repo`** so per-test permalinks elsewhere
   in the report can be audited against the same commit.

`#gaps` is the last section in both reports; its exact contents differ — see your template.

## Content rules

- Tables over prose for the data sections and evidence — they're meant to be scanned and acted on.
- Mark every assumption inline with `<span class="badge assumption">assumption</span>` so the
  reader can tell grounded calls from inferred ones.
- Flag unverifiable claims with `<span class="badge warn">unverified</span>` (e.g. E2E coverage
  claimed without the `test` repo checked out).
- **Hyperlink every GitHub or Atlassian source the report names.** Cited tests are GitHub
  permalinks (see your template's evidence/coverage rule); any Jira/Confluence/GitHub artifact the
  report names is anchored to its URL, never plain text. **Jira items and Jira-sourced behaviors
  follow `input-sources.md` → _Citing Jira issues as links_** — the link form,
  where to apply it, and the never-fabricate-a-key rule all live there. An informational
  `<a href>` is text, not a fetched resource — it does not violate the no-remote-resources rule.
- No tracking, no remote resources, no secrets — the file is shareable as-is. ("Remote resources"
  means assets the page loads — stylesheets, fonts, scripts, images, CDN imports — not
  informational `<a href>` citations, which are encouraged per the rule above.)
- Keep the fixed **back-to-top** control from the skeleton — the `<a class="to-top" href="#top">`
  after `</main>` paired with `id="top"` on `<header>`. It floats with the reader and jumps to the
  top from anywhere; it is CSS-only (the stylesheet's `.to-top` rule, no JavaScript). Drop either
  half and the anchor breaks.

## Skeleton

The shared document shell. Your template supplies the `<title>`, the eyebrow, the ToC section
list, the report-specific section(s) between `#evidence` and `#gaps`, and the `#summary`/`#gaps`
headings:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>…report title — {{change}}…</title>
    <style>
      /* @@BITWARDEN_REPORT_STYLESHEET@@ */
    </style>
  </head>
  <body>
    <header id="top">
      <p class="eyebrow">…report title…</p>
      <h1>…the change under analysis…</h1>
      <p class="meta">…ticket/PR · status · team · date…</p>
    </header>
    <main>
      <nav class="toc" aria-label="Sections">
        <!-- one <a href="#…"> per section, per your template's section list -->
      </nav>
      <section id="overview">
        <h2>Overview</h2>
        …synthesis: recap per platform; top 3 items; anchor links into the
        detail sections…
      </section>
      <section id="summary">
        <h2>…summary heading…</h2>
        …2–4 sentences…
        <figure class="dist">
          <figcaption>Fig 1 · …layer distribution by platform…</figcaption>
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
          <li><span class="plat">bitwarden/server</span> — …one-line shape…</li>
          <!-- one li per platform -->
        </ul>
      </section>
      <section id="evidence">
        <h2>Evidence &amp; sources</h2>
        <div class="scroll">
          …sources used + what was missing + commit SHA(s)…
        </div>
      </section>
      <!-- report-specific section(s) here, per your template -->
      <section id="gaps">
        <h2>…gaps heading…</h2>
        …per your template…
      </section>
    </main>
    <a class="to-top" href="#top" aria-label="Back to top">Top</a>
  </body>
</html>
```
