import { describe, it, expect } from "vitest";

import { buildDescriptionAdf, buildCommentAdf } from "./adf-build.js";

describe("buildDescriptionAdf", () => {
  it("builds one ADF paragraph per input string", () => {
    const doc = buildDescriptionAdf(["First para.", "Second para."]);

    expect(doc).toEqual({
      version: 1,
      type: "doc",
      content: [
        { type: "paragraph", content: [{ type: "text", text: "First para." }] },
        {
          type: "paragraph",
          content: [{ type: "text", text: "Second para." }],
        },
      ],
    });
  });

  it("trims surrounding whitespace", () => {
    const doc = buildDescriptionAdf(["  padded  "]);

    expect(doc?.content[0].content[0].text).toBe("padded");
  });

  it("drops empty and whitespace-only paragraphs", () => {
    const doc = buildDescriptionAdf(["kept", "   ", ""]);

    expect(doc?.content).toHaveLength(1);
  });

  it("returns undefined when there is nothing to send", () => {
    expect(buildDescriptionAdf([])).toBeUndefined();
    expect(buildDescriptionAdf(["  ", ""])).toBeUndefined();
  });
});

describe("buildCommentAdf", () => {
  it("builds a single paragraph for text with no blank lines", () => {
    const doc = buildCommentAdf("Looks good to me.");

    expect(doc).toEqual({
      version: 1,
      type: "doc",
      content: [
        {
          type: "paragraph",
          content: [{ type: "text", text: "Looks good to me." }],
        },
      ],
    });
  });

  it("splits on blank lines into separate paragraphs", () => {
    const doc = buildCommentAdf("First paragraph.\n\nSecond paragraph.");

    expect(doc.content).toEqual([
      {
        type: "paragraph",
        content: [{ type: "text", text: "First paragraph." }],
      },
      {
        type: "paragraph",
        content: [{ type: "text", text: "Second paragraph." }],
      },
    ]);
  });

  it("treats blank lines with trailing whitespace as paragraph breaks", () => {
    const doc = buildCommentAdf("First.\n  \nSecond.\n\n\nThird.");

    expect(doc.content).toEqual([
      { type: "paragraph", content: [{ type: "text", text: "First." }] },
      { type: "paragraph", content: [{ type: "text", text: "Second." }] },
      { type: "paragraph", content: [{ type: "text", text: "Third." }] },
    ]);
  });
});
