# Report style tokens — data-report visual system for HTML reports

The **visual system** for every self-contained HTML report the `bitwarden-test-engineer` plugin
emits — the `analyzing-test-stack` test-stack report and the `assessing-test-coverage` coverage
report alike. Because the output is a single file with no external assets, the stylesheet is
inlined; both reports splice the **same** canonical CSS so they read as one instrument and cannot
drift.

**You never retype, prune, or hand-edit the stylesheet.** It lives as a real file at
`report-style.css` (alongside this file) and is spliced into the report by `scripts/build-report.sh`
— never reproduced as model output. Authoring a report means writing its **content** (the sections
below) into a fragment whose `<style>` holds a single sentinel line, then running the build script
(see _Building the report_). If the visual system genuinely needs to change, edit `report-style.css`
once and every future report inherits it.

The look is deliberately **not** a brand skin — a quiet, ink-on-paper _data report_ where the data
is the hero and nothing decorates: flat white page, hairline rules, no cards/shadows/rounded panels.

## Design intent (why these choices)

- **Monospace is a structural role.** Section numbers, eyebrows, table headers, layer/badge chips,
  axis labels, counts, and SHAs are set in the system mono stack; prose in the system sans stack.
  The split makes "data" and "argument" visually distinct without any web font.
- **The layer ramp is sequential, because the layers are ordered.** unit → integration → e2e is a
  cost/depth sequence (cheapest/shallowest → most expensive/deepest); a single-hue light→dark ramp
  encodes that order, so a thin dark sliver reads as "expensive, used sparingly." Do not swap it for
  unrelated categorical hues.
- **State colors are categorical and muted.** The assumption/warn/ok badges each carry exactly one
  meaning — muted traffic colors, not saturated brand colors.

## Token → meaning mapping (binding)

These mappings are **normative**. Do not re-pick colors per report. Your markup must use exactly
these class names; the spliced stylesheet styles them.

### Layer tokens (chips, distribution bars, table cells)

| Layer       | Token           | HEX       | Role in the ramp                 |
| ----------- | --------------- | --------- | -------------------------------- |
| unit        | `--unit`        | `#8FB3D1` | lightest — cheapest / shallowest |
| integration | `--integration` | `#3F7196` | mid — the confidence layer       |
| e2e         | `--e2e`         | `#1D3A54` | deepest — most expensive, thin   |

`unit` is light, so its chips and bar segments use **dark** text (`--on-unit`); integration and e2e
use **white** text (`--on-deep`).

### Badge / state tokens

| Badge      | Token    | Use                                             |
| ---------- | -------- | ----------------------------------------------- |
| assumption | `--warn` | Anything inferred without direct evidence       |
| warn       | `--bad`  | Risks, missing-input flags, unverifiable claims |
| ok         | `--ok`   | Confirmed coverage, grounded calls              |

All badge chips use white (`--on-state`) text on these muted fills.

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

Typography is system fonts only — **no web fonts, no `@font-face`, no CDN imports** — split across
`--sans` (prose) and `--mono` (data, labels, chrome).

## Graphics — the layer-distribution chart

The report's signature graphic: the layer distribution per platform, rendered as a normalized
horizontal **stacked bar** (a `<figure>` captioned `Fig 1`).

- One `.dist-row` per platform: a right-aligned `.dist-label` and a `.bar` track holding one `.seg`
  per layer present.
- **Segment width is proportional to the test count at that layer** — set it with inline
  `style="flex: <count>"` (raw counts; the browser normalizes them). Never hand-compute percentages
  or pixel widths.
- Each segment shows its **count** as a monospace label; the shared `.legend` above maps color →
  layer; a `figcaption` names the figure. The unit segment carries dark text (`--on-unit`),
  integration and e2e white (`--on-deep`).

## Building the report

This section is the **single source of truth** for the build invocation; the templates only name
their `--kind`. The model authors a **content fragment** — a complete HTML document whose `<style>`
contains exactly one line, the sentinel:

```html
<style>
  /* @@BITWARDEN_REPORT_STYLESHEET@@ */
</style>
```

Write that fragment to a temporary path (e.g. `<kind>-report-<slug>.fragment.html`), then run the
build script from the plugin root:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/build-report.sh" \
  --kind <test-stack|test-coverage> --slug <slug> --date <YYYY-MM-DD> \
  <fragment-file>
```

It replaces the sentinel with `report-style.css` verbatim and writes the report into a per-change
directory `test-engineer-report-<slug>-<date>/` (created if needed) — the coverage report as
`coverage.html`, the test-stack report as `recommended.html` — then prints the final path. The
directory name derives only from `--slug`/`--date`, so a run's reports share one folder;
**re-running the same change on the same date refreshes the report in place**. Delete the temporary
fragment afterward. If the script errors (missing sentinel, bad `--kind`/`--date`, fragment not
found) it writes nothing — fix the fragment and re-run rather than pasting CSS by hand.

**Combined two-tab page (assembled, not authored).** When both reports exist for one change, the
build script can stitch them into one page with two CSS-only tabs — _Current coverage_ and
_Recommended coverage_. This is a presentation-only merge from the two finished report files: no
skill or template knows about tabs, and the agent (not the report author) runs it with
`--kind test-combined --current test-engineer-report-<slug>-<date>/coverage.html --recommended test-engineer-report-<slug>-<date>/recommended.html`,
which writes `combined.html` into that same directory. The tab chrome lives entirely in the build
script and `report-style.css`.

## What not to do

- Do not reintroduce a brand skin — no saturated brand colors, no logo images, no `<link>` to a
  design system. The report is intentionally off-brand and self-contained.
- Do not swap the sequential layer ramp for unrelated categorical hues; the order is the encoding.
- Do not paste, retype, or trim the stylesheet into the fragment — the fragment carries only the
  sentinel. A report that ships a hand-copied or "only the classes I used" stylesheet is exactly how
  two reports drift apart.
- Do not hand-compute distribution bar widths — set `flex: <count>` per segment.
