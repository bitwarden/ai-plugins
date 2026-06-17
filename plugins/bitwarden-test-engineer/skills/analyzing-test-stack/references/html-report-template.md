# HTML report template

Produce a **single self-contained HTML file**: all CSS inline in a `<style>` block, no
external/CDN links, no required JavaScript, no web fonts. It must render correctly opened
directly from disk and survive being attached to a ticket or PR.

Write it to the **current working directory** as
`test-stack-report-<slug>-<date>.html` (slug = ticket key / PR number / feature name in
kebab-case; date = the caller-provided date, `YYYY-MM-DD`).

## Styling — binding

Inline the paste-ready stylesheet from `../../../references/report-style-tokens.md` **verbatim**
into the `<style>` block. The report uses a deliberately off-brand, low-key _data-report_
visual system (flat white paper, monospace for data/labels/chrome, sans for prose, a
sequential layer ramp). Do not re-pick colors, do not invent additional layer tokens, do
not reintroduce a brand skin, do not add `<link>`/`@font-face`/CDN imports. The layer →
token mapping (unit / integration / e2e) and the badge → token mapping
(assumption / warn / ok) are normative wherever rendered — chips, distribution bars,
table cells, and recommendation rows.

Section headings are auto-numbered by CSS (`01 · …`) — write a plain `<h2>` per section
and do not hand-number. Wrap each wide table in `<div class="scroll">…</div>` so it
scrolls rather than overflows on narrow widths.

## Required sections, in order

Each section uses the **normative `id` listed below**. Do not rename, omit, or add
top-level sections — readers look these up by id.

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
   a `.plat` name plus the one-line shape (e.g. "server: integration-heavy, thin unit;
   clients: integration + 1 E2E journey"). No JS. See `../../../references/report-style-tokens.md`
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
   row per behavior. The **Severity** cell carries the behavior's risk severity
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

6. **`#gaps`** — Coverage gaps & imbalances — behaviors with no coverage, and any
   trophy-wrong shape observed (ice-cream-cone, over-unit-tested, trivial tests). **Order
   the list by severity**, highest first, so a Critical uncovered behavior leads and the
   reader resolves the worst-impact gaps first; Informative behaviors are recorded as
   out-of-scope rather than gaps. Each tied to evidence. Findings you could not ground
   belong here, marked `unverified` with a one-line reason.

## Content rules

- Tables over prose for recommendations and evidence — they're meant to be scanned and
  acted on.
- Mark every assumption inline with `<span class="badge assumption">assumption</span>`
  so the reader can tell grounded calls from inferred ones.
- Flag unverifiable claims with `<span class="badge warn">unverified</span>` (e.g.
  E2E coverage claimed without the `test` repo checked out).
- No tracking, no remote resources, no secrets. The file is shareable as-is.

## Skeleton

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Test Stack Report — {{change}}</title>
    <style>
      /* Paste the full paste-ready stylesheet from
         ../../../references/report-style-tokens.md here, verbatim. */
    </style>
  </head>
  <body>
    <header>
      <p class="eyebrow">Test Stack Report</p>
      <h1>…the change under analysis…</h1>
      <p class="meta">…ticket/PR · status · team · date…</p>
    </header>
    <main>
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
            <span class="plat">bitwarden/server</span> — integration-heavy, thin
            unit, 1 E2E journey
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
  </body>
</html>
```
