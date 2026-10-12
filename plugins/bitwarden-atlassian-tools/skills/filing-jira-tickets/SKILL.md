---
name: filing-jira-tickets
description: File Jira work items that stand on their own, with real ticket titles, acceptance criteria in whatever field the target project provides, and verified dependency links. Reads the target project's create screen first, so no project's field layout is assumed.
when_to_use: Use when the user is ready to create one or more Jira work items and wants them filed correctly. Phrasings like "file a bug for this", "create a story for this work", "open a spike", "file these tickets", "link these two tickets", or "wire the blocked-by relationship". Also use when another skill hands off a set of drafted tickets to create. Do not use for reading or researching existing issues (that is researching-jira-issues), or for editing tickets that already exist.
allowed-tools: Read, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_create_fields
---

# Filing Jira Tickets

Tickets get read outside the context that produced them, so each one has to stand alone.

Live tickets are awkward to unwind, so `create_issue` and `link_issues` both default to a dry run that returns the exact payload without sending it. Preview before every live write. A live write takes an explicit `dryRun: false`.

Nothing gets created without approval unless you are explicitly told to skip it. See Step 3.

## Step 1: Read the target project's create screen

Bitwarden files into many projects and they do not share a shape. PM and SM expose an Acceptance criteria field; QA, VULN, and PLT do not. VULN has no Story type. PLT's only creatable type is `Platform Initiative`. Never assume a field id, a required field, or that an issue type exists.

Call `get_create_fields` with the project key, and again with the intended issue type. It returns the project's creatable types, then every field on that type's create screen with its id, whether it is required, and its allowed values.

- The type is not in the list: pick from what the project offers, or ask the user which one they want.
- The tool reports it cannot read the create screen (a 404): this means the project key does not exist, or the user lacks create permission there — the tool cannot tell which. Re-check the project key for a typo before concluding the latter; if it's correct, tell the user they likely lack create permission and stop. Do not guess at a different project.

**Completion criterion:** for the target project and issue type, a list of the required fields and the ids of any optional fields this work should populate.

## Step 2: Draft the ticket

Translate the work into fields. Do not paste in whatever the source document said.

- **Title.** Imperative verb, outcome, and area: `Add CSV export to the item list (web)`. Match the style of sibling tickets under the same parent, and check one if you are unsure.
- **Description.** One short paragraph of the actual work, plus any caveat specific to this ticket. No lineage boilerplate such as `Part of PM-1234`, and no path to a source document; the parent link already conveys that. Spell out shorthand rather than using symbols.
- **Acceptance criteria.** If Step 1 showed the project has a criteria field, pass the criteria there through `fields`, keyed by that field's id, as a single string of Gherkin (`Scenario`, `Given`, `When`, `Then`, `And`) — that field is plain text, so embedded line breaks render fine. If the project has no such field, put the criteria in the description instead: pass each Gherkin line as its own `descriptionParagraphs` entry, since each entry becomes one paragraph and a paragraph has no line-break node of its own. Tell the user that is what you did. Do not invent a field id.
- **Required fields.** Supply every one Step 1 reported. Where a value is a business judgement rather than something derivable from the work, ask the user and offer the allowed values Step 1 returned. Do not guess, and do not pick the first option.
- **Labels.** Only what the user asked for.

**Completion criterion:** a drafted payload per ticket that satisfies every required field Step 1 reported.

## Step 3: Preview, approve, create

For each ticket, in the order given:

1. Dry-run it.
2. Verify the tool's raw output against Step 1: every required field present, criteria in the field Step 1 identified (or in the description if the project has none), parent correct, title makes sense to someone who has not read the source material.
3. Show the user a plain-language preview: title, full description text, full acceptance criteria, parent, labels.
4. Get approval on that preview. Then create it with `dryRun: false` and record the returned key.

**Approval before every create is the default.** Skip it only when explicitly told to file without approval.

If a create fails naming a field, re-read Step 1 for that project instead of guessing at the fix.

**Completion criterion:** every requested ticket previewed, approved, and created, with each returned key recorded.

## Step 4: Wire dependency links

Linking is reversible, so this step can run as a batch once the tickets exist.

- A hard dependency, where one item must land before another can start, is `Blocks`. Soft or ordering-only is `Relates`.
- For `Blocks`, pass `blockerKey` for the item that must land first and `blockedKey` for the item waiting on it. The tool maps those onto Jira's inward and outward sides internally, so the direction cannot be inverted by getting the argument order wrong.
- `link_issues` reads the link back itself and reports whether it verified. If it reports it could not verify, tell the user and point them at Jira's Linked Issues panel directly — `get_issue`'s output has no links section, so it cannot confirm this for you.

**Completion criterion:** every relationship whose target ticket exists is created and verified. Relationships pointing at work that does not exist yet are reported back to the user, not dropped.
