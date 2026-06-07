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
| Tertiary Yellow | 0, 16, 100, 0   |
| Tertiary Red    | 0, 60, 69, 0    |

## Application rules

- **Primary surfaces** lean on Bitwarden Blue and Deep Blue. Light surfaces use Off White or
  True White; dark surfaces use Deep Blue or True Black.
- **Highlights** use Teal Highlight and Light Teal Highlight, paired with the blues.
- **Greys** (Light Grey, Medium Grey) carry secondary surfaces, dividers, and disabled states.
- **Tertiary palette is restrained.** Two or three tertiary swatches on one screen is usually
  too many. State semantics (success/warning/error) are the right use; decorative use is not.

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
canonical SCSS source and is what this reference mirrors. If the palette has drifted, update
this file in a separate PR.
