# Writing for Accessibility and Inclusivity

These rules are first-class — apply alongside grammar and mechanics whenever copy is being
reviewed or written. Bitwarden's users include people using assistive technology, non-native
English speakers, and people with cognitive differences. Copy that ignores them is incomplete.

## Write simply and directly

Target a **U.S. 7th-grade reading level**. Short sentences and paragraphs. Active voice. Simple
verb tenses. Avoid adverbs and adjectives.

- Good: Delete file
- Avoid: Would you like to delete this file?

Exception: in UI where the verb focus should be the object — e.g., "The file was saved."

## Create scannable layouts

Follow header hierarchy (H1, H2, H3, H4) — don't skip levels. Assistive tech relies on this. If
a level is skipped, users assume they missed a section.

- Good: `[H2] File types` → `[H3] Images`
- Avoid: `[H2] File types` → `[H4] Images`

Paragraph text 16 pt or larger. Line height 1.5×. Space after paragraphs 2× the font size. Use
bulleted/numbered lists where appropriate.

## Consider non-English and ESL speakers

Avoid idioms, phrases, and emojis that don't translate well. Treat them as decorative —
acceptable for zest, but not load-bearing for meaning.

- Good: Nice job
- Avoid: Hats off to you

## Spell out acronyms

Never assume the reader knows the acronym. Spell out at first reference per page, with the
acronym in parentheses. Then use only the acronym.

## Don't imply tasks are easy or simple

Tasks aren't equally easy for everyone — assistive tech, cognitive ability, and environment all
affect speed. Give helpful information instead.

- Good: Follow these three steps.
- Avoid: Follow these fast, easy steps.

## Use text styling sparingly

Italics, bold, and ALL CAPS are harder to read. Screen readers don't always identify font
styles. Don't apply to full paragraphs.

Always **left-align paragraph text**. Justified and center-aligned text is harder for people
with dyslexia.

## Avoid spatial language

Use time-based ("next", "before") or element-based ("in the dropdown") directions, not spatial
("above", "below", "on the left"). Spatial directions confuse screen reader users.

- Good: In the global menu
- Avoid: In the top left corner of the screen

## Focus on critical info in alt text

If a visual conveys information, describe it in alt text, caption, or paragraph text. Keep alt
text under 125 characters where possible. Don't write "image of" — repetitive with screen
readers.

If the visual isn't critical:

- Write short alt text so users know what's there but can move on, OR
- Leave alt blank and add `aria-hidden="true"` so screen readers skip it.

- Good: search results for airplanes
- Avoid: image of search results for the keyword phrase "airplanes" which includes 63 images
  and PDF documents and the download button circled

## Write meaningful link text

Link text should tell the user what they're clicking or where they'll go. Don't write "Click
here." Screen reader users may jump from link to link.

- Good: Read this article about integrations.
- Avoid: Click here to learn more about integrations.

Don't add a separate "Learn more" sentence — usually repetitive.

- Good: Turn on the new vault feature.
- Avoid: The new vault feature is now available. Learn more about the feature and how to turn
  it on.

Always underline link text so colorblind users can see it.

## Stay gender neutral

Use **they** or **you** instead of gendered pronouns like he/she.
