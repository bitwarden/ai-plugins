---
name: content-style-guide
description: Bitwarden's product content style guide for end-user-facing GUI copy — voice, tone, AP-style-with-exceptions grammar, sentence case in UI, and accessibility-first language at a U.S. 7th-grade reading level.
when_to_use: Use when end-user-facing GUI strings are being authored or critiqued — button labels, error messages, toasts, modal copy, onboarding, empty states, form labels, helper text, link text. Triggers — "review this copy", "is this error message ok", "rewrite this button label", "check the wording", "what should this say". Composed by `design-review` at 60%/90% stages and by `figma-to-angular` (external, not bundled) during code generation. Not for developer-facing strings, code comments, design tokens, or marketing/long-form content.
allowed-tools: Skill
---

# Product Content Style Guide

This skill grounds GUI copy decisions in Bitwarden's product content style guide. Apply it to
end-user-facing strings only — button labels, error messages, toasts, modals, onboarding flows,
empty states, form labels, helper text, link text, and similar. Do not apply to design tokens,
code comments, internal/dev-facing strings, or marketing copy.

When in doubt about a specific case, ask before changing copy.

## Voice and tone

**Voice is constant. Tone flexes with context.**

Product voice is **approachable, encouraging, and transparent** — consistent across platforms.

Tone conveys mood and depends on who you're talking to and what's happening. Security is serious
stuff. Users aren't looking for humor or fluff — they want to know their information is safe. So
Bitwarden's product tone is **almost always serious and respectful**.

Tone spectrums:

- Casual ↔ formal
- Enthusiastic ↔ matter-of-fact

Where common content types land on the tone map (axes: casual ↔ formal × matter-of-fact ↔ enthusiastic):

| Content type     | Casual / Formal   | Matter-of-fact / Enthusiastic |
| ---------------- | ----------------- | ----------------------------- |
| Success messages | Casual            | Enthusiastic                  |
| Onboarding copy  | Casual            | Enthusiastic                  |
| Dialogs          | Casual            | Matter-of-fact                |
| Empty states     | Casual            | Matter-of-fact (slightly)     |
| Labels           | Neutral           | Matter-of-fact                |
| Community        | Formal            | Enthusiastic                  |
| Confirmations    | Formal            | Matter-of-fact                |
| Help articles    | Formal (slightly) | Neutral                       |
| Warnings         | Formal            | Matter-of-fact                |
| Error states     | Formal            | Matter-of-fact                |

### Examples

**Error message — formal, matter-of-fact:**

- Good: An error occurred. Please try again.
- Avoid: Uh oh! We goofed. Go ahead and refresh!

**Onboarding message — casual, enthusiastic:**

- Good: Hey there! 👋 Welcome to Bitwarden. We'll show you around!
- Avoid: This is your vault. Get started now.

## Applying this skill

**During explicit copy critique** ("review this copy", "is this error message ok"):

1. Identify the content type (error, onboarding, button, etc.) and the expected tone using the
   tone map above.
2. Check voice consistency (approachable, encouraging, transparent).
3. Walk grammar and mechanics rules relevant to the snippet — see
   `references/grammar-mechanics.md`.
4. Walk accessibility rules relevant to the snippet — see `references/accessibility-rules.md`.
5. Return specific, actionable rewrites — not just "this is wrong."

**Inside `figma-to-angular` runs** (external skill in the clients repo, not bundled here):

When the Figma design includes copy strings, validate them against this guide before emitting
them into the Angular template. If a string clearly violates a rule (e.g., title-case button,
ampersand, "Click here" link), surface the issue and propose a compliant alternative — do not
silently rewrite. Ask the user which to use.

**Inside design-review critiques:**

If the stage is 60% or 90%, include content observations alongside visual feedback (90% is the
right stage for "nitty-gritty grammar, finalizing copy"). Skip content nitpicks at 30% — the
copy will change. Frame content feedback the same way as visual feedback: tied to user/product
goals, not personal taste.

## Output format for copy critique

1. **Content type and expected tone** — name what this string is and where it should land on
   the tone spectrum.
2. **What's working** — what to keep.
3. **Issues** — each tied to a specific rule from this guide (cite the section name, including
   the references file if the rule lives there).
4. **Proposed rewrite(s)** — concrete alternatives the user can pick from.

Keep critique specific. "The button uses title case; sentence case per
`references/grammar-mechanics.md` (Capitalization)" beats "the capitalization is off."

## Additional resources

The detailed rules live in two references files. Load them when the critique needs them — most
copy issues touch only one or two rules.

- **`references/grammar-mechanics.md`** — Acronyms, ampersands, capitalization (sentence case,
  product names, features, lowercase objects), dates and months, days of the week, e.g. / i.e.,
  ellipsis, file sizes and formats, money, numbers, Oxford comma, times and time zones, versus.
- **`references/accessibility-rules.md`** — Reading level and directness, scannable layouts,
  non-English and ESL considerations, spelling out acronyms, avoiding "easy" and "simple"
  framings, text styling, spatial language, alt text, meaningful link text, gender-neutral
  pronouns.
