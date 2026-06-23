# Logo usage

Source of truth: [`bitwarden.com/brand`](https://bitwarden.com/brand). Lockup choice, clear-space rules, and the official SVG come from there.

## Lockups

- **Horizontal lockup — primary.** Per the brand site: _"The primary and preferred composition will be the horizontal lockup."_ Use this unless the available space makes it impossible.
- **Vertical lockup — secondary.** Use only when horizontal won't fit — e.g. narrow sidebars, vertical banners.
- **Product-specific lockups.** Bitwarden products have their own lockups for in-product UI and comparative diagrams. Use these when the artifact is specifically about a single product (e.g. Password Manager, Secrets Manager). These lockups are NOT bundled with this plugin — fetch them from `bitwarden.com/brand`.

## Color variants

The brand site ships two color variants of every lockup:

- **Brand blue (`#175DDC`)** — for use on light surfaces.
- **White (`#FFFFFF`)** — for use on dark surfaces.

Switching between blue and white on the appropriate surface is **not** a recolor. Both ship in the official lockup file. Using blue on a dark surface, or recoloring to any other shade, is.

## Clear space

- **Horizontal logo** — at minimum, leave one shield-width of clear space on every side. Nothing — text, icons, illustration, edge of canvas — encroaches inside that margin.
- **Vertical logo** — at minimum, leave one X-height (the height of the lowercase "x" in the "Bitwarden" wordmark) of clear space on every side.

## Bundled assets

This plugin ships the canonical paths extracted verbatim from the official lockup SVG. Use whichever variant fits the deliverable.

| File                                           | What it is                                                                                                                      | Use on                                                           |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `assets/bitwarden-lockup-official.svg`         | The full official lockup file, verbatim from the brand site. Contains every variant at every scale, both colors, on one canvas. | Reference. Use when you need the canonical source file directly. |
| `assets/bitwarden-lockup-horizontal-blue.svg`  | Primary horizontal lockup (shield + wordmark)                                                                                   | Light surface                                                    |
| `assets/bitwarden-lockup-horizontal-white.svg` | Primary horizontal lockup (shield + wordmark)                                                                                   | Dark surface                                                     |
| `assets/bitwarden-lockup-vertical-blue.svg`    | Secondary vertical lockup (shield above wordmark)                                                                               | Light surface                                                    |
| `assets/bitwarden-lockup-vertical-white.svg`   | Secondary vertical lockup (shield above wordmark)                                                                               | Dark surface                                                     |
| `assets/bitwarden-shield-blue.svg`             | Shield only                                                                                                                     | Light surface                                                    |
| `assets/bitwarden-shield-white.svg`            | Shield only                                                                                                                     | Dark surface                                                     |
| `assets/bitwarden-wordmark-blue.svg`           | Wordmark only                                                                                                                   | Light surface                                                    |
| `assets/bitwarden-wordmark-white.svg`          | Wordmark only                                                                                                                   | Dark surface                                                     |

Every derived asset preserves the original path data and coordinate system from the official lockup; only the surrounding `<svg>` wrapper and the `viewBox` crop are local. The shield is the same path at every size — scale it via the consuming page's CSS rather than swapping to a different shield variant.

### When to use which

- **Default to a full lockup** (horizontal preferred, vertical only when horizontal doesn't fit).
- **Use the shield alone** for small chip-scale uses where a full lockup would be illegible — e.g. a 32px header chip, a favicon-adjacent context.
- **Use the wordmark alone** only when the shield is already established elsewhere on the same deliverable (e.g. a long-form document where the header carries the shield and a footer carries the wordmark). The brand site does not prescribe a wordmark-only lockup; this is a pragmatic affordance.

### Tinting from a single asset

If you want a single shield/wordmark asset to flow with the deliverable's surface (light or dark) via CSS, swap the SVG's `fill="#175DDC"` for `fill="currentColor"` in your local copy and set the surrounding element's `color` property. Switching between blue and white this way is canonical; setting `color` to any other value is a recolor and not permitted.

## Do-not list

- **Don't recolor** to anything other than the published blue or white.
- **Don't outline** the logo or wordmark.
- **Don't compress or stretch.** Preserve the aspect ratio.
- **Don't place on busy backgrounds** without a solid panel underneath. The shield must read cleanly.
- **Don't recreate from scratch** when the official SVG is available — your trace will not match the canonical outlines.
- **Don't rotate** or apply effects (drop shadow, glow, gradient overlay).

## Non-bundled assets and source

This plugin bundles the lockups, shield, and wordmark above. For anything else, the canonical source is the [bitwarden/brand](https://github.com/bitwarden/brand) repository (raw URLs: `https://github.com/bitwarden/brand/raw/main/<path>`) or [bitwarden.com/brand](https://bitwarden.com/brand):

- **Product-specific lockups** (Password Manager, Secrets Manager, etc.) — for in-product UI and comparative diagrams; not bundled.
- **Product icon, PNG** — rounded `/icons/<size>x<size>.png` and square `/icons/square-<size>x<size>.png` at 16, 32, 64, 128, 256 px. The bare shield mark is at `/shield/`; the vector shield is `/logos/icon.svg` (`/logos/icon-inverse.svg` for dark contexts).

For a missing size, request it on the brand repo rather than scaling a PNG (rounded corners and shield proportions do not scale cleanly). For a missing color variant, do not generate one. Blue and inverse-white are the only sanctioned variants, so surface the gap to the brand owners.

The bundled lockups were extracted verbatim from the official source file:

```
https://images.ctfassets.net/7rncvj1f8mw7/6RNJEeiUeUvaJFcUXV5R49/e73a356cad20bce2336afcff8829485b/BitwardenLogo.svg
```

## Trademark

"Bitwarden" is a registered trademark of Bitwarden Inc. Apply the ® mark or trademark attribution per the destination surface's standards (typically the first reference per page in external-facing content; not required in product UI).
