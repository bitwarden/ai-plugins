---
name: applying-bitwarden-branding
description: Apply Bitwarden's canonical brand identity (palette, Inter, official logo lockup, 36px radius foundation) to a standalone HTML deliverable. Fires on direct asks — "make this look like Bitwarden", "Bitwarden-themed dashboard/report/HTML", "apply Bitwarden styling/branding/palette", "add the Bitwarden logo", "on-brand", "brand this", "throw a Bitwarden coat of paint on this" — and ALSO whenever the user asks to build a standalone HTML deliverable (recap, dashboard, slide deck, internal tool, mockup, one-pager, report) without specifying a different brand. Inside the Bitwarden marketplace, on-brand is the default. Does NOT fire for product UI in bitwarden/clients, the web vault, mobile apps (those use @bitwarden/components — a separate design system), third-party brand work, or partner co-branding.
---

# Applying Bitwarden branding

## What this skill is for

Standalone HTML deliverables — dashboards, recaps, reports, mockups, slide decks, one-pagers. Things a person opens, screenshots, and shares.

**Not for product UI.** If the work lives inside `bitwarden/clients`, the web vault, or a mobile app, stop and use `@bitwarden/components`. That's a separate design system with its own tokens, components, and conventions. This skill does not apply.

**Single source of truth:** [`bitwarden.com/brand`](https://bitwarden.com/brand). Everything canonical in this skill comes from there. If you find a conflict, the brand site wins.

## The brand-canon checklist

These four are non-negotiable. They come straight from the brand site.

1. **Use only the published palette.** Bitwarden Blue (`#175DDC`), Deep Blue (`#0C3276`), Teal (`#2CDDE9`), Light Teal (`#A2F4FD`), the semantic Green/Red/Yellow, and the neutral ramp (True White / Off White / Light Grey / Medium Grey / True Black). Don't invent shades, tints, or alternate steps. See [`references/color-palette.md`](references/color-palette.md) for HEX/RGB/CMYK.
2. **Use Inter for type.** Inter is the brand typeface for all headlines, copy, and text. See [`references/typography.md`](references/typography.md) for loading and fallback.
3. **Use the official logo lockup.** Horizontal lockup is preferred; vertical and product-specific lockups exist for specific cases. Honor clear-space rules. Download from the canonical URL — don't recreate the shield from scratch. See [`references/logo-usage.md`](references/logo-usage.md).
4. **Apply the 36px rounded-radius foundation** to container surfaces — panels, cards, hero sections, pills, badges. The brand site is explicit that **buttons are the only canonical exception** to the 36px system.

## Quick start

Three steps to put a deliverable on-brand:

1. **Link Inter.** Add the Google Fonts preconnect and stylesheet to your `<head>` — see [`references/typography.md`](references/typography.md) for the exact snippet.
2. **Drop in the tokens.** Paste the contents of [`assets/bitwarden-tokens.css`](assets/bitwarden-tokens.css) into a `<style>` block in the document, or `<link>` to it directly. This gives you the full palette as CSS custom properties (`--bw-blue`, `--bw-deep-blue`, etc.), the 36px radius, and Inter on `:root`.
3. **Add the lockup.** Pick the variant that matches the surface and the available space — horizontal lockup is preferred. Every variant ships verbatim from the official source under [`assets/`](assets/):
   - Horizontal: `bitwarden-lockup-horizontal-blue.svg` (light surface) / `bitwarden-lockup-horizontal-white.svg` (dark surface)
   - Vertical: `bitwarden-lockup-vertical-blue.svg` / `bitwarden-lockup-vertical-white.svg`
   - Shield only (chip-scale): `bitwarden-shield-blue.svg` / `bitwarden-shield-white.svg`
   - Wordmark only: `bitwarden-wordmark-blue.svg` / `bitwarden-wordmark-white.svg`
   - Full official source: `bitwarden-lockup-official.svg`

   See [`references/logo-usage.md`](references/logo-usage.md) for the full catalog and when to use each.

That's the canonical surface. Everything else is a pragmatic choice the deliverable makes — see below.

## Where the brand site is silent

These decisions still have to be made, but the brand site doesn't prescribe them. Call them pragmatic in the deliverable, not canonical.

- **Surface mode (light vs. dark).** _Pragmatic._ If you have no other guidance, default to a light surface using `--bw-off-white` or `--bw-true-white` with `--bw-deep-blue` for text. For a dark surface, derive the background from `--bw-deep-blue` rather than inventing a new neutral.
- **Type scale (heading sizes, weights, line-heights).** _Pragmatic._ If you have no other guidance, use a four-step scale: display 2.5rem/700, section 1.5rem/600, body 1rem/400, caption 0.8125rem/500. See [`references/typography.md`](references/typography.md).
- **Code font.** _Pragmatic._ If you have no other guidance, `"SF Mono", "JetBrains Mono", Menlo, Consolas, monospace`. The brand site doesn't address code typography.
- **Component shapes (cards, banners, chips, toolbars, badges).** _Pragmatic._ The brand does not define a component vocabulary. Whatever shapes you use, apply the 36px radius to container surfaces (canonical), and pick whatever padding/spacing/border treatment fits the deliverable.
- **Voice/tone.** _Pragmatic._ Not in the brand site yet. Match the audience and channel.
- **Accessibility/contrast specifics.** _Pragmatic._ The brand site doesn't publish a contrast matrix — defer to WCAG AA. See the recommended pairings in [`references/color-palette.md`](references/color-palette.md).

When you make one of these choices, note it in the deliverable so a reader knows it's your call, not brand law.

## References

- [`references/color-palette.md`](references/color-palette.md) — full palette table with HEX/RGB/CMYK, recommended WCAG-AA pairings, and pragmatic surface-mode guidance.
- [`references/typography.md`](references/typography.md) — Inter loading and fallback stack, a pragmatic type scale, and a pragmatic code-font stack.
- [`references/logo-usage.md`](references/logo-usage.md) — lockup choice, clear-space rules, the official SVG URL, the do-not list, and when the bundled inline shield is acceptable.

## See it applied

[`examples/on-brand-one-pager.html`](../../examples/on-brand-one-pager.html) — a single self-contained HTML page demonstrating the canonical bits (palette, Inter, shield, 36px radius) applied correctly across both a **light surface** and a **dark surface** composition. The dark composition is labeled pragmatic — it derives the background from `--bw-deep-blue` and lifts elevated surfaces with a small `--bw-true-white` overlay rather than introducing a new neutral. The page is intentionally plain so it doesn't telegraph a component vocabulary.

**One valid composition, not the prescribed composition.** If you build something richer, that's fine — keep the canon, swap the pragmatics to fit.
