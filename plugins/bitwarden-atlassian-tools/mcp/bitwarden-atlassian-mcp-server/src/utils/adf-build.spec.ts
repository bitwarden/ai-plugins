import { readFileSync } from "node:fs";

import { describe, it, expect } from "vitest";

import { buildDescriptionAdf, buildCommentAdf } from "./adf-build.js";

/** A paragraph of unstyled text, the shape plain prose still converts to. */
const paragraph = (text: string) => ({
  type: "paragraph",
  content: [{ type: "text", text }],
});

describe("buildDescriptionAdf", () => {
  it("builds one ADF paragraph per input string", () => {
    const doc = buildDescriptionAdf(["First para.", "Second para."]);

    expect(doc).toEqual({
      version: 1,
      type: "doc",
      content: [paragraph("First para."), paragraph("Second para.")],
    });
  });

  it("trims surrounding whitespace", () => {
    const doc = buildDescriptionAdf(["  padded  "]);

    expect(doc?.content).toEqual([paragraph("padded")]);
  });

  it("drops empty and whitespace-only paragraphs", () => {
    const doc = buildDescriptionAdf(["kept", "   ", ""]);

    expect(doc?.content).toEqual([paragraph("kept")]);
  });

  it("returns undefined when there is nothing to send", () => {
    expect(buildDescriptionAdf([])).toBeUndefined();
    expect(buildDescriptionAdf(["  ", ""])).toBeUndefined();
  });

  it("converts inline markdown to ADF marks", () => {
    const doc = buildDescriptionAdf([
      "Ship **now**, see [ticket](http://x/1).",
    ]);

    expect(doc?.content).toEqual([
      {
        type: "paragraph",
        content: [
          { type: "text", text: "Ship " },
          { type: "text", text: "now", marks: [{ type: "strong" }] },
          { type: "text", text: ", see " },
          {
            type: "text",
            text: "ticket",
            marks: [{ type: "link", attrs: { href: "http://x/1" } }],
          },
          { type: "text", text: "." },
        ],
      },
    ]);
  });

  it("expands an entry whose markdown is a list into one block", () => {
    const doc = buildDescriptionAdf(["- first", "closing prose"]);

    expect(doc?.content.map((node) => node.type)).toEqual([
      "bulletList",
      "paragraph",
    ]);
  });

  it("keeps a fenced code block's language", () => {
    const doc = buildDescriptionAdf(["```ts\nconst x = 1;\n```"]);

    expect(doc?.content).toEqual([
      {
        type: "codeBlock",
        attrs: { language: "ts" },
        content: [{ type: "text", text: "const x = 1;" }],
      },
    ]);
  });

  it("leaves underscores inside identifiers alone", () => {
    const doc = buildDescriptionAdf(["snake_case_name stays intact"]);

    expect(doc?.content).toEqual([paragraph("snake_case_name stays intact")]);
  });
});

describe("buildCommentAdf", () => {
  it("builds a single paragraph for text with no blank lines", () => {
    const doc = buildCommentAdf("Looks good to me.");

    expect(doc).toEqual({
      version: 1,
      type: "doc",
      content: [paragraph("Looks good to me.")],
    });
  });

  it("splits on blank lines into separate paragraphs", () => {
    const doc = buildCommentAdf("First paragraph.\n\nSecond paragraph.");

    expect(doc.content).toEqual([
      paragraph("First paragraph."),
      paragraph("Second paragraph."),
    ]);
  });

  it("treats blank lines with trailing whitespace as paragraph breaks", () => {
    const doc = buildCommentAdf("First.\n  \nSecond.\n\n\nThird.");

    expect(doc.content).toEqual([
      paragraph("First."),
      paragraph("Second."),
      paragraph("Third."),
    ]);
  });

  it("converts block markdown a reviewer would actually write", () => {
    const doc = buildCommentAdf(
      "Two problems:\n\n- the guard is inverted\n- the test is skipped\n\n```sh\npnpm test\n```",
    );

    expect(doc.content.map((node) => node.type)).toEqual([
      "paragraph",
      "bulletList",
      "codeBlock",
    ]);
  });

  it("falls back to a plain paragraph when markdown yields no blocks", () => {
    // A bare link reference definition declares a label and renders nothing.
    const doc = buildCommentAdf("[ref]: https://example.com");

    expect(doc).toEqual({
      version: 1,
      type: "doc",
      content: [paragraph("[ref]: https://example.com")],
    });
  });
});

describe("link target sanitization", () => {
  /** The text nodes of a single-paragraph comment body. */
  const inline = (markdown: string) =>
    buildCommentAdf(markdown).content[0].content;

  it.each([
    ["javascript:", "[x](javascript:alert(1))"],
    ["mixed-case javascript:", "[x](JavaScript:alert(1))"],
    ["data:", "[x](data:text/html,hello)"],
    ["vbscript:", "[x](vbscript:evil)"],
  ])("drops a %s link target but keeps its text", (_label, markdown) => {
    expect(inline(markdown)).toEqual([{ type: "text", text: "x" }]);
  });

  it.each([
    "https://example.com/a",
    "http://example.com/a",
    "mailto:someone@example.com",
    "/browse/PM-1",
  ])("keeps the allowed target %s", (href) => {
    expect(inline(`[ok](${href})`)).toEqual([
      {
        type: "text",
        text: "ok",
        marks: [{ type: "link", attrs: { href } }],
      },
    ]);
  });

  it("keeps sibling marks when dropping an unsafe link", () => {
    expect(inline("**bold [x](javascript:alert(1))**")).toEqual([
      { type: "text", text: "bold ", marks: [{ type: "strong" }] },
      { type: "text", text: "x", marks: [{ type: "strong" }] },
    ]);
  });

  it("sanitizes targets nested inside a block", () => {
    const doc = buildCommentAdf("- see [x](javascript:alert(1))");

    expect(JSON.stringify(doc)).not.toContain("javascript:");
    expect(JSON.stringify(doc)).toContain('"text":"x"');
  });

  it("sanitizes description paragraphs as well as comments", () => {
    const doc = buildDescriptionAdf(["see [x](javascript:alert(1))"]);

    expect(JSON.stringify(doc)).not.toContain("javascript:");
  });
});

/** Every character of text a document carries, in order. */
function allText(nodes: readonly unknown[]): string {
  return nodes
    .map((node) => {
      if (node === null || typeof node !== "object") {
        return "";
      }

      const { type, text, content } = node as {
        type?: string;
        text?: string;
        content?: unknown[];
      };

      return type === "text" ? (text ?? "") : allText(content ?? []);
    })
    .join("");
}

describe("text preservation", () => {
  // Markdown reads `<` followed by a name as opening an HTML tag, and raw HTML
  // is discarded rather than rendered. Left alone that silently eats ordinary
  // ticket prose, so every one of these must round-trip exactly.
  it.each([
    "Change the return type to List<String>",
    "Use Map<String, List<Int>> here",
    "When the user enters <password> into the field",
    "a <b> and <c> pair",
    "a < b and c > d",
    "compare 1<2",
    "close the </div> tag",
  ])("keeps every character of %j", (body) => {
    expect(allText(buildCommentAdf(body).content)).toBe(body);
  });

  it("keeps angle brackets in a description entry", () => {
    const doc = buildDescriptionAdf(["needs List<String>"]);

    expect(allText(doc?.content ?? [])).toBe("needs List<String>");
  });

  // Asserted on node structure, not through `allText`: a concatenation helper
  // reads the same whether the text arrives as one node or several, and
  // adjacent text nodes carrying identical marks are non-canonical ADF.
  it("emits one text node rather than fragmenting around the bracket", () => {
    const doc = buildCommentAdf("Use List<String> in the DTO");

    expect(doc.content).toEqual([paragraph("Use List<String> in the DTO")]);
  });

  it.each([
    ["an inline code span", "use `List<String>` here", "use List<String> here"],
    [
      "a fenced block",
      "```ts\nconst a: List<String> = b < c;\n```",
      "const a: List<String> = b < c;",
    ],
    ["a tilde-fenced block", "~~~\nx <y> z\n~~~", "x <y> z"],
  ])("leaves %s untouched", (_label, body, expected) => {
    expect(allText(buildCommentAdf(body).content)).toBe(expected);
  });
});

describe("image target sanitization", () => {
  // An image carries its target in the media node's attrs rather than in a
  // link mark, so checking only marks would let an unsafe scheme through.
  it.each(["![x](javascript:alert(1))", "![x](data:text/html,hi)"])(
    "drops the media node for %j and keeps the text",
    (body) => {
      const doc = buildCommentAdf(body);

      expect(JSON.stringify(doc)).not.toContain('"media"');
      expect(allText(doc.content)).toBe(body);
    },
  );

  it("keeps an image whose target is allowed", () => {
    const doc = buildCommentAdf("![x](https://example.com/a.png)");

    expect(doc.content).toEqual([
      {
        type: "mediaSingle",
        attrs: { layout: "center" },
        content: [
          {
            type: "media",
            attrs: {
              type: "external",
              url: "https://example.com/a.png",
              alt: "x",
            },
          },
        ],
      },
    ]);
  });
});

describe("encoded link targets", () => {
  // `new URL` rejects these, so a fallback that assumed "cannot be parsed means
  // relative" would keep them. Anything decoding entities into an href would
  // then recover a real javascript: scheme.
  it.each([
    "[x](javascript&colon;alert(1))",
    "[x](javascript&#58;alert(1))",
    "[x](not-a-scheme-at-all)",
  ])("drops the link mark for %j", (body) => {
    expect(buildCommentAdf(body).content).toEqual([
      { type: "paragraph", content: [{ type: "text", text: "x" }] },
    ]);
  });

  // A scheme-relative target inherits Jira's scheme, so it is equivalent to
  // the absolute https link the allowlist already admits.
  it.each([
    "[x](//example.com/p)",
    "[x](/browse/PM-1)",
    "[x](#a)",
    "[x](?q=1)",
  ])("keeps the scheme-relative target %j", (body) => {
    expect(JSON.stringify(buildCommentAdf(body))).toContain('"link"');
  });
});

describe("block-level HTML", () => {
  it("keeps a block HTML tag as text instead of discarding the block", () => {
    const doc = buildCommentAdf(
      "Before\n\n<div>the requirement</div>\n\nAfter",
    );

    expect(doc.content).toHaveLength(3);
    expect(allText(doc.content)).toBe("Before<div>the requirement</div>After");
  });
});

describe("description entries never vanish", () => {
  it.each([
    "<details><summary>s</summary>body</details>",
    "<br>",
    "[ref]: https://example.com",
  ])("keeps an entry whose markdown renders nothing: %j", (entry) => {
    const doc = buildDescriptionAdf(["intro", entry]);

    expect(doc?.content).toHaveLength(2);
    expect(allText(doc?.content ?? [])).toBe(`intro${entry}`);
  });

  it("still omits the description when every entry is blank", () => {
    expect(buildDescriptionAdf(["  ", ""])).toBeUndefined();
  });
});

// Whether a `<` is markup depends on lexical context, and every one of these
// shapes was mis-read by an earlier hand-rolled bracket scan. They are kept as
// regression cases against reintroducing one.
describe("lexical edge cases", () => {
  const CR = String.fromCharCode(13);

  it.each([
    ["an unclosed fence", "```\nconst a = b<c;", "const a = b<c;"],
    ["an unclosed tilde fence", "~~~\nx <y>", "x <y>"],
    [
      "a CRLF fence",
      "```ts" + CR + "\nList<String>" + CR + "\n```",
      "List<String>",
    ],
    ["adjacent code spans", "`a<b`c<d`e<f`", "a<bc<de<f"],
    // Mixing a code span with raw HTML forfeits rendering for the entry: it is
    // sent verbatim so no characters are lost.
    ["a multi-backtick span", "``a<b``  <tag>", "``a<b``  <tag>"],
    // `\<` already means a literal `<`, so marked reports no HTML token and
    // the entry converts normally.
    ["an already-escaped bracket", "a \\<tag> b", "a <tag> b"],
  ])("handles %s", (_label, body, expected) => {
    expect(allText(buildCommentAdf(body).content)).toBe(expected);
  });

  // Asserted per block rather than as one joined string, so each expectation
  // stays readable across the paragraph break.
  it.each([
    [
      "a stray fence run in prose",
      "in ``` fences\n\nthen List<String>",
      ["in ``` fences", "then List<String>"],
    ],
    [
      "an indented code block",
      "para\n\n    if (a<b) { }\n",
      ["para", "if (a<b) { }"],
    ],
  ])("keeps every block intact for %s", (_label, body, expected) => {
    const blocks = buildCommentAdf(body).content.map((node) => allText([node]));

    expect(blocks).toEqual(expected);
  });

  it("keeps an autolink a link", () => {
    expect(buildCommentAdf("<https://ok.com>").content).toEqual([
      {
        type: "paragraph",
        content: [
          {
            type: "text",
            text: "https://ok.com",
            marks: [{ type: "link", attrs: { href: "https://ok.com" } }],
          },
        ],
      },
    ]);
  });
});

describe("degenerate bodies", () => {
  // ADF has no valid empty text node. Both write schemas reject a blank body
  // before it reaches these builders, but the builders are exported, so they
  // must not be able to emit one.
  it.each(["", "   ", "\n\n", "\t"])(
    "emits no empty text node for %j",
    (body) => {
      const doc = buildCommentAdf(body);

      expect(doc.content).toEqual([{ type: "paragraph" }]);
      expect(JSON.stringify(doc)).not.toContain('"text":""');
    },
  );
});

describe("line breaks on the verbatim path", () => {
  it("carries single newlines as hard breaks so lines do not run together", () => {
    const doc = buildCommentAdf("- item one<br>\n- item two");

    expect(doc.content).toEqual([
      {
        type: "paragraph",
        content: [
          { type: "text", text: "- item one<br>" },
          { type: "hardBreak" },
          { type: "text", text: "- item two" },
        ],
      },
    ]);
  });

  it("still splits blank-line-separated blocks into paragraphs", () => {
    const doc = buildCommentAdf("a<br>\nb\n\nc\nd");

    expect(doc.content).toHaveLength(2);
    expect(doc.content.map((node) => allText([node]))).toEqual([
      "a<br>b",
      "cd",
    ]);
  });

  it("introduces no hard break on the converting path", () => {
    expect(JSON.stringify(buildCommentAdf("- a\n- b"))).not.toContain(
      "hardBreak",
    );
  });
});

describe("marked version agreement", () => {
  // `containsRawHtml` lexes with marked to predict what marklassian will do to
  // the same input. That prediction holds only while both resolve to one copy
  // of marked, so the direct pin has to stay inside the range marklassian
  // declares. Drifting outside it installs a second copy and the agreement
  // fails silently, with no symptom until a body loses text.
  it("pins marked inside the range marklassian supports", () => {
    const read = (relative: string) =>
      JSON.parse(readFileSync(new URL(relative, import.meta.url), "utf8"));

    const pinned: string = read("../../package.json").dependencies.marked;
    const supported: string = read(
      "../../node_modules/marklassian/package.json",
    ).dependencies.marked;

    expect(pinned).toMatch(/^\d+\.\d+\.\d+$/);
    expect(supported).toContain(`^${pinned.split(".")[0]}.`);
  });
});

describe("positional nodes survive sanitization", () => {
  // Dropping a cell shifts every later cell in the row a column left, so a
  // value ends up under the wrong heading. An empty cell is the lesser evil.
  it("keeps the column count when a cell held only a blocked image", () => {
    const doc = buildCommentAdf(
      "| chart | note |\n| - | - |\n| ![c](data:image/png;base64,iVBORw0KGgo=) | up 10% |",
    );
    const table = doc.content[0] as { content: { content: unknown[] }[] };

    expect(table.content.map((row) => row.content)).toHaveLength(2);
    expect(table.content[0].content).toHaveLength(2);
    expect(table.content[1].content).toHaveLength(2);
    expect(table.content[1].content[0]).toEqual({
      type: "tableCell",
      content: [{ type: "paragraph" }],
    });
    expect(JSON.stringify(doc)).not.toContain("data:");
  });

  it("still collapses a wrapper whose position carries nothing", () => {
    const doc = buildCommentAdf("![x](javascript:alert(1))");

    expect(JSON.stringify(doc)).not.toContain('"media"');
    expect(allText(doc.content)).toBe("![x](javascript:alert(1))");
  });
});
