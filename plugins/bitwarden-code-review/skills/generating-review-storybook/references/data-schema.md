# Storybook Config Schema

The `scaffold.py` script consumes a single JSON config file. This document is the source of truth for that shape.

## Top-Level Object

| Field               | Type   | Required | Default                          | Notes                                                                                       |
| ------------------- | ------ | -------- | -------------------------------- | ------------------------------------------------------------------------------------------- |
| `title`             | string | no       | `"Stack review"`                 | Cover headline + default `doc_title` and `brand_meta` source.                               |
| `doc_title`         | string | no       | falls back to `title`            | The HTML `<title>` (browser tab text).                                                      |
| `brand_meta`        | string | no       | falls back to `title`            | Topbar text after the Bitwarden lockup divider.                                             |
| `summary`           | string | no       | auto-generated stack blurb       | Cover lead paragraph (2–3 sentences works best).                                            |
| `slug`              | string | no       | slugified `title`                | Used in the default output directory name.                                                  |
| `storage_prefix`    | string | no       | `"review-storybook-v1"`          | Prefix for all `localStorage` keys. Must be unique per stack to avoid cross-stack bleeding. |
| `gh_repo`           | string | no       | `"bitwarden/server"`             | `owner/name`. Drives the `ghPrUrl()` helper inside `app.js`.                                |
| `estimated_minutes` | number | no       | derived from total lines + count | Reviewer ETA shown on the cover.                                                            |
| `stack`             | array  | **yes**  | —                                | Per-PR / per-commit pages. See below.                                                       |
| `merge_plan`        | array  | no       | derived from `stack`             | Ordered merge steps. See below.                                                             |

## `stack[]` Item

| Field           | Type   | Required | Default                | Notes                                                                                                                                                  |
| --------------- | ------ | -------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `key`           | string | **yes**  | —                      | PR number (e.g. `"2573"`) or short commit SHA. Stringified.                                                                                            |
| `kind`          | enum   | no       | `"pr"`                 | `"pr"` or `"commit"`. Drives the cover label (`PR 2573` vs `commit a1b2c3`).                                                                           |
| `title`         | string | no       | falls back to `key`    | Short human label.                                                                                                                                     |
| `ticket`        | string | no       | `""`                   | Jira key, e.g. `"PM-32809"`. Renders next to the title; empty omits.                                                                                   |
| `description`   | string | no       | `""`                   | One-paragraph PR/commit summary used in the merge plan default.                                                                                        |
| `verdict`       | enum   | no       | `"pending"`            | One of `approve` / `approve-fix` / `block` / `pending`. See verdict notes below.                                                                       |
| `verdict_label` | string | no       | derived from `verdict` | Override the badge text (rarely needed).                                                                                                               |
| `findings`      | object | no       | all zero               | `{ critical, important, debt, suggested, question }` — integers.                                                                                       |
| `files_changed` | number | no       | `0`                    | Cover stats + cards.                                                                                                                                   |
| `lines_changed` | number | no       | `0`                    | Cover stats + cards.                                                                                                                                   |
| `diff_b64`      | string | no       | `""`                   | Base64-encoded unified diff text. Produced by `scripts/capture_diffs.py`.                                                                              |
| `diff_path`     | string | no       | `""`                   | Read a diff from disk and base64-encode it inline. Use **either** `diff_b64` OR `diff_path`.                                                           |
| `comments`      | array  | no       | `[]`                   | Human reviewer comments — render as marginalia alongside findings. See below.                                                                          |
| `chapters`      | array  | no       | `[]`                   | Ordered walkthrough groupings. Files declared here render under chapter headings; anything unlisted falls into a final "Other files" group. See below. |

### Verdict Values

| Value         | Meaning                                                                | Cover badge           |
| ------------- | ---------------------------------------------------------------------- | --------------------- |
| `approve`     | Reviewer signed off. No critical/important findings.                   | Green "Approved"      |
| `approve-fix` | Approve, but follow-up findings exist (typically debt or suggestions). | Amber "Approve+"      |
| `block`       | Blocked — change requested, do not merge.                              | Red "Blocked"         |
| `pending`     | Review not yet performed.                                              | Grey "Pending review" |

`scripts/parse_review_md.py` derives these from a Bitwarden code-review summary:

- "Overall Assessment: APPROVE" + no critical/important findings → `approve`
- "Overall Assessment: APPROVE" + ❌ or ⚠️ finding → `approve-fix`
- "Overall Assessment: REQUEST CHANGES" → `block`
- No "Overall Assessment" line → `pending`

### `findings` Object

Counts by severity (vocabulary matches the bitwarden-code-review classifier) plus
an optional `items[]` array of per-finding details:

```json
{
  "critical": 1,
  "important": 1,
  "debt": 0,
  "suggested": 0,
  "question": 1,
  "items": [
    {
      "severity": "critical",
      "message": "SQL injection in user query builder",
      "location": "src/auth/queries.ts:87",
      "suggestion": "Use the parameterized query helper in `db/safe.ts`."
    },
    {
      "severity": "important",
      "message": "Missing null check on optional config",
      "location": "src/config/loader.ts:23",
      "suggestion": ""
    },
    {
      "severity": "question",
      "message": "Should this be behind a feature flag?",
      "location": "",
      "suggestion": ""
    }
  ]
}
```

Counts populate the cover rollup, the verdict card's findings grid, and the
pagination dot indicators. The `items[]` list — when present — drives the per-PR
**Findings** section, sorted by severity (critical → important → debt → suggested →
question). `parse_review_md.py` produces both pieces from a Bitwarden review summary.

Each item:

| Field        | Type   | Required | Notes                                                                       |
| ------------ | ------ | -------- | --------------------------------------------------------------------------- |
| `severity`   | enum   | yes      | One of `critical` / `important` / `debt` / `suggested` / `question`.        |
| `message`    | string | yes      | The one-line description (text after the severity emoji in the review).     |
| `location`   | string | no       | `path/to/file.ext:lineno` — surfaced as a `mono` code chip on the card.     |
| `suggestion` | string | no       | Free-form follow-up text (anything in sub-bullets that isn't the location). |

### `comments[]`

Human reviewer comments on this PR/commit. Rendered inline at the diff line they
reference, the same way findings are — distinguished only by an author label and
a Bitwarden Blue accent line (rather than a severity color).

```json
[
  {
    "author": "Sam (security)",
    "body": "Confirmed reproducible — `findUserByEmail(\"' OR 1=1 --\")` returns the first row.",
    "location": "src/auth/queries.ts:86",
    "created_at": "23 min ago"
  },
  {
    "author": "Pat (reviewer)",
    "body": "Worth confirming whether this helper is needed at all.",
    "location": "src/auth/queries.ts",
    "created_at": "2 hours ago"
  }
]
```

| Field        | Type   | Required | Notes                                                                                 |
| ------------ | ------ | -------- | ------------------------------------------------------------------------------------- |
| `author`     | string | yes      | Display name — keep short. Used as the gloss header and the file-row dot tooltip.     |
| `body`       | string | yes      | The comment text.                                                                     |
| `location`   | string | no       | `path/to/file.ext:lineno` anchors to that line. Path-only ⇒ file-level prologue.      |
| `created_at` | string | no       | Free-form; e.g. `"23 min ago"`. Surfaces as a small right-aligned label on the gloss. |

Only Claude findings ship with a producer (`parse_review_md.py`). Comments come
from the user (or from a future `gh api reviewThreads` integration); for now,
populate them by hand or from an external script.

### `chapters[]`

The walkthrough structure for one PR. Each chapter is a logical group of files with
a heading and a narrative paragraph that tells the reviewer what this chapter is
_about_ before they read code. Chapters render in declaration order; tests should
typically belong to the same chapter as the code they cover.

```json
[
  {
    "title": "UpgradedToPremium screen (on-Plan celebration)",
    "narrative": "A new full-screen celebration registered in vaultUnlockedGraph. Modal entry returns to the CTA host; Standard entry leaves the user on Plan. PremiumStateManager owns the upgrade-state stream that drives this surface.",
    "paths": [
      "app/src/main/.../UpgradedToPremiumScreen.kt",
      "app/src/main/.../UpgradedToPremiumViewModel.kt",
      "app/src/test/.../UpgradedToPremiumScreenTest.kt"
    ]
  }
]
```

| Field       | Type   | Required | Notes                                                                                        |
| ----------- | ------ | -------- | -------------------------------------------------------------------------------------------- |
| `title`     | string | yes      | Chapter heading — keep it short and concrete. Avoid generic labels like "Code" or "Other".   |
| `narrative` | string | yes      | One paragraph (2–4 sentences) explaining what this chapter is about. Talk concept, not file. |
| `paths`     | array  | yes      | File paths that belong to this chapter (must match `diff_b64` paths exactly).                |

**Tip:** if you can't articulate a non-trivial narrative for a chapter, the grouping
is probably wrong — merge it with another chapter or split it differently. A
chapter that earns its keep is one a reviewer can read top-down and understand the
intent of the change before they read the code.

## `merge_plan[]`

Ordered steps shown on the final page. If omitted, the scaffolder generates one item per stack PR using its `title` and `description`.

```json
{
  "title": "#2576 — Bank Account SDK bridge (PM-32809)",
  "body": "Adds CipherType.bankAccount + SDK bridge arms.",
  "zone": "Blocker: sdk-swift 2.0.0-6370-96753eef must publish before merge."
}
```

| Field   | Type   | Required | Notes                                                                                            |
| ------- | ------ | -------- | ------------------------------------------------------------------------------------------------ |
| `title` | string | yes      | Step heading.                                                                                    |
| `body`  | string | yes      | One-paragraph explanation.                                                                       |
| `zone`  | string | no       | Renders an inline "↳ ..." callout under the body — use for blockers, conflicts, follow-up notes. |

## Generated Outputs

After `scaffold.py` runs:

```
<output>/
  index.html          ← rendered from index.html.tmpl
  assets/
    app.js            ← rendered from app.js.tmpl (STACK_ORDER, TOTAL_PAGES, STORAGE_PREFIX, gh_repo subbed)
    data.js           ← generated: window.REVIEW_DATA, window.DIFFS
    styles.css        ← copied verbatim
    bw-shield.svg     ← copied verbatim
```

`window.REVIEW_DATA` is a map keyed by `stack[].key`:

```js
window.REVIEW_DATA = {
  "2573": {
    key: "2573",
    kind: "pr",
    title: "Bank Account foundation",
    ticket: "PM-32809",
    description: "...",
    verdict: "approve",
    verdictLabel: "Approved",
    findings: { critical: 0, important: 0, debt: 1, suggested: 0, question: 0 },
    filesChanged: 12,
    linesChanged: 320
  },
  ...
};
```

`window.DIFFS` is `{ key: base64-encoded-unified-diff }` — the per-PR app.js logic decodes lazily.
