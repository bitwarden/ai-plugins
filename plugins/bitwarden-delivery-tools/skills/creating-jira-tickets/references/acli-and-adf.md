# acli create + ADF reference

Mechanics for Steps 3–5. All commands run against `bitwarden.atlassian.net` as the authenticated user.

`--key` is a `link ...` flag only. `workitem view` and `workitem create` take the key positionally: `acli jira workitem view PM-XXXX --fields "summary,issuetype" --json`.

## Create command

Core fields go through flags; the description goes through an ADF file:

Keys and names below are placeholders — substitute the breakdown's real epic key. Bitwarden files into the `PM` project.

```bash
acli jira workitem create \
  --project PM \
  --type Story \
  --parent PM-XXXX \
  --summary "Add CSV export to the item list (web)" \
  --label "team-label,area-label" \
  --description-file ./ticket-adf.json
```

- `--type` — `Epic`, `Story`, `Task`, or `Bug`.
- `--parent` — the epic key for a child story/task.
- `--label` — comma-separated, no spaces.
- **Team / Capability Driver / Initiative Owner auto-default from the project** (for Bitwarden's `PM` project) — do not pass them.
- **Priority is not a create flag** (defaults to Medium). Set it afterward with `acli jira workitem edit` only if the task calls for it.
- Add `--json` to capture the returned key programmatically.

## ADF description shape

`--description-file` takes an Atlassian Document Format JSON document: a summary paragraph, then a level-2 `Acceptance criteria` heading, then a `codeBlock` holding the Gherkin.

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "Add a CSV export option to the item list so users can download their items. "
        },
        {
          "type": "text",
          "text": "libs/exporter is owned by another team and needs their review."
        }
      ]
    },
    {
      "type": "heading",
      "attrs": { "level": 2 },
      "content": [{ "type": "text", "text": "Acceptance criteria" }]
    },
    {
      "type": "codeBlock",
      "attrs": { "language": "gherkin" },
      "content": [
        {
          "type": "text",
          "text": "Scenario: User exports the item list as CSV\n  Given a user viewing the item list\n  When they choose Export and select CSV\n  Then a CSV file of the listed items downloads\n  And the file preserves the list's current column order"
        }
      ]
    }
  ]
}
```

### Linking a ticket reference in prose

To make a ticket key clickable in an ADF paragraph, apply a `link` mark to the text node:

```json
{
  "type": "text",
  "text": "PM-XXXX",
  "marks": [
    {
      "type": "link",
      "attrs": { "href": "https://bitwarden.atlassian.net/browse/PM-XXXX" }
    }
  ]
}
```

A key inside the Gherkin `codeBlock` cannot carry a link mark — that is fine; leave it as plain text.

## Linking dependencies

Map dependencies to link types:

- Hard dependency (must land first) → **Blocks**
- Soft / ordering-only dependency → **Relates**

**The direction is inverted from acli's own success message.** Verified against the Jira UI: to make **X block Y**, run with the blocker on `--in`:

```bash
# Make PM-YYYY (the blocker) block PM-ZZZZ:
acli jira workitem link create --out PM-ZZZZ --in PM-YYYY --type Blocks --yes
```

acli then prints a reversed confirmation like `PM-ZZZZ Blocks PM-YYYY` — ignore the message and verify instead.

### Reading a link back

```bash
acli jira workitem link list --key PM-YYYY --json
```

Payload — top-level `issueLinks`, type is `typeName`:

```json
{
  "issueLinks": [
    { "id": "84678", "outwardIssueKey": "PM-ZZZZ", "typeName": "Blocks" },
    { "id": "84680", "outwardIssueKey": null, "typeName": "Relates" }
  ]
}
```

`outwardIssueKey` non-null = the queried issue is the blocker/outward side (here `PM-YYYY blocks PM-ZZZZ`); `null` = the queried issue is the blocked/inward side. Confirm against the UI panel headings (`blocks` vs `is blocked by`) when in doubt.

Available link types: `acli jira workitem link type`.
