import { describe, it, expect } from "vitest";
import {
  walkTextNodes,
  replaceInTextNodes,
  collectInlineCommentAnchors,
  AdfNode,
} from "./confluence-adf.js";

/** A small document: one paragraph with an anchored span and a plain span. */
function doc(): AdfNode {
  return {
    type: "doc",
    version: 1,
    content: [
      {
        type: "paragraph",
        content: [
          { type: "text", text: "The value is " },
          {
            type: "text",
            text: "to_rfc3339()",
            marks: [
              {
                type: "annotation",
                attrs: { id: "anchor-1", annotationType: "inlineComment" },
              },
            ],
          },
          { type: "text", text: " today." },
        ],
      },
    ],
  };
}

describe("walkTextNodes", () => {
  it("visits every text node in document order", () => {
    const seen: string[] = [];
    walkTextNodes(doc(), (n) => seen.push(n.text ?? ""));
    expect(seen).toEqual(["The value is ", "to_rfc3339()", " today."]);
  });

  it("ignores non-text nodes and tolerates empty content", () => {
    const seen: string[] = [];
    walkTextNodes({ type: "doc", content: [{ type: "rule" }] }, (n) =>
      seen.push(n.text ?? ""),
    );
    expect(seen).toEqual([]);
    expect(() => walkTextNodes(undefined, () => {})).not.toThrow();
  });
});

describe("replaceInTextNodes", () => {
  it("replaces across text nodes and reports counts", () => {
    const body = doc();
    const result = replaceInTextNodes(
      body,
      "to_rfc3339()",
      "to_rfc3339_opts(true)",
    );
    expect(result).toEqual({ nodeCount: 1, occurrenceCount: 1 });
    expect(body.content![0].content![1].text).toBe("to_rfc3339_opts(true)");
  });

  it("preserves the annotation mark on the replaced text node", () => {
    const body = doc();
    replaceInTextNodes(body, "to_rfc3339()", "changed");
    const node = body.content![0].content![1];
    expect(node.marks).toEqual([
      {
        type: "annotation",
        attrs: { id: "anchor-1", annotationType: "inlineComment" },
      },
    ]);
  });

  it("counts every occurrence when a node matches more than once", () => {
    const body: AdfNode = {
      type: "doc",
      content: [
        { type: "paragraph", content: [{ type: "text", text: "a a a" }] },
      ],
    };
    const result = replaceInTextNodes(body, "a", "b");
    expect(result).toEqual({ nodeCount: 1, occurrenceCount: 3 });
    expect(body.content![0].content![0].text).toBe("b b b");
  });

  it("treats the search string literally, not as a regex", () => {
    const body: AdfNode = {
      type: "doc",
      content: [
        {
          type: "paragraph",
          content: [{ type: "text", text: "cost is $5.00" }],
        },
      ],
    };
    const result = replaceInTextNodes(body, "$5.00", "$6.00");
    expect(result.occurrenceCount).toBe(1);
    expect(body.content![0].content![0].text).toBe("cost is $6.00");
  });

  it("reports zero when nothing matches and leaves the body unchanged", () => {
    const body = doc();
    const before = JSON.stringify(body);
    const result = replaceInTextNodes(body, "absent", "x");
    expect(result).toEqual({ nodeCount: 0, occurrenceCount: 0 });
    expect(JSON.stringify(body)).toBe(before);
  });
});

describe("collectInlineCommentAnchors", () => {
  it("returns each anchor id with the text it covers", () => {
    expect(collectInlineCommentAnchors(doc())).toEqual([
      { id: "anchor-1", fragments: ["to_rfc3339()"] },
    ]);
  });

  it("groups fragments of one anchor split across nodes, in order", () => {
    const mark = {
      type: "annotation",
      attrs: { id: "split", annotationType: "inlineComment" },
    };
    const body: AdfNode = {
      type: "doc",
      content: [
        {
          type: "paragraph",
          content: [
            { type: "text", text: "first ", marks: [mark] },
            { type: "text", text: "bold", marks: [mark, { type: "strong" }] },
            { type: "text", text: " last", marks: [mark] },
          ],
        },
      ],
    };
    expect(collectInlineCommentAnchors(body)).toEqual([
      { id: "split", fragments: ["first ", "bold", " last"] },
    ]);
  });

  it("ignores non-annotation marks", () => {
    const body: AdfNode = {
      type: "doc",
      content: [
        {
          type: "paragraph",
          content: [
            {
              type: "text",
              text: "linked",
              marks: [{ type: "link", attrs: { href: "https://x" } }],
            },
          ],
        },
      ],
    };
    expect(collectInlineCommentAnchors(body)).toEqual([]);
  });
});
