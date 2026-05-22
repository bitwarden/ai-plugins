# Bitwarden Design Tools

Apply Bitwarden's brand identity to standalone HTML deliverables — dashboards, recaps, reports, mockups, slide decks, one-pagers — without re-deriving the palette ad-hoc.

## What's in the box

A single skill, **`applying-bitwarden-branding`**, plus the assets and reference docs it ships with.

## Installation

```bash
/plugin install bitwarden-design-tools@bitwarden-marketplace
```

```
skills/applying-bitwarden-branding/
├── SKILL.md
├── references/
│   ├── color-palette.md
│   ├── typography.md
│   └── logo-usage.md
└── assets/
    ├── bitwarden-tokens.css
    ├── bitwarden-lockup-official.svg          (full reference)
    ├── bitwarden-lockup-horizontal-blue.svg   (light-surface primary)
    ├── bitwarden-lockup-horizontal-white.svg  (dark-surface primary)
    ├── bitwarden-lockup-vertical-blue.svg     (light-surface secondary)
    ├── bitwarden-lockup-vertical-white.svg    (dark-surface secondary)
    ├── bitwarden-shield-blue.svg              (chip-scale, light)
    ├── bitwarden-shield-white.svg             (chip-scale, dark)
    ├── bitwarden-wordmark-blue.svg            (wordmark only, light)
    └── bitwarden-wordmark-white.svg           (wordmark only, dark)
examples/
└── on-brand-one-pager.html
```

## When it fires

Triggers on direct asks — _"make this look like Bitwarden"_, _"Bitwarden-themed dashboard"_, _"apply our branding"_, _"add the Bitwarden logo"_, _"on-brand"_ — and also on any standalone HTML deliverable request inside this marketplace where the user hasn't specified a different brand. Inside Bitwarden, on-brand is the default.

It does **not** fire on:

- Product UI in `bitwarden/clients`, the web vault, or mobile apps — those use `@bitwarden/components`, which is a separate design system.
- Third-party brand work or partner co-branding.

## Canonical vs. pragmatic — the dividing line

The skill is explicit about this distinction, and you should be too when reading it.

**Canonical** (lifted directly from [`bitwarden.com/brand`](https://bitwarden.com/brand)):

- The published color palette (Bitwarden Blue, Deep Blue, Teal, Light Teal, Green, Red, Yellow, and the neutral ramp).
- **Inter** as the primary typeface.
- The official logo lockup (horizontal preferred), clear-space rules, and the canonical SVG URL.
- The **36px rounded-radius foundation** — "buttons are the only exception."

**Pragmatic** (the brand site is silent — the deliverable still has to choose):

- Dark vs. light surface mode.
- Specific heading scale, line height, weight choices.
- Code-font choice.
- Component shapes (cards, banners, chips, toolbars, badges).
- Voice/tone.
- Accessibility/contrast specifics (defer to WCAG AA).

The skill suggests safe defaults for the pragmatic items but never pretends they are brand canon.

## Source of truth

[`bitwarden.com/brand`](https://bitwarden.com/brand) is the only canonical source. If you find a conflict between this plugin and the brand site, the brand site wins — file an issue so the plugin can be corrected.

## See it applied

Open [`examples/on-brand-one-pager.html`](examples/on-brand-one-pager.html) in a browser. It demonstrates the canonical bits applied correctly — palette, Inter, shield, 36px radius — and is intentionally plain so it doesn't telegraph a component vocabulary. **One valid composition, not the prescribed composition.**

## Out of scope

- Product UI styling. Use `@bitwarden/components` in `bitwarden/clients`.
- A Bitwarden component vocabulary. Not part of brand canon.
- Voice/tone guide. Not in the brand site yet.
