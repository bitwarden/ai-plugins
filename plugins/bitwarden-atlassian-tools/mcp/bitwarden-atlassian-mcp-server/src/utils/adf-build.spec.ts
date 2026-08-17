import { describe, it, expect } from "vitest";

import { buildDescriptionAdf } from "./adf-build.js";

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
