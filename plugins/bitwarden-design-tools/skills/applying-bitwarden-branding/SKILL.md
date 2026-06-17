---
name: applying-bitwarden-branding
description: Apply or review Bitwarden branding on standalone shareable deliverables (dashboards, recaps, reports, slide decks, one-pagers, mockups) and design-adjacent assets. Use when building or auditing a Bitwarden-audience deliverable, on explicit asks like "make this look like Bitwarden", "Bitwarden-themed deck", "is this on-brand?", or "brand-check this", and proactively when producing a shareable deliverable with no other brand specified. Not for product UI in bitwarden/clients, the web vault, or mobile apps (use @bitwarden/components), third-party work, or partner co-branding.
---

# Applying Bitwarden branding

## What this skill is for

Two jobs, one brand canon:

- **Build** an on-brand standalone deliverable: dashboards, recaps, reports, slide decks, one-pagers, mockups. Things a person opens, screenshots, and shares.
- **Review** whether an existing deliverable — or a design-adjacent asset — is on-brand, and say precisely what to fix.

Not for product UI. Work inside `bitwarden/clients`, the web vault, or a mobile app uses `@bitwarden/components` — a separate design system with its own tokens and conventions. This skill does not apply there.

## Single source of truth

[`bitwarden.com/brand`](https://bitwarden.com/brand) and its backing repository [`github.com/bitwarden/brand`](https://github.com/bitwarden/brand). Everything canonical here mirrors those; on any conflict, the brand repository's published values win.

The canon is bundled in this skill (`assets/`, `references/`) so it is available offline and the logo can be embedded verbatim with no network round-trip. The bundle is the reliable default.

Staying current is optional. Bundled values can fall behind the source over time. When network access is available, run the drift guard first:

```
${CLAUDE_PLUGIN_ROOT}/skills/applying-bitwarden-branding/scripts/refresh-brand-canon.sh --verify
```

It fetches the authoritative palette from the brand repository and reports any drift against the bundle. On a reported mismatch, prefer the live value it prints. On error or no network, fall back to the bundled canon. The same script runs in CI to keep the bundle fresh.

## The brand-canon checklist

These four are non-negotiable. They come straight from the brand repository.

1. Use only the published palette: Bitwarden Blue (`#175DDC`), Deep Blue (`#0C3276`), Teal (`#2CDDE9`), Light Teal (`#A2F4FD`), the tertiary Green/Red/Yellow, and the neutral ramp (True White, Off White, Light Grey, Medium Grey, True Black). Invent no shades, tints, or alternate steps. See [`references/color-palette.md`](references/color-palette.md) for HEX/RGB/CMYK.
2. Use Inter for type, across headlines, copy, and text. See [`references/typography.md`](references/typography.md) for loading and fallback.
3. Use the official logo lockup. Horizontal is preferred; vertical and product-specific lockups exist for specific cases. Honor clear-space rules. Embed the bundled SVG verbatim; do not recreate the shield from scratch. See [`references/logo-usage.md`](references/logo-usage.md).
4. Apply the 36px rounded-radius foundation to container surfaces (panels, cards, hero sections, pills, badges). Buttons are the only canonical exception.

## Quick start (build)

Three steps to put a deliverable on-brand:

1. Link Inter. Add the Google Fonts preconnect and stylesheet to the document head. See [`references/typography.md`](references/typography.md) for the exact snippet.
2. Drop in the tokens. Paste the contents of [`assets/bitwarden-tokens.css`](assets/bitwarden-tokens.css) into a style block, or link to it. This provides the full palette as CSS custom properties (`--bw-blue`, `--bw-deep-blue`, and so on), the 36px radius, and Inter on `:root`.
3. Add the lockup. Pick the variant that matches the surface and available space; horizontal is preferred. Every variant ships verbatim from the official source under [`assets/`](assets/):
   - Horizontal: `bitwarden-lockup-horizontal-blue.svg` (light) / `bitwarden-lockup-horizontal-white.svg` (dark)
   - Vertical: `bitwarden-lockup-vertical-blue.svg` / `bitwarden-lockup-vertical-white.svg`
   - Shield only (chip-scale): `bitwarden-shield-blue.svg` / `bitwarden-shield-white.svg`
   - Wordmark only: `bitwarden-wordmark-blue.svg` / `bitwarden-wordmark-white.svg`
   - Full official source: `bitwarden-lockup-official.svg`

   See [`references/logo-usage.md`](references/logo-usage.md) for the full catalog and when to use each.

That is the canonical surface. Everything else is a pragmatic choice — see below.

## Where the brand site is silent

These decisions still have to be made, but the brand site does not prescribe them. Treat them as pragmatic, not canonical.

- Surface mode (light vs. dark). Pragmatic. Default to a light surface (`--bw-off-white` or `--bw-true-white` with `--bw-deep-blue` text). For a dark surface, derive the background from `--bw-deep-blue` rather than inventing a new neutral.
- Type scale (heading sizes, weights, line-heights). Pragmatic. A safe four-step default: display 2.5rem/700, section 1.5rem/600, body 1rem/400, caption 0.8125rem/500. See [`references/typography.md`](references/typography.md).
- Code font. Pragmatic. `"SF Mono", "JetBrains Mono", Menlo, Consolas, monospace`. The brand is silent on code typography.
- Component shapes (cards, banners, chips, toolbars, badges). Pragmatic. The brand defines no component vocabulary. Apply the 36px radius to container surfaces (canonical); choose whatever padding, spacing, and border treatment fits.
- Voice and tone. Pragmatic. Not in the brand site. Match the audience and channel.
- Accessibility and contrast specifics. Pragmatic. No published contrast matrix, so defer to WCAG AA. See the recommended pairings in [`references/color-palette.md`](references/color-palette.md).

When making one of these choices, note it in the deliverable so a reader knows it is a deliverable-level decision, not brand law.

## Reviewing for brand compliance

When asked whether something is on-brand, structure the answer as:

1. What is checked: which brand surfaces the work touches (palette, typography, logo, radius, capitalization).
2. What is on-brand: what works and should stay. Affirm the correct things explicitly; do not only list problems.
3. What is off-brand: each finding tied to the specific canon rule it breaks, citing the actual value. "The headline uses `#46E08A` (off-palette green) where Bitwarden Blue `#175DDC` is the brand primary" beats "the color is wrong".
4. Proposed corrections: concrete swaps sourced from the canonical palette or bundled asset.

Calibrate severity — this is where reviews go wrong. Separate canon violations from brand-silent choices:

- Canon violation (flag it): off-palette color, non-Inter type, a recreated or altered logo, capitalizing the W in Bitwarden. These break the four non-negotiables.
- Brand-silent choice (note as a judgment-call, never a hard failure): the existence of a dark surface mode, the 36px radius on an internal tool, emoji vs. custom icons, a code-font choice, loading Inter from a CDN. The brand does not rule on these. Mention them as optional refinements, but do not mark them as failures or non-negotiable violations. Over-flagging defensible pragmatic choices erodes trust in the review.

## Within the design lifecycle

This skill also serves design work, not only standalone deliverables. When it does:

- `using-figma`. With a Figma URL in play, use `get_variable_defs` to check whether a design's colors are library-bound to the brand palette, and `get_libraries` to confirm the right library is loaded, before declaring a design on-brand.
- `content-style-guide`. Brand sits alongside content. When reviewing user-visible surfaces, walk both: this skill catches color, logo, and capitalization; the style guide catches voice, tone, sentence case, and accessibility.
- `preparing-design-handoff`. Surface brand findings as part of the handoff gate, as Figma annotations or open questions in the Epic. Do not quietly fix.
- `evolving-design-system-components`. New patterns must respect the brand palette and the 36px radius system (buttons excepted). Raise brand concerns explicitly when sponsoring a pattern.

## References

- [`references/color-palette.md`](references/color-palette.md): full palette (HEX/RGB/CMYK), WCAG-AA pairings, pragmatic surface guidance.
- [`references/typography.md`](references/typography.md): Inter loading and fallback, a pragmatic type scale, a pragmatic code-font stack.
- [`references/logo-usage.md`](references/logo-usage.md): lockup choice, clear-space rules, the official SVG URL, the do-not list.

## See it applied

[`examples/on-brand-one-pager.html`](../../examples/on-brand-one-pager.html) applies the canon (palette, Inter, shield, 36px radius) across light and dark compositions. The dark composition is labeled pragmatic — background derived from `--bw-deep-blue`, elevated surfaces lifted with a small `--bw-true-white` overlay, no invented neutral. It is one valid composition, not the prescribed one. Build something richer when appropriate; keep the canon, swap the pragmatics to fit.
