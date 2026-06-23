# Bitwarden Color Palette — Full Reference

Source of truth: [bitwarden.com/brand](https://bitwarden.com/brand/) and the
[bitwarden/brand](https://github.com/bitwarden/brand) repository, specifically
`/brand-colors/palette.scss`.

## Branding colors

| Color                | HEX       | RGB             | HSL                      | SCSS variable           |
| -------------------- | --------- | --------------- | ------------------------ | ----------------------- |
| Bitwarden Blue       | `#175DDC` | `23, 93, 220`   | `hsla(219, 81%, 48%, 1)` | `$bitwarden-blue`       |
| Deep Blue            | `#0C3276` | `12, 50, 118`   | `hsla(219, 81%, 25%, 1)` | `$deep-blue`            |
| Off White            | `#F3F6F9` | `243, 246, 249` | `hsla(210, 33%, 96%, 1)` | `$off-white`            |
| True White           | `#FFFFFF` | `255, 255, 255` | `hsla(0, 0%, 100%, 1)`   | `$true-white`           |
| True Black           | `#000000` | `0, 0, 0`       | `hsla(0, 0%, 0%, 1)`     | `$true-black`           |
| Light Grey           | `#D8E2EB` | `216, 226, 235` | —                        | `$light-grey`           |
| Medium Grey          | `#99A7B5` | `153, 167, 181` | —                        | —                       |
| Teal Highlight       | `#2CDDE9` | `44, 221, 233`  | `hsla(184, 81%, 54%, 1)` | `$teal-highlight`       |
| Light Teal Highlight | `#A2F4FD` | `162, 244, 253` | `hsla(187, 96%, 81%, 1)` | `$light-teal-highlight` |

## Tertiary colors

Per the brand site: "Green, Yellow, and Red should be used sparingly, primarily in product
graphics and for success/error communications." Treat them as state colors, not headline
colors.

| Color           | HEX       | RGB             | HSL                      | SCSS variable      | Typical use                |
| --------------- | --------- | --------------- | ------------------------ | ------------------ | -------------------------- |
| Tertiary Green  | `#7BF1A8` | `123, 241, 168` | `hsla(143, 80%, 71%, 1)` | `$tertiary-green`  | Success states             |
| Tertiary Yellow | `#FDC700` | `253, 199, 0`   | `hsla(47, 100%, 50%, 1)` | `$tertiary-yellow` | Warning states             |
| Tertiary Red    | `#FF6550` | `255, 101, 80`  | `hsla(5, 100%, 66%, 1)`  | `$tertiary-red`    | Error / destructive states |

## Token names

The bundled `assets/bitwarden-tokens.css` exposes the palette as CSS custom properties, mapped
from the SCSS source. Cite whichever namespace fits the context.

| SCSS (`palette.scss`)      | CSS custom property |
| -------------------------- | ------------------- |
| `$bitwarden-blue`          | `--bw-blue`         |
| `$deep-blue`               | `--bw-deep-blue`    |
| `$teal-highlight`          | `--bw-teal`         |
| `$light-teal-highlight`    | `--bw-light-teal`   |
| `$tertiary-green`          | `--bw-green`        |
| `$tertiary-yellow`         | `--bw-yellow`       |
| `$tertiary-red`            | `--bw-red`          |
| `$off-white`               | `--bw-off-white`    |
| `$true-white`              | `--bw-true-white`   |
| `$true-black`              | `--bw-true-black`   |
| `$light-grey`              | `--bw-light-grey`   |
| (Medium Grey, no SCSS var) | `--bw-medium-grey`  |

## CMYK (for print)

The brand site lists CMYK alongside HEX/RGB for use in print and produced materials. Pull from
the brand site directly when print specs are needed — these are not in the SCSS file.

| Color           | CMYK            |
| --------------- | --------------- |
| Bitwarden Blue  | 84, 66, 0, 0    |
| Deep Blue       | 100, 91, 26, 12 |
| Off White       | 3, 1, 1, 0      |
| True White      | 0, 0, 0, 0      |
| True Black      | 75, 68, 67, 90  |
| Light Grey      | 14, 6, 3, 0     |
| Medium Grey     | 42, 28, 22, 0   |
| Teal Highlight  | 58, 0, 15, 0    |
| Light Teal      | 30, 0, 5, 0     |
| Tertiary Green  | 49, 0, 30, 5    |
| Tertiary Yellow | 0, 21, 100, 1   |
| Tertiary Red    | 0, 60, 69, 0    |

## Application rules

- **Primary surfaces** lean on Bitwarden Blue and Deep Blue. Light surfaces use Off White or
  True White; dark surfaces use Deep Blue or True Black.
- **Highlights** use Teal Highlight and Light Teal Highlight, paired with the blues.
- **Greys** (Light Grey, Medium Grey) carry secondary surfaces, dividers, and disabled states.
- **Tertiary palette is restrained.** Two or three tertiary swatches on one screen is usually
  too many. State semantics (success/warning/error) are the right use; decorative use is not.

## Recommended pairings (WCAG AA, body-text scale)

Pairings labeled "AA" hit at least 4.5:1 for normal text. Pairings labeled "AA-large" hit at
least 3:1 — use only for ≥18pt or ≥14pt bold.

| Foreground        | Background        | Status   | Notes                                                      |
| ----------------- | ----------------- | -------- | ---------------------------------------------------------- |
| `--bw-true-black` | `--bw-true-white` | AA       | Default body text on light surfaces.                       |
| `--bw-deep-blue`  | `--bw-true-white` | AA       | Body or heading text on light surfaces.                    |
| `--bw-deep-blue`  | `--bw-off-white`  | AA       | Body text on a slightly softened light surface.            |
| `--bw-blue`       | `--bw-true-white` | AA-large | Headings or CTAs, not body. Body Blue-on-white is too low. |
| `--bw-true-white` | `--bw-deep-blue`  | AA       | Default body text on dark surfaces.                        |
| `--bw-true-white` | `--bw-blue`       | AA-large | Headings or CTAs, not body.                                |
| `--bw-deep-blue`  | `--bw-light-teal` | AA       | Accent panel with readable body.                           |

> The brand site does not publish a contrast matrix. The pairings above are pragmatic — verify
> against the actual size, weight, and rendering of the deliverable using a contrast checker
> (e.g. WebAIM).

## Surface choices (pragmatic — the brand site is silent)

The brand site does not prescribe a surface mode for deliverables. Two safe defaults:

- **Light surface** — use `--bw-off-white` or `--bw-true-white` as the page background,
  `--bw-deep-blue` for text, `--bw-blue` and `--bw-teal` for accents.
- **Dark surface** — derive the page background from `--bw-deep-blue` (use it directly, or
  compose a slightly lighter shade on top via a 10-20% opacity `--bw-true-white` layer). **Do
  not invent a new dark neutral.** Use `--bw-true-white` for body text and `--bw-teal` /
  `--bw-light-teal` for accents.

Whichever surface is chosen, document the decision in the deliverable so a reader knows it is a
deliverable-level call, not brand canon.

## Common off-brand patterns to catch

- **Off-system blues.** Anything that isn't `#175DDC` or `#0C3276` claiming to be "the
  Bitwarden blue."
- **Tertiary green or yellow used as a headline color.** Reserved for state communication.
- **Pure black (`#000000`) on pure white (`#FFFFFF`) at scale** — usable for text, but Off
  White (`#F3F6F9`) is the default light surface; not the sole option but more often correct.
- **Raw hex values in Figma instead of library-bound variables.** Compose
  `Skill(using-figma)` with `get_variable_defs` to confirm library binding before claiming a
  design is on-brand.

## When this reference is outdated

Treat the brand site and brand repo as authoritative. If a color appears in product code but
not on this page, check `brand-colors/palette.scss` in the repo first — that file is the
canonical SCSS source and is what this reference mirrors. Run
`scripts/verify-brand-canon.sh` to compare the bundled tokens against that source at any time;
on drift it prints the correct values to use in the deliverable. Updating this file (and
`assets/bitwarden-tokens.css`) to match is a separate PR.
