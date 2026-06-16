# HTML report template

Produce a **single self-contained HTML file**: all CSS inline in a `<style>` block, no
external/CDN links, no required JavaScript, no web fonts. It must render correctly opened
directly from disk and survive being attached to a ticket or PR.

Write it to the **current working directory** as
`test-stack-report-<slug>-<date>.html` (slug = ticket key / PR number / feature name in
kebab-case; date = the caller-provided date, `YYYY-MM-DD`).

## Required sections, in order

1. **Header** — report title, the change under analysis (ticket/PR/feature), and the date.
2. **Summary & recommended shape** — 2–4 sentences plus a per-platform one-line shape
   (e.g. "server: integration-heavy, thin unit; clients: integration + 1 E2E journey").
   A simple text/CSS trophy bar per platform is welcome; no JS.
3. **Evidence & sources** — a table of which inputs were used (Jira / PR / CSV /
   description) and, explicitly, **what was missing or unverifiable** (e.g. "`test` repo
   not checked out — existing E2E coverage unverified").
4. **Per-platform recommendations** — for each affected platform, a table:
   `Behavior | Recommended layer | Tooling | Rationale | Evidence`. One row per behavior.
   Use the layer→repo map; E2E rows must name the dedicated `test` repo as target.
5. **Coverage gaps & imbalances** — behaviors with no coverage, and any trophy-wrong
   shape observed (ice-cream-cone, over-unit-tested, trivial tests). Each tied to evidence.
6. **Adversarial Review** — a clearly marked placeholder section the
   `challenging-test-stack-recommendations` skill fills in. Leave a labeled empty block,
   e.g. `<section id="adversarial-review"> … to be completed by adversarial pass … </section>`.

## Style guidance

- Keep the palette calm and high-contrast; use color only to distinguish the four layers
  (e.g. static / unit / integration / E2E) consistently wherever they appear.
- Tables over prose for the recommendations and evidence — they're meant to be scanned and
  acted on.
- Mark every assumption inline (e.g. an "assumption" badge) so the adversary and the
  reader can tell grounded calls from inferred ones.
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
      /* inline, self-contained styles only */
    </style>
  </head>
  <body>
    <header>…title, change, date…</header>
    <section id="summary">…recommended shape per platform…</section>
    <section id="evidence">…sources used + what was missing…</section>
    <section id="recommendations">…per-platform behavior→layer tables…</section>
    <section id="gaps">…coverage gaps & imbalances…</section>
    <section id="adversarial-review">
      …filled in by the adversarial pass…
    </section>
  </body>
</html>
```
