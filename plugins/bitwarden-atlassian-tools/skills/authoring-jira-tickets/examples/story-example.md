# Story Example — Add CSV Export to Report List

This is a complete example output `.md` file for a Story ticket. It demonstrates the format and writing style expected by the skill.

---

## Filename

`story-add-csv-export-to-report-list.md`

---

## Output

````markdown
# Add CSV Export to the Report List (web)

**Type:** Story
**Links:** [AA-XXXX](https://compy.atlassian.net/browse/AA-XXXX) — Blocks · [AA-2105](https://compy.atlassian.net/browse/AA-2105) — Relates to · [AA-2108](https://compy.atlassian.net/browse/AA-2108) — Relates to

---

**DESCRIPTION**

**User Story:** As an admin user, I want to export report data as a CSV file so that I can use the data in other tools.

This ticket adds a CSV export option to the report list action menu in the web app. When selected, the export downloads a file containing all visible fields for the reports currently in view. It does not cover encrypted exports or folder-scoped exports — those are separate tickets.

**Feature Flag:** `report-csv-export`
**Design:** [CSV Export Designs](https://figma.com/file/abc123/report-csv-export)
**Tech Breakdown:** [CSV Export Tech Breakdown](LINK TO BE PROVIDED)

---

**ACCEPTANCE CRITERIA**

- An Export option appears in the report list action menu for users with the report-csv-export feature flag enabled
- Selecting Export > CSV initiates a file download
- The downloaded file contains all fields visible in the current report list view
- If the report list is empty, the Export option is disabled

**Out of Scope:**

- Encrypted export format
- Folder-scoped export

---

**SCENARIOS**

```gherkin
Scenario: Admin exports a non-empty report list as CSV
  Given the admin has reports in the system
  And the report-csv-export feature flag is enabled
  When the admin opens the report list action menu and selects Export > CSV
  Then a CSV file downloads containing all visible fields for those reports

Scenario: Export option is disabled when the report list is empty
  Given the admin has no reports in the system
  And the report-csv-export feature flag is enabled
  When the admin views the report list action menu
  Then the Export > CSV option is visible but disabled

Scenario: Export option is hidden when the feature flag is off
  Given the report-csv-export feature flag is disabled
  When the admin views the report list action menu
  Then no Export option appears in the menu
` `` `

---

**QA TESTING NOTES**

- Test with a dataset containing more than 500 reports to verify the export completes without timeout
- Test with reports that have special characters in field values (commas, quotes, newlines)

---

**TECHNICAL BREAKDOWN**

The export serializes the current report list view state — not the full dataset — so it respects active filters and search terms. The CSV column order should match the visible column order in the list. The file should be streamed rather than buffered in memory to avoid issues with large datasets.

The relevant list component and its data source are in [apps/web/src/app/reports](https://github.com/example/app/tree/main/apps/web/src/app/reports). The download mechanism should follow the existing pattern used for JSON export.

---

**RISKS / CONSIDERATIONS**

- Large datasets (10k+ items) may cause the browser to hang if the export is not streamed — streaming is required
- CSV format does not support encrypted fields; this ticket exports only decrypted, visible fields

---

**QUESTIONS AND ANSWERS**

[STATUS: Resolved: Yes] **Should the export respect the current search/filter state, or always export the full dataset?**
> Export respects the current view state (filters and search terms applied). Full-dataset export is a separate use case.
```
````

---

## Annotation

**What this example shows:**

- Title uses imperative verb + outcome + area, with client in parentheses
- Purpose paragraph names what the ticket covers and explicitly calls out what it does not (linked tickets handle the rest — no need to name them in Purpose)
- Feature flag uses the LaunchDarkly value (`report-csv-export`), not a code enum name
- Acceptance Criteria: observable changes only, no function names or file paths
- Out of Scope in Acceptance Criteria names what a reader could reasonably assume is included — no "covered by" ticket references; those sibling tickets appear in Links metadata as "Relates to"
- Scenarios: three cases — happy path, empty state, flag off; each tests one behavior
- QA Testing Notes adds two things the scenarios don't cover (volume, special characters)
- Technical Breakdown captures intent (stream vs. buffer, follow existing download pattern) and links to the relevant directory — not a step-by-step implementation guide
- Risks / Considerations names one real risk with a stated mitigation requirement
- Questions and Answers captures a resolved product decision so it's on record
- No code identifiers (class names, method names) outside Technical Breakdown
