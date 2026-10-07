# Storybook Config Schema

The `scaffold.py` script consumes a single JSON config file. This document is the source of truth for that shape.

[`examples/storybook.json`](../examples/storybook.json) is a complete config that scaffolds without warnings, with findings, a human comment, and chapters both with and without scenes. Start from it when writing a new one.

## Top-Level Object

| Field               | Type   | Required | Default                          | Notes                                                                                       |
| ------------------- | ------ | -------- | -------------------------------- | ------------------------------------------------------------------------------------------- |
| `title`             | string | no       | `"Stack review"`                 | Cover headline + default `doc_title` and `brand_meta` source.                               |
| `doc_title`         | string | no       | falls back to `title`            | The HTML `<title>` (browser tab text).                                                      |
| `brand_meta`        | string | no       | falls back to `title`            | Topbar text after the Bitwarden lockup divider.                                             |
| `summary`           | string | no       | auto-generated stack blurb       | Cover lead paragraph (2-3 sentences works best).                                            |
| `slug`              | string | no       | slugified `title`                | Used in the default output directory name.                                                  |
| `storage_prefix`    | string | no       | `"review-storybook-v1"`          | Prefix for all `localStorage` keys. Must be unique per stack to avoid cross-stack bleeding. |
| `gh_repo`           | string | no       | `"bitwarden/server"`             | `owner/name`. Drives the `ghPrUrl()` helper inside `app.js`.                                |
| `estimated_minutes` | number | no       | derived from total lines + count | Reviewer ETA shown on the cover.                                                            |
| `stack`             | array  | **yes**  | none                             | Per-PR / per-commit pages. See below.                                                       |
| `merge_plan`        | array  | no       | derived from `stack`             | Ordered merge steps. See below.                                                             |

## `stack[]` Item

| Field           | Type   | Required | Default                | Notes                                                                                                                                                                               |
| --------------- | ------ | -------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `key`           | string | **yes**  | none                   | PR number (e.g. `"2573"`) or short commit SHA. Stringified.                                                                                                                         |
| `kind`          | enum   | no       | `"pr"`                 | `"pr"` or `"commit"`. Drives the cover label (`PR 2573` vs `commit a1b2c3`).                                                                                                        |
| `title`         | string | no       | falls back to `key`    | Short human label.                                                                                                                                                                  |
| `ticket`        | string | no       | `""`                   | Jira key, e.g. `"PM-32809"`. Renders next to the title; empty omits.                                                                                                                |
| `description`   | string | no       | `""`                   | One-paragraph PR/commit summary used in the merge plan default.                                                                                                                     |
| `verdict`       | enum   | no       | `"pending"`            | One of `approve` / `approve-fix` / `block` / `no-verdict` / `pending`. See verdict notes below.                                                                                     |
| `verdict_label` | string | no       | derived from `verdict` | Override the badge text (rarely needed).                                                                                                                                            |
| `verdict_note`  | string | no       | `""`                   | The review's own qualification of its verdict: the reason for `no-verdict`, or the coverage gap on a reached verdict. See verdict notes below.                                      |
| `findings`      | object | no       | all zero               | `{ critical, important, debt, suggested, question }`, all integers.                                                                                                                 |
| `files_changed` | number | no       | derived from the diff  | Cover stats + cards. Counted from the diff when omitted or `0`; an explicit non-zero value wins.                                                                                    |
| `lines_changed` | number | no       | derived from the diff  | Cover stats + cards. Added plus removed lines, counted from the diff when omitted or `0`; an explicit non-zero value wins.                                                          |
| `diff_b64`      | string | no       | `""`                   | Base64-encoded unified diff text. Produced by `scripts/capture_diffs.py`.                                                                                                           |
| `diff_path`     | string | no       | `""`                   | Read a diff from disk and base64-encode it inline. Use **either** `diff_b64` OR `diff_path`.                                                                                        |
| `comments`      | array  | no       | `[]`                   | Human reviewer comments, rendered as marginalia alongside findings. See below.                                                                                                      |
| `chapters`      | array  | no       | `[]`                   | Ordered walkthrough groupings. Files declared here render under chapter headings; changed files no chapter lists render in an "Other files" group on the PR's last page. See below. |

### Verdict Values

| Value         | Meaning                                                     | Cover badge           |
| ------------- | ----------------------------------------------------------- | --------------------- |
| `approve`     | Reviewer signed off. No critical/important findings.        | Green "Approved"      |
| `approve-fix` | Approve, but critical or important findings need follow-up. | Amber "Approve+"      |
| `block`       | Blocked: change requested, do not merge.                    | Red "Blocked"         |
| `no-verdict`  | A review was attempted and reached no verdict.              | Teal "No verdict"     |
| `pending`     | Review not yet performed.                                   | Grey "Pending review" |

`verdict_note` carries what a reviewer needs to read before trusting the verdict:

- On `no-verdict`, it is the reason the review stopped, shown in place of the findings summary on the PR's verdict card.
- On `approve`, `approve-fix`, or `block`, it is the coverage gap: what the review did not look at, and why. It renders as a "Not covered" callout on the verdict card, and the derived `verdict_label` gains a ", coverage gap" suffix so the cover and chapter list flag it too. An explicit `verdict_label` replaces the derived one, suffix included.
- On `pending`, it is ignored.

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
pagination dot indicators. The `items[]` list, when present, drives the per-PR
**Findings** section, sorted by severity (critical -> important -> debt -> suggested ->
question).

Each item:

| Field        | Type   | Required | Notes                                                                       |
| ------------ | ------ | -------- | --------------------------------------------------------------------------- |
| `severity`   | enum   | yes      | One of `critical` / `important` / `debt` / `suggested` / `question`.        |
| `message`    | string | yes      | The finding's one-line summary as the review states it.                     |
| `location`   | string | no       | `path/to/file.ext:lineno`; a range `:start-end` anchors at its first line.  |
| `suggestion` | string | no       | Free-form follow-up text: the explanation or suggested fix from the review. |

A location the diff cannot show still renders, labeled with the location as written: a line outside the diff's hunks moves to the top of its file, and a path outside the diff joins the PR's notes that are not anchored to a file. Human comments follow the same rule.

A finding's `message` and `suggestion` and a comment's `body` render as Markdown limited to paragraphs, lists, bold, italic, inline code, fenced code (a `suggestion` fence shows as a suggested change), block quotes, and http or https links. Raw HTML and any other syntax show as plain text, since review threads carry contributor-written content.

### `comments[]`

Human reviewer comments on this PR/commit. Rendered inline at the diff line they
reference, the same way findings are, distinguished only by an author label and
a Bitwarden Blue accent line (rather than a severity color).

```json
[
  {
    "author": "Sam (security)",
    "body": "Confirmed reproducible: `findUserByEmail(\"' OR 1=1 --\")` returns the first row.",
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

| Field        | Type   | Required | Notes                                                                                       |
| ------------ | ------ | -------- | ------------------------------------------------------------------------------------------- |
| `author`     | string | yes      | Display name; keep it short. Used as the gloss header and the file-row dot tooltip.         |
| `body`       | string | yes      | The comment text.                                                                           |
| `location`   | string | no       | `path/to/file.ext:lineno` anchors to that line. A path alone anchors a file-level prologue. |
| `created_at` | string | no       | Free-form; e.g. `"23 min ago"`. Surfaces as a small right-aligned label on the gloss.       |

`fetch_pr_threads.py` produces these from human reviewer threads (it wraps
`gh api graphql` against `reviewThreads`). Use `fetch_pr_threads.py --key <PR>` to
emit a `{ key: [...comments] }` map you can merge into each stack item's
`comments[]`. Hand-authored comments are also supported; the producer is optional.

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

| Field       | Type   | Required | Notes                                                                                                                                                                              |
| ----------- | ------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `title`     | string | yes      | Chapter heading; keep it short and concrete. Avoid generic labels like "Code" or "Other".                                                                                          |
| `narrative` | string | yes      | One paragraph (2-4 sentences) explaining what this chapter is about. Talk concept, not file.                                                                                       |
| `paths`     | array  | yes      | File paths that belong to this chapter (must match `diff_b64` paths exactly). A path that matches no file in the diff renders nothing, and `scaffold.py` warns about it on stderr. |
| `scenes`    | array  | no       | Splits the chapter across several pages. When non-empty, the scenes' `paths` replace the chapter's `paths` and `paths` may be omitted. See below.                                  |

**Tip:** if you can't articulate a non-trivial narrative for a chapter, the grouping
is probably wrong. Merge it with another chapter or split it differently. A
chapter that earns its keep is one a reviewer can read top-down and understand the
intent of the change before they read the code.

#### `scenes[]`

A chapter renders as one page by default. Give it a `scenes[]` array when its files are too many for one screen, or when it tells a story in steps a reviewer should take one at a time (the contract, then the implementation, then the tests that pin it). Each scene becomes its own page, in declaration order, so a chapter with three scenes contributes three pages to the walkthrough.

```json
{
  "title": "Vault item model",
  "narrative": "Bank accounts become a first-class cipher type, from the shared model down to the SDK bridge.",
  "scenes": [
    {
      "title": "Model and enum",
      "narrative": "The new cipher type and the fields it carries.",
      "paths": [
        "src/vault/models/bank-account.ts",
        "src/vault/enums/cipher-type.ts"
      ]
    },
    {
      "title": "SDK bridge",
      "narrative": "Mapping between the client model and the SDK view.",
      "paths": ["src/vault/sdk/bank-account-mapper.ts"]
    }
  ]
}
```

| Field       | Type   | Required | Notes                                                                                      |
| ----------- | ------ | -------- | ------------------------------------------------------------------------------------------ |
| `title`     | string | no       | Page heading for this scene. Falls back to the chapter `title` when empty.                 |
| `narrative` | string | no       | One or two sentences shown on this scene's page, below the chapter intro on the first one. |
| `paths`     | array  | no       | File paths shown on this scene's page, matched against the diff the same way as chapters.  |

`scaffold.py` enforces the following when it loads the config:

- `scenes` defaults to `[]` and must be an array; anything else exits with an error.
- Each scene is an object whose `title` and `narrative` default to `""` and whose `paths` defaults to `[]`; a `paths` that is not an array exits with an error.
- Every scene path, like every chapter path, is checked against the diff, and one that matches no changed file is reported as a warning on stderr.

How the pages and paths fit together:

- The chapter's `narrative` renders once, as an intro on the chapter's first scene page. Each scene's `narrative` renders on its own page.
- When `scenes` is non-empty, only the scene `paths` decide what renders. A path listed in the chapter's own `paths` but in no scene is not shown under the chapter, and counts as unassigned.
- An empty `scenes` array behaves as if it were absent: the chapter is one page showing its own `paths`.
- After all chapters and scenes are laid out, any changed file that no chapter or scene claims renders once in an **Other files** group on the PR's last page, next to the verdict recap. A PR with no `chapters` at all skips this and shows every changed file on its single page.

The first PR in [`examples/storybook.json`](../examples/storybook.json) splits a chapter into scenes and claims every changed file, so it renders no Other files group.

## `merge_plan[]`

Ordered steps shown on the final page. If omitted, the scaffolder generates one item per stack PR using its `title` and `description`.

```json
{
  "title": "#2576: Bank Account SDK bridge (PM-32809)",
  "body": "Adds CipherType.bankAccount + SDK bridge arms.",
  "zone": "Blocker: sdk-swift 2.0.0-6370-96753eef must publish before merge."
}
```

| Field   | Type   | Required | Notes                                                                                            |
| ------- | ------ | -------- | ------------------------------------------------------------------------------------------------ |
| `title` | string | yes      | Step heading.                                                                                    |
| `body`  | string | yes      | One-paragraph explanation.                                                                       |
| `zone`  | string | no       | Renders an indented callout under the body. Use it for blockers, conflicts, and follow-up notes. |

## Generated Outputs

After `scaffold.py` runs:

```
<output>/
  index.html          <- rendered from index.html.tmpl
  assets/
    app.js            <- rendered from app.js.tmpl (STACK_ORDER, TOTAL_PAGES, STORAGE_PREFIX, gh_repo subbed)
    data.js           <- generated: window.REVIEW_DATA, window.DIFFS
    styles.css        <- copied verbatim
    bw-shield.svg     <- copied verbatim
    vendor/           <- copied verbatim (Prism, the Inter font, and their licenses)
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
    verdictNote: "",
    findings: { critical: 0, important: 0, debt: 1, suggested: 0, question: 0 },
    filesChanged: 12,
    linesChanged: 320
  },
  ...
};
```

`window.DIFFS` is `{ key: base64-encoded-unified-diff }`; the per-PR app.js logic decodes lazily.
