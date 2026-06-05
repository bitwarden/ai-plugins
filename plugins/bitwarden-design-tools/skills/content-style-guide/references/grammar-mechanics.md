# Grammar and Mechanics

Default to **Associated Press style**, with the exceptions noted below.

## Acronyms

In body text, spell out acronyms at first reference, then add the acronym in parentheses
immediately after. On second and subsequent references, use only the acronym.

In UI, it's ok to use the acronyms **SSO** and **SAML** on first reference, but **not IdP**.

## Ampersands

Avoid ampersands. Spell out **and** in all references — including headings and button text.

## Capitalization

Use **sentence case** for most text on the page, including headers, button text, table headings,
modal headings, etc. (Marketing materials use title case for button text — but product UI does
not.)

**Product names and plans — capitalize:**

- Secrets Manager
- Password Manager
- Enterprise
- Teams
- Families

**Features — default to lowercase unless there's a good reason.**

Generally, don't name and capitalize features. One named feature isn't a big deal, but when
everything in software gets named, the information architecture becomes inconsistent and the
user has to learn and remember what things are called. Call features what they are. Example:
prefer "shared folders" over "Collections".

Currently capitalized features (mixed state — will evolve):

- Send
- Access Intelligence
- Objects

**Lowercase objects — these are not proper nouns:**

- secrets, passwords, items, vault, favorites, folders, extension, organization, policy

**Bitwarden teams — lowercase:**

- "support team", "Bitwarden sales team"

## Dates and months

For emails, blog posts, or anywhere with white space, use: **September 19, 2025**.

- Capitalize and spell out each month.
- Include a comma after the date.
- Include the year.
- Do NOT include `st`, `nd`, `rd`, or `th` after the date.
- Avoid all-numeric dates (e.g., 1/13/20) — confusing for ESL readers and translation.

Abbreviate the month only when spacing is an issue (mostly product UI). No periods:

- Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sept, Oct, Nov, Dec

## Days of the week

Spell out each day. If space is limited, use **Mon, Tue, Wed, Thu, Fri, Sat, Sun** (no periods).

## E.g. and i.e.

- **e.g.** = for example; cite a few examples.
- **i.e.** = that is / in other words; further explain.
- Both are followed by a comma.

For translation, prefer "for example" and "this means" over the Latin abbreviations.

## Ellipsis

Use mainly to indicate deletion of text. Also use in loading spinners to indicate users are
waiting a few seconds for something to load. **No spaces** before or after.

## File sizes and formats

Capitalize file sizes and formats; don't spell them out: **GB, MB, ZIP, PDF, JPG, HTML, PNG, GIF,
CSV, EXIF**. Lowercase only inside a filename (e.g., `cat.jpg`).

## Money

For USD, include the dollar sign and amount. Only include cents when non-zero:

- Good: $3 or $3.99
- Avoid: $3.00

**Exception:** Checkout UI totals always show cents, even when zero.

## Numbers

Numerals are ok for numbers under 10, especially in components with little space. With plenty
of space, spell out one through nine. For numbers over **1,000**, always include a comma.

## Oxford comma

**Use it.** Adds clarity, especially in longer sentences. (Exception to AP style.) If a
sentence has many commas, consider simplifying.

## Times and time zones

Bitwarden products determine time zone and time based on user location — but not date format.

Format: **9 PM**. Include a colon and minutes only if not `:00`. Don't include seconds.
Capitalize AM/PM with no periods. (Exception to AP style.)

Default time zone: **EDT (Eastern Daylight Time)**.

## Versus

Write as the full word **versus** or **vs.** (with a period).
