---
name: editing-confluence-pages
description: Edit a Confluence page while keeping its inline-comment anchors, layouts, and other ADF features intact — the things a markdown round-trip silently strips. Uses ADF-native MCP tools that preserve the annotation marks anchoring open inline comments.
when_to_use: Use when editing a Confluence page and any of these hold — the page has open inline comments that must stay attached after the edit, the user asks to preserve anchors/comments, or the edit is a small surgical change (a typo, a renamed symbol, a reworded phrase). Phrasings like "fix this on the Confluence page", "update the doc but keep the comments", "resolve comment 3 by changing the text", "preserve the anchors". Do not use for creating a fresh page, or for a large rewrite of a page that has no inline comments (the standard markdown update is fine there).
allowed-tools: Read, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__list_confluence_anchors, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_adf, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__replace_confluence_text, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__update_confluence_page
---

# Editing Confluence Pages

Inline comments are anchored to text, and a markdown round-trip loses that anchoring. Edit through ADF instead, so open comments stay attached to the words they were about.

Live edits are awkward to unwind, so `replace_confluence_text` and `update_confluence_page` both default to a dry run that reports what would change without sending it. A live edit takes an explicit `dryRun: false`. Confirm before writing when the user has flagged anchors as fragile.

## When to use

Any edit to a Confluence page where one or more of these apply:

- The page has **open inline comments**. The standard markdown update (`updateConfluencePage` with `contentFormat: "markdown"`) strips the `annotation` marks that anchor those comments, leaving them dangling with no highlight on the page.
- The edit is **small** — a typo, a function-name swap, a reworded phrase — and `replace_confluence_text` can do it without routing the whole document through the conversation.
- You want to verify the anchor set **before and after** the edit.

If none apply — a fresh page, no comments, a big rewrite — the standard `mcp__plugin_atlassian_atlassian__updateConfluencePage` with markdown is fine.

## Why ADF, not markdown

Confluence stores an inline comment's anchor as an `annotation` mark on the text node it covers:

```json
{
  "type": "annotation",
  "attrs": { "id": "<uuid>", "annotationType": "inlineComment" }
}
```

- **markdown → ADF**: the API fabricates ADF from your markdown. Markdown never carried the annotation marks, so they cannot be reconstructed. Every inline-comment anchor becomes dangling.
- **ADF → ADF**: the round-trip is lossless. Annotation marks survive unless you delete the text node they sit on.

The anchor is the mark, not the text. You can change the highlighted text itself without breaking the anchor, as long as the mark stays on the replacement text node.

## Tools

All four are MCP tools on the `bitwarden-atlassian` server. The two edit tools require `ATLASSIAN_CONFLUENCE_WRITE_TOKEN` for a live write; without it their dry-run previews still work.

| Tool                      | What it does                                                                                                                                                         |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `list_confluence_anchors` | Lists every inline-comment anchor id and the text it covers. Read-only. Use before and after an edit to confirm the id set is unchanged.                             |
| `get_confluence_page_adf` | Fetches the page as raw ADF JSON plus its current version. Read-only. The fetch step before a full-body rewrite.                                                     |
| `replace_confluence_text` | Replaces every occurrence of a literal string, preserving marks. Dry-run by default. The safe path for small edits.                                                  |
| `update_confluence_page`  | Overwrites the body with a full ADF document. Dry-run by default; the dry run diffs anchors and warns about any that would be dropped. For larger, structural edits. |

## Workflows

### Small text swap on a page with comments

1. `list_confluence_anchors` — baseline the anchor set.
2. `replace_confluence_text` with `dryRun: true` — confirm the match count and that no anchor would be dropped.
3. `replace_confluence_text` with `dryRun: false` — apply.
4. `list_confluence_anchors` again — confirm the same ids are still present.

### Larger surgical edit (rewrite a section, reorder blocks)

1. `list_confluence_anchors` — baseline.
2. `get_confluence_page_adf` — fetch the ADF body and note the version it reports.
3. Edit the body. On any text node whose comment should stay anchored, change the `text` and **leave its `marks` array alone**.
4. `update_confluence_page` with `dryRun: true` and `expectedVersion` set to the version from step 2 — read the anchor diff and the version guard. If it reports anchors would be dropped, or that the page has moved, fix the body (re-fetch if it moved) before writing.
5. `update_confluence_page` with `dryRun: false` and the same `expectedVersion` — apply. If the page changed since step 2, the write is refused rather than clobbering the newer version; re-fetch and re-apply.

## Patterns

- **Baseline with `list_confluence_anchors` before writing** whenever the page has open comments, and compare afterwards.
- **Marks are per-text-node.** To change highlighted text (e.g. rename a function inside an anchored span), edit that node's `text` and keep its `marks`. The anchor moves with the new text.
- **Don't delete an annotated text node** unless you accept the comment dangling. Splitting the node and keeping the mark on one side is fine.
- **Trust the dry-run anchor diff.** `update_confluence_page`'s dry run tells you exactly which anchors a rewritten body would drop; treat a non-empty "would be dropped" list as a stop sign, not a warning to skip.
- **Always pass `expectedVersion` to `update_confluence_page`.** A full-body overwrite spans two tool calls, so the page can change between the fetch and the write. Passing the fetched version makes the tool refuse a stale write instead of silently clobbering someone else's edit. `replace_confluence_text` reads and writes in one call, so it needs no such guard.

## Anti-patterns

- ❌ Calling `updateConfluencePage` with `contentFormat: "markdown"` on a page with open inline comments. Strips every annotation mark; the comments end up dangling.
- ❌ Passing a full ADF body to `update_confluence_page` when `replace_confluence_text` would do. It bloats the conversation for no benefit.
- ❌ Deleting an annotated text node "to clean up." The comment loses its anchor. Keep at least one text node with the mark, or tell the user the anchor will dangle.

## Known gotcha

The `mcp__plugin_atlassian_atlassian__updateConfluencePage` tool's `contentFormat` description claims `"html"` is round-trip safe and preserves inline comments. The enum only accepts `"markdown"` and `"adf"`; `"html"` returns an `InputValidationError`. For round-trip safety, use these ADF tools.
