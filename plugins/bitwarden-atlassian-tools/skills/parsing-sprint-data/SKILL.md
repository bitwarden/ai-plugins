---
name: Parsing Sprint Data
description: |
  This skill should be used when the user needs to "extract tickets from Confluence",
  "parse sprint planning page", "get ticket list from Confluence", or requires
  extraction of JIRA ticket identifiers from Confluence sprint planning documentation.
version: 1.0.0
---

# Parsing Sprint Data

## Purpose

Extract JIRA ticket identifiers from Confluence sprint planning pages, handling
various formats and structures commonly used in sprint planning documentation.

## Input Requirements

- **Confluence Page ID**: Numeric identifier for the page
- **Sprint Identifier**: Date range or sprint name to locate correct section

## Confluence Page Structures

### Structure 1: Table Format with Date Headers

```html
<h2>Dec 15-26</h2>
<table>
  <tr><th>Ticket</th><th>Summary</th><th>Status</th></tr>
  <tr><td><a href="...">PM-12345</a></td><td>...</td><td>...</td></tr>
</table>
```

Extraction: Find H2/H3 matching sprint, parse following table for ticket links.

### Structure 2: List Format

```html
<h2>Sprint 42</h2>
<ul>
  <li><a href="...">PM-12345</a> - Summary text</li>
</ul>
```

Extraction: Find heading, extract links from list items.

### Structure 3: Embedded JIRA Macros

```html
<ac:structured-macro ac:name="jira">
  <ac:parameter ac:name="key">PM-12345</ac:parameter>
</ac:structured-macro>
```

Extraction: Parse JIRA macro parameters for ticket keys.

## Parsing Algorithm

1. Fetch Confluence page content (storage format)
2. Locate section matching sprint identifier:
   - Search for H2/H3 elements containing sprint name/dates
   - Handle variations: "Dec 15-26", "December 15-26", "12/15-12/26"
3. Extract ticket keys from section:
   - Pattern match: /[A-Z]+-\d+/ (e.g., PM-12345, MOBILE-678)
   - Parse href attributes for JIRA links
   - Extract from JIRA macros
4. Deduplicate ticket keys
5. Return structured list with metadata

## Output Format

```json
{
  "source": {
    "type": "confluence",
    "pageId": "2270330935",
    "pageTitle": "Sprint Planning 2024"
  },
  "sprint": {
    "identifier": "Dec 15-26",
    "matchedSection": "Sprint: December 15-26, 2024"
  },
  "tickets": [
    {
      "key": "PM-12345",
      "extractedFrom": "table_cell",
      "rawText": "PM-12345 - Authentication refactoring"
    }
  ],
  "metadata": {
    "totalExtracted": 42,
    "extractionTimestamp": "2024-12-20T10:30:00Z"
  }
}
```

## Error Handling

- **Page Not Found**: Return error with suggestion to verify page ID
- **Sprint Section Not Found**: Return all tickets from page with warning
- **No Tickets Found**: Return empty list with parsing details for debugging
- **Malformed Content**: Best-effort extraction with warnings
