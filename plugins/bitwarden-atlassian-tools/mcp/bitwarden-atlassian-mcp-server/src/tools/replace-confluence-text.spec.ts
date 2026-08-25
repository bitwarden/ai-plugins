import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

const mockGet = vi.fn();
const mockPut = vi.fn();

vi.mock("axios", () => {
  const mockAxios: any = {
    create: vi.fn(() => ({
      get: mockGet,
      put: mockPut,
      interceptors: { response: { use: vi.fn() } },
    })),
  };
  return { default: mockAxios };
});

import replaceConfluenceTextTool from "./replace-confluence-text.js";

const ANNOTATION = {
  type: "annotation",
  attrs: { id: "anchor-1", annotationType: "inlineComment" },
};

function pageBody() {
  return {
    type: "doc",
    version: 1,
    content: [
      {
        type: "paragraph",
        content: [
          { type: "text", text: "Call " },
          { type: "text", text: "to_rfc3339()", marks: [ANNOTATION] },
          { type: "text", text: " here." },
        ],
      },
    ],
  };
}

/** Shape the getPageAdf() call unwraps from client.get(). */
function pageResponse(version = 3) {
  return {
    data: {
      id: "2923724969",
      title: "Design Notes",
      status: "current",
      version: { number: version },
      spaceId: "42",
      body: {
        atlas_doc_format: {
          value: JSON.stringify(pageBody()),
          representation: "atlas_doc_format",
        },
      },
      _links: { webui: "/wiki/spaces/EN/pages/2923724969" },
    },
  };
}

const base = {
  pageId: "2923724969",
  oldText: "to_rfc3339()",
  newText: "to_rfc3339_opts(true)",
};

describe("replace_confluence_text handler", () => {
  const ENV_KEYS = [
    "ATLASSIAN_CLOUD_ID",
    "ATLASSIAN_EMAIL",
    "ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN",
    "ATLASSIAN_CONFLUENCE_WRITE_TOKEN",
  ] as const;
  const saved: Record<string, string | undefined> = {};

  beforeEach(() => {
    vi.clearAllMocks();
    for (const key of ENV_KEYS) {
      saved[key] = process.env[key];
      delete process.env[key];
    }
    process.env.ATLASSIAN_CLOUD_ID = "test-cloud-id";
    process.env.ATLASSIAN_EMAIL = "user@example.com";
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = "read-token";
  });

  afterEach(() => {
    for (const key of ENV_KEYS) {
      if (saved[key] === undefined) delete process.env[key];
      else process.env[key] = saved[key];
    }
  });

  it("previews the change without writing on a dry run", async () => {
    mockGet.mockResolvedValueOnce(pageResponse());

    const out = await replaceConfluenceTextTool.handler({
      ...base,
      dryRun: true,
    });

    expect(out).toContain("Dry run: replace text");
    expect(out).toContain("1 occurrence(s) across 1 text node(s)");
    expect(out).toContain("version 3 → 4");
    expect(out).toContain("all preserved");
    expect(mockPut).not.toHaveBeenCalled();
  });

  it("reports no matches and writes nothing when the text is absent", async () => {
    mockGet.mockResolvedValueOnce(pageResponse());

    const out = await replaceConfluenceTextTool.handler({
      ...base,
      oldText: "not-present",
      dryRun: false,
    });

    expect(out).toContain("No occurrences");
    expect(mockPut).not.toHaveBeenCalled();
  });

  it("refuses a live edit when no write token is set", async () => {
    mockGet.mockResolvedValueOnce(pageResponse());

    const out = await replaceConfluenceTextTool.handler({
      ...base,
      dryRun: false,
    });

    expect(out).toContain("Refusing to edit");
    expect(out).toContain("ATLASSIAN_CONFLUENCE_WRITE_TOKEN");
    expect(mockPut).not.toHaveBeenCalled();
  });

  it("pushes the edited body, preserving the anchor, on a live edit", async () => {
    process.env.ATLASSIAN_CONFLUENCE_WRITE_TOKEN = "write-token";
    mockGet.mockResolvedValueOnce(pageResponse(3));
    mockPut.mockResolvedValueOnce({ data: { version: { number: 4 } } });

    const out = await replaceConfluenceTextTool.handler({
      ...base,
      dryRun: false,
    });

    expect(out).toContain("Updated **Design Notes** to version 4");
    expect(mockPut).toHaveBeenCalledOnce();

    const [url, payload] = mockPut.mock.calls[0];
    expect(url).toBe("/wiki/api/v2/pages/2923724969");
    expect(payload.version.number).toBe(4);

    const pushed = JSON.parse(payload.body.value);
    const editedNode = pushed.content[0].content[1];
    expect(editedNode.text).toBe("to_rfc3339_opts(true)");
    // The annotation mark rides along with the new text.
    expect(editedNode.marks).toEqual([ANNOTATION]);
  });

  it("hints at partial write-token scopes on a 401", async () => {
    process.env.ATLASSIAN_CONFLUENCE_WRITE_TOKEN = "write-token";
    mockGet.mockResolvedValueOnce(pageResponse());
    mockPut.mockRejectedValueOnce(
      new Error(
        "Confluence authentication failed. Check your API token and email.",
      ),
    );

    const out = await replaceConfluenceTextTool.handler({
      ...base,
      dryRun: false,
    });

    expect(out).toContain("Error updating page");
    expect(out).toContain("full scope");
  });
});
