# Bitwarden Brand Asset Inventory

The canonical source is the [bitwarden/brand](https://github.com/bitwarden/brand) GitHub
repository. Use raw GitHub URLs (`https://github.com/bitwarden/brand/raw/main/<path>`) or clone
the repo when assets are needed locally. Paths below are repo-relative.

## Logos

| Asset                        | Path                               | Notes                                       |
| ---------------------------- | ---------------------------------- | ------------------------------------------- |
| Default horizontal (primary) | `/logos/logo-horizontal-blue.svg`  | Use on light backgrounds. Preferred lockup. |
| Inverse horizontal           | `/logos/logo-horizontal-white.svg` | Use on dark backgrounds.                    |
| Vertical lockup              | `/logos/` (see repo)               | Use when horizontal won't fit.              |
| Product icon (default, SVG)  | `/logos/icon.svg`                  | The Bitwarden shield mark.                  |
| Product icon (inverse, SVG)  | `/logos/icon-inverse.svg`          | For dark contexts.                          |

**Safe area:** horizontal lockup needs one Bitwarden-shield width of clear space on every
side. Vertical lockup uses the height of the "X" in the logotype.

**Don't:** recolor, distort, rotate, stretch, recompose, or add effects (shadow, gradient,
outline) to the logo. If a unique need arises, escalate to the brand owners.

## Product icon (shield) — PNG sizes

Both rounded and square variants. The shield is at `/shield/` for the bare-mark version
without rounding or square framing.

| Variant | Sizes available         | Path prefix                       |
| ------- | ----------------------- | --------------------------------- |
| Rounded | 16, 32, 64, 128, 256 px | `/icons/<size>x<size>.png`        |
| Square  | 16, 32, 64, 128, 256 px | `/icons/square-<size>x<size>.png` |

For sizes beyond the table, check `/icons/` in the repo for additional pre-rendered sizes.

## Product logos

Unique lockups exist for individual Bitwarden products (Password Manager, Secrets Manager,
etc.) and are described on [bitwarden.com/brand](https://bitwarden.com/brand/) as "primarily
for use in-product." Source these from the brand site directly rather than reconstructing
them.

## Screenshots and media

| Asset             | Path                                         |
| ----------------- | -------------------------------------------- |
| Product app combo | `/screenshots/apps-combo.png`                |
| Full screenshots  | `/screenshots/` (see repo for all platforms) |
| Media assets      | `/media-assets/` (additional media)          |

The brand site links to Google Drive-hosted Password Manager and Secrets Manager product
images and Vimeo-hosted B-roll footage available for "public use and distribution."

## Source files

The `/src/` directory holds source files for the brand assets (typically Illustrator or
similar). Treat these as designer-only — use the exported SVG/PNG in production work.

## When the asset you need isn't here

- **For a missing format:** check the brand site first (`bitwarden.com/brand`); some assets
  live there but not in the repo.
- **For a missing size:** open an issue on the brand repo with the use case and the requested
  size, rather than scaling up an existing PNG (rounded corners and shield proportions don't
  scale cleanly).
- **For a missing color variant:** don't generate one. The blue and the inverse-white are the
  sanctioned variants. Surface the gap to the brand owners.

## Trademark

"Bitwarden" is a registered trademark of Bitwarden Inc. Apply the ® mark or trademark
attribution per the destination surface's standards (typically first reference per page in
external-facing content; not required in product UI).
