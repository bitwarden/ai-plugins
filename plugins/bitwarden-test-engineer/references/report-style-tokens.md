# Report style tokens — data-report visual system for HTML reports

This file is the **single source of styling truth** for every self-contained HTML report the
`bitwarden-test-engineer` plugin emits — the `analyzing-test-stack` test-stack report and the
`assessing-test-coverage` coverage report alike. The HTML output requirements (single file,
inline CSS, no external/CDN assets, no web fonts, no JS) mean a report cannot `<link>` to a
design system at runtime — instead, **inline the stylesheet block at the bottom of this file
verbatim** into the report's `<style>` element.

The look is deliberately **not** a brand skin. It is a quiet, ink-on-paper _data report_
— the aesthetic of a statistical notebook or a coverage readout, where the data is the
hero and nothing decorates. Every report ships the same system so two reports read as the
same instrument. Do not re-pick colors, fonts, or layer tokens per report.

## Design intent (why these choices)

- **Flat paper, no chrome.** White page, hairline rules, no cards, no shadows, no
  rounded panels. Sections are separated by a single rule and whitespace. Simple and
  low-key by construction.
- **Monospace is a structural role, not just for code.** Section numbers, eyebrows,
  table headers, layer/badge chips, axis labels, counts, and SHAs are all set in
  the system monospace stack. Prose is set in the system sans stack. The split makes
  "data" and "argument" visually distinct and gives the report its notebook character
  without any web font.
- **The layer ramp is sequential, because the layers are ordered.** unit → integration
  → e2e is a cost/depth sequence (cheapest/shallowest → most expensive/deepest). A
  single-hue light→dark ramp encodes that order honestly; a thin dark sliver therefore
  reads as "expensive, used sparingly." Do not swap it for unrelated categorical hues.
- **State colors are categorical and muted.** The assumption/warn/ok badges each carry
  exactly one meaning. Muted traffic colors, not saturated brand colors.

## Token → meaning mapping (binding)

These mappings are **normative**. Do not re-pick colors per report.

### Layer tokens (used wherever a Testing Trophy layer is rendered — chips, distribution bars, table cells)

| Layer       | Token           | HEX       | Role in the ramp                 |
| ----------- | --------------- | --------- | -------------------------------- |
| unit        | `--unit`        | `#8FB3D1` | lightest — cheapest / shallowest |
| integration | `--integration` | `#3F7196` | mid — the trophy's bulge         |
| e2e         | `--e2e`         | `#1D3A54` | deepest — most expensive, thin   |

`unit` is light, so layer chips and bar segments at the unit layer use **dark** text
(`--on-unit`); integration and e2e use **white** text (`--on-deep`).

### Badge / state tokens

| Badge      | Token    | Use                                             |
| ---------- | -------- | ----------------------------------------------- |
| assumption | `--warn` | Anything inferred without direct evidence       |
| warn       | `--bad`  | Risks, missing-input flags, unverifiable claims |
| ok         | `--ok`   | Confirmed coverage, grounded calls              |

All badge chips use white (`--on-state`) text on these muted fills — the one
contrast tradeoff in the system, kept legible by bold mono chip text at small sizes.

### Surface, ink, and structural tokens

| Token         | HEX       | Use                                           |
| ------------- | --------- | --------------------------------------------- |
| `--paper`     | `#FFFFFF` | Page background (flat — no cards)             |
| `--panel`     | `#F4F6F8` | Inline code, chart track, table row hover     |
| `--ink`       | `#16191D` | Primary text                                  |
| `--ink-soft`  | `#585F68` | Secondary text, captions, table cells of note |
| `--ink-faint` | `#818892` | Eyebrows, section numbers, axis labels        |
| `--rule`      | `#E4E7EA` | Hairlines, dividers, table row borders        |
| `--link`      | `#2F6E9E` | Links                                         |

## Typography

System fonts only — **no web fonts, no `@font-face`, no CDN imports**. Two roles, mapped
to two stacks via `--sans` (prose) and `--mono` (data, labels, chrome):

```
--sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif
--mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace
```

## Graphics — the layer-distribution chart

The one graphic the report needs is the **recommended layer distribution per platform**,
rendered as a normalized horizontal **stacked bar** (a `<figure>` captioned `Fig 1`):

- One `.dist-row` per platform: a right-aligned `.dist-label` (the platform) and a
  `.bar` track holding one `.seg` per layer present.
- **Segment width is proportional to the recommended test count at that layer** — set it
  with an inline `style="flex: <count>"`. The flex values are the raw counts; the browser
  normalizes them to fill the track. Do not hand-compute percentages or pixel widths.
- Each segment shows its **count** as a monospace label inside it; the shared `.legend`
  above maps color → layer. A `figcaption` names the figure. The unit segment carries
  **dark** text (`--on-unit`) like the unit chip; integration and e2e segments carry
  white (`--on-deep`).

This replaces any arbitrary fixed-width bar. The chart is the report's signature: keep
everything around it quiet so it reads.

## Paste-ready stylesheet

Paste the entire block below — unchanged — into the report's `<style>` element, as a single
contiguous block. **Both report templates inline this identically** — the coverage report
(`assessing-test-coverage`'s `coverage-report-template.md`) and the test-stack report
(`analyzing-test-stack`'s `html-report-template.md`). Do not prune unused selectors, do not
reorder, and do not let one report carry a trimmed copy; that is exactly how two reports that
claim the same system drift apart. Component classes (`.layer.*`, `.badge.*`,
`.dist`/`.seg.*`, `.shapes`, etc.) are part of the binding contract — both templates reference
them by name.

```css
:root {
  /* Surfaces & ink — flat paper, no cards or shadows */
  --paper: #ffffff;
  --panel: #f4f6f8;
  --ink: #16191d;
  --ink-soft: #585f68;
  --ink-faint: #818892;
  --rule: #e4e7ea;

  /* Layer ramp — SEQUENTIAL: ordered cheap/shallow -> costly/deep */
  --unit: #8fb3d1;
  --integration: #3f7196;
  --e2e: #1d3a54;
  --on-unit: #16191d; /* --unit is light: use dark text */
  --on-deep: #ffffff; /* white text on integration/e2e */

  /* Verdict & state — muted categorical */
  --ok: #43875a;
  --warn: #b07d2f;
  --bad: #bf564a;
  --on-state: #ffffff;

  --link: #2f6e9e;

  --sans:
    system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --mono:
    ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, "Liberation Mono",
    monospace;
}

* {
  box-sizing: border-box;
}
html {
  -webkit-text-size-adjust: 100%;
}

body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font: 15px/1.6 var(--sans);
  font-feature-settings: "tnum" 1; /* tabular figures where supported */
}

a {
  color: var(--link);
  text-decoration: underline;
  text-underline-offset: 2px;
  text-decoration-thickness: 1px;
}
a:focus-visible,
summary:focus-visible {
  outline: 2px solid var(--link);
  outline-offset: 2px;
}

/* Masthead */
header {
  max-width: 60rem;
  margin: 0 auto;
  padding: 56px 32px 28px;
}
header .eyebrow {
  margin: 0 0 14px;
  font: 600 11px/1 var(--mono);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--ink-faint);
}
header h1 {
  margin: 0 0 12px;
  font-size: 28px;
  line-height: 1.2;
  font-weight: 650;
  letter-spacing: -0.01em;
}
header .meta {
  font: 12px/1.6 var(--mono);
  color: var(--ink-soft);
}
header .meta a {
  color: var(--ink-soft);
}

/* Sections — flat, hairline-separated, auto-numbered */
main {
  max-width: 60rem;
  margin: 0 auto;
  padding: 0 32px 96px;
  counter-reset: sec;
}
section {
  counter-increment: sec;
  padding: 36px 0;
  border-top: 1px solid var(--rule);
}
section:first-of-type {
  border-top: 0;
}
section > h2 {
  margin: 0 0 18px;
  font-size: 19px;
  font-weight: 650;
  letter-spacing: -0.01em;
}
section > h2::before {
  content: counter(sec, decimal-leading-zero);
  display: inline-block;
  margin-right: 12px;
  font: 600 12px/1 var(--mono);
  letter-spacing: 0.1em;
  color: var(--ink-faint);
  vertical-align: 2px;
}
section h3 {
  margin: 28px 0 10px;
  font: 600 11px/1.3 var(--mono);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-soft);
}

/* Prose */
p {
  margin: 0 0 14px;
  max-width: 72ch;
}
.lead {
  font-size: 16px;
}
.small {
  font-size: 12.5px;
  color: var(--ink-soft);
}
ul.tight {
  margin: 8px 0 16px;
  padding-left: 20px;
}
ul.tight li {
  margin: 0 0 6px;
}
ol {
  padding-left: 22px;
}
ol li {
  margin: 0 0 10px;
}
code {
  font: 0.86em var(--mono);
  background: var(--panel);
  padding: 1px 5px;
  border-radius: 3px;
}

/* Tables — heavy header rule, hairline rows */
.scroll {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 4px 0 18px;
  font-size: 13.5px;
}
thead th {
  text-align: left;
  vertical-align: bottom;
  padding: 0 12px 8px;
  font: 600 10.5px/1.3 var(--mono);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ink-faint);
  border-bottom: 1px solid var(--ink);
}
tbody td {
  vertical-align: top;
  padding: 10px 12px;
  border-bottom: 1px solid var(--rule);
}
tbody tr:hover {
  background: var(--panel);
}
th:first-child,
td:first-child {
  padding-left: 0;
}
th:last-child,
td:last-child {
  padding-right: 0;
}

/* Layer chip */
.layer {
  display: inline-block;
  font: 600 10.5px/1.6 var(--mono);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 2px;
  white-space: nowrap;
}
.layer.unit {
  background: var(--unit);
  color: var(--on-unit);
}
.layer.integration {
  background: var(--integration);
  color: var(--on-deep);
}
.layer.e2e {
  background: var(--e2e);
  color: var(--on-deep);
}

/* Layer-distribution chart (the signature graphic) */
figure {
  margin: 18px 0;
}
figcaption {
  margin-bottom: 14px;
  font: 11px/1.4 var(--mono);
  letter-spacing: 0.04em;
  color: var(--ink-faint);
}
.dist .legend {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  margin-bottom: 14px;
  font: 11px/1 var(--mono);
  color: var(--ink-soft);
}
.dist .legend .key {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.dist .legend .key::before {
  content: "";
  width: 10px;
  height: 10px;
  border-radius: 2px;
  background: var(--rule);
}
.dist .legend .unit::before {
  background: var(--unit);
}
.dist .legend .integration::before {
  background: var(--integration);
}
.dist .legend .e2e::before {
  background: var(--e2e);
}
.dist-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 7px 0;
}
.dist-row .dist-label {
  flex: 0 0 14ch;
  text-align: right;
  font: 11px/1.3 var(--mono);
  color: var(--ink-soft);
  word-break: break-word;
}
.dist-row .bar {
  flex: 1;
  display: flex;
  height: 24px;
  background: var(--panel);
  border-radius: 3px;
  overflow: hidden;
}
.bar .seg {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  font: 600 11px/1 var(--mono);
  color: var(--on-deep);
}
.bar .seg.unit {
  background: var(--unit);
  color: var(--on-unit);
}
.bar .seg.integration {
  background: var(--integration);
}
.bar .seg.e2e {
  background: var(--e2e);
}

/* Per-platform recommended-shape list (replaces card blocks) */
ul.shapes {
  margin: 6px 0 0;
  padding: 0;
  list-style: none;
}
ul.shapes li {
  padding: 10px 0;
  border-top: 1px solid var(--rule);
}
ul.shapes li:first-child {
  border-top: 0;
}
ul.shapes .plat {
  font: 600 13px/1.5 var(--mono);
}

/* Badges */
.badge {
  display: inline-block;
  font: 600 10px/1.5 var(--mono);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 1px 6px;
  border-radius: 2px;
  color: var(--on-state);
  white-space: nowrap;
}
.badge.assumption {
  background: var(--warn);
}
.badge.warn {
  background: var(--bad);
}
.badge.ok {
  background: var(--ok);
}

/* Unlinkable evidence */
.unlinkable {
  font: italic 12px/1.4 var(--mono);
  color: var(--ink-faint);
}

@media (max-width: 720px) {
  header,
  main {
    padding-left: 20px;
    padding-right: 20px;
  }
  .dist-row {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }
  .dist-row .dist-label {
    flex: none;
    text-align: left;
  }
}

@media print {
  body {
    font-size: 11pt;
  }
  section {
    break-inside: avoid;
    border-top-color: #ccc;
  }
  tbody tr:hover {
    background: none;
  }
  a {
    color: var(--ink);
  }
}
```

## What not to do

- Do not reintroduce a brand skin — no saturated brand blue/yellow, no logo images, no
  `<link>` to a design system. The report is intentionally off-brand and self-contained.
- Do not swap the sequential layer ramp for unrelated categorical hues; the order is the
  encoding.
- Do not introduce web fonts, CDN links, or `<link rel="stylesheet">` — the single-file
  constraint is binding.
- Do not narrow the stylesheet down to "only the classes this report uses." The template
  ships the full stylesheet so a reader inspecting any report sees the same system.
- Do not hand-compute the distribution bar widths in pixels or percentages — set
  `flex: <count>` per segment and let the browser normalize.
