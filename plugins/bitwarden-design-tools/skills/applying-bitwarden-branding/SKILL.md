---
name: applying-bitwarden-branding
description: Apply Bitwarden brand standards — logo usage, color palette, typography, iconography, and capitalization rules — grounded in bitwarden.com/brand and the bitwarden/brand repository.
when_to_use: Use when a task touches Bitwarden's visual brand surface in design work or design-adjacent assets. Triggers — "check the brand", "apply Bitwarden branding", "use the brand colors", "is this on-brand", "what color is Bitwarden blue", "what font does Bitwarden use", "logo usage", "brand guidelines", "brand assets", "shield". Not for product content voice or grammar (use `content-style-guide`).
allowed-tools: Skill
---

# Applying Bitwarden Branding

This skill grounds brand-application decisions in Bitwarden's two canonical sources:

- **[bitwarden.com/brand](https://bitwarden.com/brand/)** — the brand guidelines hub, including
  logo lockups, the radius system, social-post framing, product images, and B-roll.
- **[github.com/bitwarden/brand](https://github.com/bitwarden/brand)** — the source-of-truth
  repository for SVG logos, PNG product icons (multiple sizes), the shield mark, color palette
  in multiple formats (HEX, HSL, SCSS), screenshots, and media assets.

When applying brand in real work, treat the repo as canonical for assets and the brand site as
canonical for usage rules. Detailed reference material lives in `references/brand-assets.md`
(asset inventory and file paths) and `references/color-palette.md` (full palette with usage
notes and SCSS variable names).

## The five rules that catch the most mistakes

1. **Capitalize the B in Bitwarden.** Always. The W is never capitalized. The only place
   "bitwarden" appears lowercase is inside the official logo lockup — not in body copy, not in
   headlines, not in handles or URLs.
2. **Primary palette before tertiary palette.** Green, Yellow, and Red are tertiary — use them
   sparingly, primarily in product graphics and for success / warning / error communications.
   They are not headline colors.
3. **Inter for everything.** Product and website. The available weights are 300 (light), 400
   (regular), 500 (medium), 600 (semi-bold), and 700 (bold).
4. **Logo safe-area is non-negotiable.** Horizontal lockup needs one Bitwarden-shield width of
   clear space on every side. Vertical lockup uses the height of the "X" in the logotype.
   Cramped logos break the lockup.
5. **36px radius system, but buttons are the exception.** Rounded corners follow a 36px radius
   across primary brand surfaces. Buttons sit outside that system — don't apply 36px to
   buttons.

## Logo usage

- **Default mark.** `/logos/logo-horizontal-blue.svg` from the brand repo. Horizontal is the
  primary/preferred lockup.
- **Inverse (for dark backgrounds).** `/logos/logo-horizontal-white.svg`.
- **Vertical lockup.** Available for use cases where horizontal doesn't fit; the safe area uses
  the height of the "X" in the logotype.
- **Product icon (the shield).** Available rounded and square, at 16/32/64/128/256 px PNG plus
  SVG (`/logos/icon.svg`, `/logos/icon-inverse.svg`, `/icons/*.png`). The shield itself lives
  at `/shield/`.
- **Product logos.** Unique lockups exist for individual Bitwarden products (Password Manager,
  Secrets Manager, etc.). Use these "primarily for use in-product."

Don't recolor, distort, rotate, or recompose the logo. If the supplied SVG doesn't fit the
need, reach out to the brand owners rather than improvising a variant.

## Color palette quick reference

Full palette with all variable names is in `references/color-palette.md`. Five colors carry
most of the work:

| Color          | HEX       | Use                                                    |
| -------------- | --------- | ------------------------------------------------------ |
| Bitwarden Blue | `#175DDC` | Primary brand color. Headlines, primary CTAs, accents. |
| Deep Blue      | `#0C3276` | Secondary brand color. Dense surfaces, headers.        |
| Off White      | `#F3F6F9` | Default light surface.                                 |
| True Black     | `#000000` | Default text on light surfaces.                        |
| Teal Highlight | `#2CDDE9` | Accent and highlight — pair with the blues.            |

Tertiary palette (Green `#7BF1A8`, Yellow `#FDC700`, Red `#FF6550`) is **sparingly** applied
for product graphics and success/warning/error states. The brand site is explicit on this.

SCSS variable names (from the brand repo's `brand-colors/palette.scss`):

- `$bitwarden-blue`, `$deep-blue`, `$off-white`, `$true-white`, `$true-black`, `$light-grey`,
  `$teal-highlight`, `$light-teal-highlight`, `$tertiary-green`, `$tertiary-yellow`,
  `$tertiary-red`.

## Typography

- **Typeface:** Inter (open-source, Google Fonts).
- **Weights available:** 300 (light), 400 (regular), 500 (medium), 600 (semi-bold), 700 (bold).
- **Use:** product UI and website body / headline copy. The brand site doesn't enumerate
  weight-per-context rules; defer to product or marketing leads when an unusual case comes up.

## Iconography

- **Web icons.** Designed for a wide range of uses with more detail than the product icon.
- **Product icon (shield).** Available rounded and square at multiple sizes from the brand
  repo's `/icons/` directory.

Asset paths and full sizing tables are in `references/brand-assets.md`.

## Capitalization and trademark

- The "B" in **Bitwarden** is capitalized in all copy text.
- The "W" is never capitalized — neither `BITWARDEN` (in body copy) nor `bitWarden`.
- The only place "bitwarden" appears in lowercase is inside the official logo lockup itself.
- "Bitwarden" is a registered trademark of Bitwarden Inc. — surface this when content is
  external-facing and trademark attribution is appropriate.

## Composing with other skills

- **`content-style-guide`.** Brand sits alongside content style. When reviewing user-visible
  surfaces, walk both: this skill catches color, logo, and capitalization issues; the content
  style guide catches voice, tone, sentence case, and accessibility.
- **`using-figma`.** Use `get_variable_defs` to check whether a design's colors are
  library-bound and aligned to the brand palette; use `get_libraries` to confirm the right
  design library is loaded before claiming a design is on-brand.
- **`preparing-design-handoff`.** Surface brand findings as part of the handoff gate — flag
  them as Figma annotations or as open questions in the Epic when something is off-brand at
  handoff time. Don't quietly fix.
- **`evolving-design-system-components`.** New patterns must respect the brand palette and the
  36px radius system (with the button exception). The Component Library governance review
  catches obvious violations, but raise them explicitly when sponsoring a pattern.

## Output format for brand checks

When asked "is this on-brand?", structure the response as:

1. **What's checked** — which brand surfaces this design touches (logo, color, typography,
   iconography, capitalization).
2. **What's on-brand** — what's working and should stay.
3. **What's off-brand** — each finding tied to the specific brand rule it violates (cite the
   section, e.g., "Tertiary palette overused — Green appears in three non-state surfaces, per
   the bitwarden.com/brand tertiary-usage rule").
4. **Proposed corrections** — concrete swaps the designer can apply, sourced from the canonical
   palette or asset.

Keep findings specific. "The headline uses `#7BF1A8` (tertiary green) where Bitwarden Blue
(`#175DDC`) is the brand-primary color" beats "the color is wrong."

## Additional resources

- **`references/brand-assets.md`** — full inventory of brand repo assets with file paths
  (logos, icons, shield, screenshots, media assets).
- **`references/color-palette.md`** — full palette with HEX, HSL, SCSS variable names, and
  per-color usage notes.
