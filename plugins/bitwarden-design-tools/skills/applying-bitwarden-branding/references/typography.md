# Typography

Source of truth: [`bitwarden.com/brand`](https://bitwarden.com/brand). The brand site says: _"Inter is an open-source Google font. It is used for all headlines, copy and text."_

## Primary typeface — Inter (canonical)

Use Inter for headlines, body copy, captions — everything except code.

### Loading Inter from Google Fonts

For a one-pager or dashboard that can hit Google's CDN, link Inter with a `preconnect` for performance:

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
  rel="stylesheet"
/>
```

If the deliverable will be opened offline or in an environment that blocks Google Fonts, ship Inter as a self-hosted woff2 — but verify you're using the file released under the SIL Open Font License so redistribution is legitimate.

### Fallback stack

When Inter fails to load, fall back to system sans-serif before the generic. The tokens CSS already sets this on `:root`:

```css
font-family:
  "Inter",
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  Roboto,
  Oxygen,
  Ubuntu,
  Cantarell,
  "Helvetica Neue",
  Arial,
  sans-serif;
```

## Type scale (pragmatic — the brand site is silent)

The brand site doesn't prescribe heading sizes, weights, or line-heights. Anything you choose is a deliverable-level decision, not brand canon.

Reasonable defaults for an HTML one-pager or dashboard:

| Role            | Size             | Weight | Line-height |
| --------------- | ---------------- | ------ | ----------- |
| Display heading | 2.5rem (40px)    | 700    | 1.15        |
| Section heading | 1.5rem (24px)    | 600    | 1.25        |
| Body            | 1rem (16px)      | 400    | 1.55        |
| Caption / label | 0.8125rem (13px) | 500    | 1.4         |

If your deliverable has a stronger existing scale (e.g. a slide template), keep that — it's the right level for that artifact to decide.

## Code typography (pragmatic — the brand site is silent)

The brand site does not address code typography. A reasonable default monospace stack:

```css
font-family:
  "SF Mono", "JetBrains Mono", Menlo, Consolas, "Liberation Mono", monospace;
```

Avoid pairing code in a heavy slab — code should sit visually quieter than body text, not louder.
