# Report HTML — shared authoring contract

Both self-contained HTML reports the `bitwarden-test-engineer` plugin emits — the
`analyzing-test-stack` **test-stack report** and the `assessing-test-coverage` **coverage report** —
are authored against this shared contract, so the two read as one instrument. Each skill's own
template (`html-report-template.md` / `coverage-report-template.md`) covers only what differs: its
section set, its per-platform table columns, and its recommend-vs-inventory framing. **Read this
file first, then that template.**

## Output constraints

Produce a **single self-contained HTML file**: all CSS inline in `<style>`, no external/CDN
_resource_ links (stylesheets, fonts, scripts, images), no required JavaScript, no web fonts. It
must render correctly opened directly from disk and survive being attached to a ticket or PR.
Informational `<a href>` citations to public sources are text, not loaded assets — they are fine and
encouraged (see _Content rules_).

You do not write the final file or paste any CSS: author a **content fragment** (the skeleton below,
with only the stylesheet sentinel inside `<style>`), then run the build script. The fragment/sentinel
mechanics, the build invocation, the normative class names (the layer and assumption/warn/ok tokens
your markup must use), and the visual system are all owned by `report-style-tokens.md` — **read it.**
Your template only names its `--kind`.

Section headings are auto-numbered by CSS (`01 · …`) — write a plain `<h2>` per section, do not
hand-number. Wrap each wide table in `<div class="scroll">…</div>` so it scrolls rather than
overflows on narrow widths.

## Table of contents

Directly **inside `<main>`, before `#overview`**, emit `<nav class="toc" aria-label="Sections">`
holding one `<a href="#…">` per section in the report (your template lists them). It is a `<nav>`,
not a numbered section. (In the combined two-tab report the build script namespaces these anchors per
tab so a panel's ToC jumps within its own panel.)

## Sections common to both reports

Each section uses its **normative `id`** — do not rename, omit, or add top-level sections; readers
look these up by id. The four below are shared; your template defines the report-specific data
section (`#recommendations` or `#coverage`) and the `#gaps` contents, and adds framing notes for the
shared ones (e.g. whether the chart shows recommended or observed counts).

1. **Header** (no id; `<header>` element) — report title, the change under analysis (ticket/PR/
   feature), and the date.
2. **`#overview`** — a short top-of-report synthesis written by the author so a reader sees the
   bottom line without scrolling: a 2–4 sentence recap per platform, the top 3 items the reader
   should resolve (drawn from `#gaps`), and anchor links into the detail sections. Additive — the
   per-behavior detail stays in the tables below.
3. **`#summary`** — 2–4 sentences, then the **layer-distribution chart** (the report's signature
   graphic; markup in the skeleton below) and a per-platform one-line shape list (`<ul class="shapes">`).
   The chart's segment markup and render rules are the contract owned by `report-style-tokens.md` →
   _Graphics_; it encodes **shape** (counts per layer) only — it is severity-blind. (Your template says
   whether the counts are _recommended_ or _observed_ and supplies the caption.)
4. **`#evidence`** — a table of which inputs were used and, explicitly, **what was missing or
   unverifiable** (e.g. "`test` repo not checked out — existing E2E coverage unverified"). For PR
   inputs include the captured **head SHA** and **`owner/repo`** so per-test permalinks elsewhere can
   be audited against the same commit.

`#gaps` is the last section in both reports; its exact contents differ — see your template.

## Content rules

- Tables over prose for the data sections and evidence — they're meant to be scanned and acted on.
- Mark every assumption inline with `<span class="badge assumption">assumption</span>` and every
  unverifiable claim with `<span class="badge warn">unverified</span>` (e.g. E2E coverage claimed
  without the `test` repo checked out), so grounded calls are distinguishable from inferred ones.
- **Hyperlink every GitHub or Atlassian source the report names** — never plain text. The data
  section's **evidence column** (`Evidence (linked)` in the test-stack report, `Tests (linked)` in
  the coverage report) is binding: render each behavior's 1–3 representative tests as GitHub
  permalinks, or the `.unlinkable` span when a test genuinely cannot be linked — never a fabricated
  URL. Those records come from the coverage inventory; the exact link / `.unlinkable` markup and the
  permalink-production rules are owned by the `assessing-test-coverage` skill's
  `references/finding-coverage.md` → _Citing tests as GitHub permalinks_ and _When a test cannot be
  linked_. **Jira items and Jira-sourced behaviors** follow `input-sources.md` → _Citing Jira issues
  as links_ (link form, where to apply it, never-fabricate-a-key rule). All of these are
  informational `<a href>` citations, not fetched resources, so they don't violate the self-contained
  constraint.
- Keep the fixed **back-to-top** control from the skeleton — the `<a class="to-top" href="#top">`
  after `</main>` paired with `id="top"` on `<header>`. It is CSS-only; drop either half and the
  anchor breaks.

## Skeleton

The shared document shell. Your template supplies the `<title>`, the eyebrow, the ToC section list,
the report-specific section(s) between `#evidence` and `#gaps`, and the `#summary`/`#gaps` headings:

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
