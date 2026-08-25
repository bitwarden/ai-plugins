# Anchor-preserving edit: worked example

The load-bearing rule of a full-body edit is: **change a text node's `text`, but leave its `marks` array alone.** The annotation mark is the inline comment's anchor. If the mark stays, the comment stays attached — even to different words. If the node (and its mark) disappears, the comment dangles.

This example walks one anchored span through a correct edit and through the two ways to get it wrong.

## The starting body

A paragraph fetched with `get_confluence_page_adf`. The phrase "exportItems()" carries an inline-comment anchor (`marks` holds an `annotation`); the surrounding text does not.

```json
{
  "type": "paragraph",
  "content": [
    { "type": "text", "text": "Call " },
    {
      "type": "text",
      "text": "exportItems()",
      "marks": [
        {
          "type": "annotation",
          "attrs": { "id": "a1b2c3", "annotationType": "inlineComment" }
        }
      ]
    },
    { "type": "text", "text": " to write the vault." }
  ]
}
```

`list_confluence_anchors` on this page reports:

```
- a1b2c3
  - "exportItems()"
```

## Correct: change the text, keep the mark

The reviewer's comment asked to make the export format explicit. Edit only the `text` field of the anchored node. Its `marks` array is untouched, so anchor `a1b2c3` moves onto the new text.

```json
{
  "type": "text",
  "text": "exportItems(format)",
  "marks": [
    {
      "type": "annotation",
      "attrs": { "id": "a1b2c3", "annotationType": "inlineComment" }
    }
  ]
}
```

After pushing, `list_confluence_anchors` reports the **same id** over the **new text**:

```
- a1b2c3
  - "exportItems(format)"
```

The `update_confluence_page` dry run confirms this before you write: `Inline-comment anchors: 1 on the live page, 1 in the submitted body (all preserved)`.

## Wrong #1: dropping the mark

Same new text, but the `marks` array was dropped (a common result of regenerating the node from plain text):

```json
{ "type": "text", "text": "exportItems(format)" }
```

The dry run catches it: `1 on the live page, 0 in the submitted body — ⚠️ 1 would be dropped: a1b2c3`. Writing this would leave the inline comment with nothing to point at.

## Wrong #2: deleting the node

Rewriting the paragraph and omitting the anchored node entirely — or "cleaning up" by collapsing the three text nodes into one plain node — removes the mark with it. Same outcome: the dry run reports `a1b2c3` would be dropped.

If the change genuinely requires removing the anchored text, that is a real decision, not an accident: either keep at least one text node carrying the `a1b2c3` mark, or tell the user the comment will be left dangling and confirm before writing.
