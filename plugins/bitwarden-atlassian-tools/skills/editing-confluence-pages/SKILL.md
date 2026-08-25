---
name: editing-confluence-pages
description: Edit a Confluence page without breaking its open inline comments. Confluence anchors each inline comment to a text node with an annotation mark that a markdown round-trip strips, leaving the comment dangling; this skill edits through ADF so the anchor survives even when the text changes. Use for a small surgical edit (a typo, a renamed symbol, a reworded phrase) or for any edit to a page that has open inline comments — phrasings like "fix this on the Confluence page", "update the doc but keep the comments", "resolve comment 3 by changing the text", "preserve the anchors". Do not use to create a page, or to rewrite a page that has no inline comments (a plain markdown update is fine there).
when_to_use: Use when editing a Confluence page and any of these hold — the page has open inline comments that must stay attached after the edit, the user asks to preserve anchors/comments, or the edit is a small surgical change (a typo, a renamed symbol, a reworded phrase). Phrasings like "fix this on the Confluence page", "update the doc but keep the comments", "resolve comment 3 by changing the text", "preserve the anchors". Do not use for creating a fresh page, or for a large rewrite of a page that has no inline comments (a plain markdown update is fine there).
allowed-tools: mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__list_confluence_anchors, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_adf, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__replace_confluence_text, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__update_confluence_page
---

# Editing Confluence Pages

Inline comments are anchored to text, and a markdown round-trip loses that anchoring. Edit through ADF instead, so open comments stay attached to the words they were about.

Live edits are awkward to unwind, so `replace_confluence_text` and `update_confluence_page` both default to a dry run that reports what would change without sending it. A live edit takes an explicit `dryRun: false`. **Show the dry-run output and get the user's approval before any `dryRun: false` call, unless they have explicitly told you to skip it.** Running the dry run and the live write in the same turn, without the user seeing the preview, defeats the purpose — this is a shared wiki page.

## When to use

Any edit to a Confluence page where one or more of these apply:

- The page has **open inline comments**. The standard markdown update (the official Atlassian MCP server's `mcp__plugin_atlassian_atlassian__updateConfluencePage` with `contentFormat: "markdown"`, if that plugin is installed) strips the `annotation` marks that anchor those comments, leaving them dangling with no highlight on the page.
- The edit is **small** — a typo, a function-name swap, a reworded phrase — and `replace_confluence_text` can do it without routing the whole document through the conversation.
- You want to verify the anchor set **before and after** the edit.

If none apply — a fresh page, or a large rewrite of a page with **no** inline comments — a plain markdown update is fine, and this skill does not grant it. A large rewrite of a page that _does_ have open inline comments still belongs here: use the full-body workflow below.

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

The edit tools are MCP tools on the `bitwarden-atlassian` server. The two write tools require `ATLASSIAN_CONFLUENCE_WRITE_TOKEN` for a live write; without it their dry-run previews still work.

| Tool                      | What it does                                                                                                                                                         |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `list_confluence_anchors` | Lists every inline-comment anchor id and the text it covers. Read-only. Use before and after an edit to confirm the id set is unchanged.                             |
| `get_confluence_page_adf` | Fetches the page as raw ADF JSON plus its current version. Read-only. The fetch step before a full-body rewrite.                                                     |
| `replace_confluence_text` | Replaces every occurrence of a literal string, preserving marks. Dry-run by default. The safe path for small edits.                                                  |
| `update_confluence_page`  | Overwrites the body with a full ADF document. Dry-run by default; the dry run diffs anchors and warns about any that would be dropped. For larger, structural edits. |

Every edit tool takes a numeric `pageId`. To get one from a URL or a title, see the id-resolution step below; it uses `search_confluence` (by space/title) or `search_confluence_cql`.

## Resolving the page id

Do this first — the edit tools only accept a numeric `pageId`.

- **From a URL**: the id is the number in `/pages/<id>/` (or the `pageId` query param on an edit URL).
- **From a title or a description** (e.g. "the Architecture Guidelines page"): find it with `search_confluence` (filter by space and/or title) or `search_confluence_cql` (e.g. `cql: "type = page AND title ~ \"Architecture Guidelines\""`). If more than one page matches, show the candidates and confirm which one before editing.

## Workflows

### Small text swap on a page with comments

1. Resolve the page id (see above).
2. `list_confluence_anchors` — baseline the anchor set.
3. `replace_confluence_text` with `dryRun: true` — confirm the match count and that no anchor would be dropped.
4. **Show the dry-run output and get approval** (unless told to skip).
5. `replace_confluence_text` with `dryRun: false` — apply.
6. `list_confluence_anchors` again — confirm the same ids are still present.

### Larger surgical edit (rewrite a section, reorder blocks)

1. Resolve the page id (see above).
2. `list_confluence_anchors` — baseline.
3. `get_confluence_page_adf` — fetch the ADF body and note the version it reports.
4. Edit the body. On any text node whose comment should stay anchored, change the `text` and **leave its `marks` array alone**. See [examples/anchor_preserving_edit.md](examples/anchor_preserving_edit.md) for a before/after and the mistake to avoid.
5. `update_confluence_page` with `dryRun: true` and `expectedVersion` set to the version from step 3 — read the anchor diff and the version guard. If it reports anchors would be dropped, or that the page has moved, fix the body (re-fetch if it moved) before writing.
6. **Show the dry-run output and get approval** (unless told to skip).
7. `update_confluence_page` with `dryRun: false` and the same `expectedVersion` — apply. If the page changed since step 3, the write is refused rather than clobbering the newer version; re-fetch and re-apply.

## Patterns

- **Baseline with `list_confluence_anchors` before writing** whenever the page has open comments, and compare afterwards.
- **Marks are per-text-node.** To change highlighted text (e.g. rename a function inside an anchored span), edit that node's `text` and keep its `marks`. The anchor moves with the new text.
- **Don't delete an annotated text node** unless you accept the comment dangling. Splitting the node and keeping the mark on one side is fine.
- **Trust the dry-run anchor diff.** `update_confluence_page`'s dry run tells you exactly which anchors a rewritten body would drop; treat a non-empty "would be dropped" list as a stop sign, not a warning to skip.
- **Always pass `expectedVersion` to `update_confluence_page`.** A full-body overwrite spans two tool calls, so the page can change between the fetch and the write. Passing the fetched version makes the tool refuse a stale write instead of silently clobbering someone else's edit. `replace_confluence_text` reads and writes in one call, so it needs no such guard.

## Anti-patterns

- ❌ Updating a page with open inline comments via a markdown page-update tool (`contentFormat: "markdown"`). Strips every annotation mark; the comments end up dangling.
- ❌ Passing a full ADF body to `update_confluence_page` when `replace_confluence_text` would do. It bloats the conversation for no benefit.
- ❌ Deleting an annotated text node "to clean up." The comment loses its anchor. Keep at least one text node with the mark, or tell the user the anchor will dangle.

## Known gotcha

The official Atlassian MCP server's `mcp__plugin_atlassian_atlassian__updateConfluencePage` tool describes its `contentFormat` as accepting `"html"` and being round-trip safe; in practice the enum only accepts `"markdown"` and `"adf"`, and `"html"` returns an `InputValidationError`. Even `contentFormat: "adf"` on that tool only round-trips a body _you_ already hold correct — it gives you no anchor baseline, no dropped-anchor diff, no `expectedVersion` conflict guard, and (for a one-line change) no way to avoid pushing the whole document through the conversation. Those are exactly what `list_confluence_anchors`, `update_confluence_page`, and `replace_confluence_text` add, so prefer these tools for anchor-sensitive edits.
