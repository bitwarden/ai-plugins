# Report style tokens — data-report visual system for HTML reports

This file documents the **visual system** for every self-contained HTML report the
`bitwarden-test-engineer` plugin emits — the `analyzing-test-stack` test-stack report and the
`assessing-test-coverage` coverage report alike. The HTML output requirements (single file,
inline CSS, no external/CDN assets, no web fonts, no JS) mean a report cannot `<link>` to a
design system at runtime — the stylesheet must be inlined into the report's `<style>` element.

**You do not retype the stylesheet.** The canonical CSS lives as a real file at
`report-style.css` (alongside this file in the plugin-level `references/` directory) and is
spliced into the report by the `scripts/build-report.sh` build script — never reproduced as
model output. Authoring a
report means writing its **content** (the sections below) into a fragment whose `<style>`
element holds a single sentinel line, then running the build script, which substitutes
`report-style.css` for the sentinel verbatim. See _Building the report_ below. This is what
keeps the two reports on one identical system: they splice the same file, so they cannot drift,
and the ~400-line stylesheet costs zero output tokens per report.

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

### Layer tokens (used wherever a test layer is rendered — chips, distribution bars, table cells)

| Layer       | Token           | HEX       | Role in the ramp                 |
| ----------- | --------------- | --------- | -------------------------------- |
| unit        | `--unit`        | `#8FB3D1` | lightest — cheapest / shallowest |
| integration | `--integration` | `#3F7196` | mid — the confidence layer       |
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

## Combined report — tabs (assembled, not authored)

When both reports are produced for the same change, the build script can assemble them into
**one page with two tabs** — _Current coverage_ (the `assessing-test-coverage` report) and
_Recommended coverage_ (the `analyzing-test-stack` report). This is purely a **presentation**
merge: each skill still authors and builds its own standalone report exactly as before; the
combined page is an _additional_ deliverable stitched from the two finished report files. No
skill or template knows about tabs — the tab markup and its CSS are owned entirely by
`build-report.sh` and `report-style.css`, so the per-skill split stays intact.

You never hand-write the tab markup. The build script reuses each report's `<header>`/`<main>`,
namespaces the normative section ids so the two bodies coexist in one document
(`#overview` → `#cur-overview` / `#rec-overview`, and likewise for the in-page anchor links),
and emits the tab chrome. The mechanism is **CSS-only** (no JavaScript): two visually-hidden
radio inputs (`.tab-input#tab-current` / `#tab-recommended`) drive the active `.tablist label`
and which `.tabpanel[data-panel]` shows, via general-sibling selectors. On print, the tabs
collapse and both panels stack, each titled by its `aria-label`, so a shared PDF carries the
whole analysis. These classes live in the stylesheet's _Tabbed combined report_ block and are
inert in the standalone reports, which never emit them.

## The stylesheet file (binding contract)

The full stylesheet is `report-style.css` (alongside this file). It is the single source of styling truth —
**both** report templates resolve to it through the build script, so the coverage report
(`assessing-test-coverage`'s `coverage-report-template.md`) and the test-stack report
(`analyzing-test-stack`'s `html-report-template.md`) carry byte-identical CSS. Component
classes (`.layer.*`, `.badge.*`, `.dist`/`.seg.*`, `.shapes`, `.unlinkable`, `.toc`, etc.) are
part of the binding contract — both templates reference them by name; the markup you author must
use exactly those class names so the spliced stylesheet styles it. Each report opens its
`<main>` with a `.toc` nav of linked section anchors; in the combined report the build
script namespaces those anchor links per tab.

You never read, reproduce, prune, or hand-edit `report-style.css` when authoring a report —
the build script inlines it whole. If the visual system genuinely needs to change, edit
`report-style.css` once and every future report inherits it.

## Building the report

The model authors a **content fragment** — a complete HTML document whose `<style>` element
contains exactly one line, the sentinel:

```html
<style>
  /* @@BITWARDEN_REPORT_STYLESHEET@@ */
</style>
```

Write that fragment to a temporary path (e.g. `<kind>-report-<slug>.fragment.html`), then run
the build script from the plugin root:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/build-report.sh" \
  --kind <test-stack|test-coverage> --slug <slug> --date <YYYY-MM-DD> \
  <fragment-file>
```

The script replaces the sentinel with `report-style.css` verbatim and writes
`<kind>-report-<slug>-<date>-<HHMMSS>.html` to the current working directory, printing the
final filename to stdout. The `<HHMMSS>` suffix is stamped from the wall clock by the script
(the model cannot read the clock), so **every run gets a fresh filename** — a report is never
overwritten, and an existing report never has to be read back and regenerated. Delete the
temporary fragment afterward. If the script errors (missing sentinel, bad `--kind`/`--date`,
fragment not found) it writes nothing — fix the fragment and re-run rather than falling back to
pasting CSS by hand.

To assemble the **combined two-tab page** from the two already-built standalone reports, call
the script with `--kind test-combined` and the two finished report files (no fragment, no
sentinel — the bodies are reused as-is):

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/build-report.sh" \
  --kind test-combined --slug <slug> --date <YYYY-MM-DD> \
  --current <test-coverage-report-…​.html> \
  --recommended <test-stack-report-…​.html>
```

It writes `test-combined-report-<slug>-<date>-<HHMMSS>.html` and prints the filename. The two
input reports are read, not modified, and their standalone files remain.

## What not to do

- Do not reintroduce a brand skin — no saturated brand blue/yellow, no logo images, no
  `<link>` to a design system. The report is intentionally off-brand and self-contained.
- Do not swap the sequential layer ramp for unrelated categorical hues; the order is the
  encoding.
- Do not introduce web fonts, CDN links, or `<link rel="stylesheet">` — the single-file
  constraint is binding.
- Do not paste, retype, or trim the stylesheet into the fragment — the fragment carries only
  the sentinel, and the build script supplies the full stylesheet. A report that ships a
  hand-copied or "only the classes I used" stylesheet is exactly how two reports drift apart.
- Do not hand-compute the distribution bar widths in pixels or percentages — set
  `flex: <count>` per segment and let the browser normalize.
