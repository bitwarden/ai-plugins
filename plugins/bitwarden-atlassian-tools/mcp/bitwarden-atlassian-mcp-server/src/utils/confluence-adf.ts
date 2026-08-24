/**
 * ADF editing utilities for anchor-preserving Confluence edits.
 *
 * Confluence stores an inline comment's anchor as an `annotation` mark on the
 * text node(s) it covers:
 *
 *   { "type": "annotation",
 *     "attrs": { "id": "<uuid>", "annotationType": "inlineComment" } }
 *
 * The mark, not the text, is the anchor. Editing a text node's `text` while
 * leaving its `marks` array intact moves the anchor onto the new text; deleting
 * the node drops the anchor and leaves the comment dangling. Every helper here
 * treats a text node's `marks` as immutable for that reason.
 */

/** An ADF node. Kept loose: pages carry node types we never enumerate. */
export type AdfNode = {
  type?: string;
  text?: string;
  marks?: Array<{ type?: string; attrs?: Record<string, any> }>;
  content?: AdfNode[];
  [key: string]: any;
};

/**
 * Visit every text node in a document, depth first, in document order.
 */
export function walkTextNodes(
  node: AdfNode | AdfNode[] | undefined | null,
  visit: (textNode: AdfNode) => void,
): void {
  if (Array.isArray(node)) {
    for (const child of node) {
      walkTextNodes(child, visit);
    }
    return;
  }

  if (!node || typeof node !== "object") {
    return;
  }

  if (node.type === "text") {
    visit(node);
  }

  if (node.content) {
    walkTextNodes(node.content, visit);
  }
}

export interface ReplaceResult {
  /** Number of text nodes in which at least one occurrence was replaced. */
  nodeCount: number;
  /** Total number of occurrences replaced across all nodes. */
  occurrenceCount: number;
}

/**
 * Replace every occurrence of `oldText` with `newText` across all text nodes,
 * mutating `body` in place. Marks (including annotation marks) are untouched, so
 * an anchored span keeps its anchor even when its text changes.
 */
export function replaceInTextNodes(
  body: AdfNode,
  oldText: string,
  newText: string,
): ReplaceResult {
  let nodeCount = 0;
  let occurrenceCount = 0;

  walkTextNodes(body, (textNode) => {
    const current = textNode.text;
    if (typeof current !== "string" || !current.includes(oldText)) {
      return;
    }

    // split/join counts occurrences without a regex, so `oldText` needs no
    // escaping and can contain any characters.
    const occurrences = current.split(oldText).length - 1;
    textNode.text = current.split(oldText).join(newText);
    nodeCount += 1;
    occurrenceCount += occurrences;
  });

  return { nodeCount, occurrenceCount };
}

export interface InlineCommentAnchor {
  id: string;
  /** The text fragment(s) the anchor covers, in document order. */
  fragments: string[];
}

/**
 * Collect every inline-comment anchor in a document and the text it covers.
 *
 * The same anchor id can span multiple text nodes (a highlight broken by other
 * marks), so fragments are grouped by id while preserving first-seen order.
 */
export function collectInlineCommentAnchors(
  body: AdfNode,
): InlineCommentAnchor[] {
  const order: string[] = [];
  const byId = new Map<string, string[]>();

  walkTextNodes(body, (textNode) => {
    for (const mark of textNode.marks ?? []) {
      if (mark.type !== "annotation") {
        continue;
      }
      const id = mark.attrs?.id;
      if (typeof id !== "string") {
        continue;
      }
      if (!byId.has(id)) {
        byId.set(id, []);
        order.push(id);
      }
      byId.get(id)!.push(textNode.text ?? "");
    }
  });

  return order.map((id) => ({ id, fragments: byId.get(id)! }));
}
