# Bitwarden color palette

Source of truth: [`bitwarden.com/brand`](https://bitwarden.com/brand). The HEX/RGB/CMYK values below are lifted from the published palette. Use only these colors. Do not invent shades, tints, or alternate steps.

## Primary

| Name           | HEX       | RGB           | CMYK               |
| -------------- | --------- | ------------- | ------------------ |
| Bitwarden Blue | `#175DDC` | 23 / 93 / 220 | 84 / 66 / 0 / 0    |
| Deep Blue      | `#0C3276` | 12 / 50 / 118 | 100 / 91 / 26 / 12 |

## Accents

| Name       | HEX       | RGB             | CMYK            |
| ---------- | --------- | --------------- | --------------- |
| Teal       | `#2CDDE9` | 44 / 221 / 233  | 58 / 0 / 15 / 0 |
| Light Teal | `#A2F4FD` | 162 / 244 / 253 | 30 / 0 / 5 / 0  |

## Semantic

Per the brand site: _"The tertiary Green, Yellow, and Red should be used sparingly, primarily in product graphics and for success/error communications."_

| Name   | HEX       | RGB             | CMYK             |
| ------ | --------- | --------------- | ---------------- |
| Green  | `#7BF1A8` | 123 / 241 / 168 | 49 / 0 / 30 / 5  |
| Red    | `#FF6550` | 255 / 101 / 80  | 0 / 60 / 69 / 0  |
| Yellow | `#FFD700` | 255 / 215 / 0   | 0 / 16 / 100 / 0 |

> Note on Yellow: the brand site's HEX field renders with a malformed value, but the published RGB (255, 215, 0) unambiguously resolves to `#FFD700`, which is also consistent with the published CMYK. If the brand site is later corrected, follow it.

## Neutrals

| Name        | HEX       | RGB             | CMYK              |
| ----------- | --------- | --------------- | ----------------- |
| True White  | `#FFFFFF` | 255 / 255 / 255 | 0 / 0 / 0 / 0     |
| Off White   | `#F3F6F9` | 243 / 246 / 249 | 3 / 1 / 1 / 0     |
| Light Grey  | `#D8E2EB` | 216 / 226 / 235 | 14 / 6 / 3 / 0    |
| Medium Grey | `#99A7B5` | 153 / 167 / 181 | 42 / 28 / 22 / 0  |
| True Black  | `#000000` | 0 / 0 / 0       | 75 / 68 / 67 / 90 |

## Recommended pairings (WCAG AA, body-text scale)

Pairings labeled "AA" hit at least 4.5:1 for normal text. Pairings labeled "AA-large" hit at least 3:1 — use only for ≥18pt or ≥14pt bold.

| Foreground        | Background        | Status   | Notes                                                      |
| ----------------- | ----------------- | -------- | ---------------------------------------------------------- |
| `--bw-true-black` | `--bw-true-white` | AA       | Default body text on light surfaces.                       |
| `--bw-deep-blue`  | `--bw-true-white` | AA       | Body or heading text on light surfaces.                    |
| `--bw-deep-blue`  | `--bw-off-white`  | AA       | Body text on a slightly softened light surface.            |
| `--bw-blue`       | `--bw-true-white` | AA-large | Headings or CTAs, not body. Body Blue-on-white is too low. |
| `--bw-true-white` | `--bw-deep-blue`  | AA       | Default body text on dark surfaces.                        |
| `--bw-true-white` | `--bw-blue`       | AA-large | Headings or CTAs, not body.                                |
| `--bw-deep-blue`  | `--bw-light-teal` | AA       | Accent panel with readable body.                           |

> The brand site does not publish a contrast matrix. The pairings above are pragmatic — verify against the actual size, weight, and rendering of your deliverable using a contrast checker (e.g. WebAIM).

## Surface choices (pragmatic — the brand site is silent)

The brand site does not prescribe a surface mode for deliverables. Two safe defaults:

- **Light surface** — use `--bw-off-white` or `--bw-true-white` as the page background, `--bw-deep-blue` for text, `--bw-blue` and `--bw-teal` for accents.
- **Dark surface** — derive the page background from `--bw-deep-blue` (use it directly, or compose a slightly lighter shade on top via a 10–20% opacity `--bw-true-white` layer). **Do not invent a new dark neutral.** Use `--bw-true-white` for body text and `--bw-teal` / `--bw-light-teal` for accents.

Whichever you pick, document the choice in the deliverable's own README — it isn't brand canon and shouldn't be presented as such.
