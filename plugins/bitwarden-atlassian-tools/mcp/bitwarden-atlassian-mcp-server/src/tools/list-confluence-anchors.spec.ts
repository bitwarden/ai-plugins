import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

const mockGet = vi.fn();

vi.mock("axios", () => {
  const mockAxios: any = {
    create: vi.fn(() => ({
      get: mockGet,
      interceptors: { response: { use: vi.fn() } },
    })),
  };
  return { default: mockAxios };
});

import listConfluenceAnchorsTool from "./list-confluence-anchors.js";

function pageResponse(body: unknown) {
  return {
    data: {
      id: "2923724969",
      title: "Design Notes",
      status: "current",
      version: { number: 2 },
      body: {
        atlas_doc_format: {
          value: JSON.stringify(body),
          representation: "atlas_doc_format",
        },
      },
      _links: { webui: "/wiki/spaces/EN/pages/2923724969" },
    },
  };
}

describe("list_confluence_anchors handler", () => {
  const ENV_KEYS = [
    "ATLASSIAN_CLOUD_ID",
    "ATLASSIAN_EMAIL",
    "ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN",
  ] as const;
  const saved: Record<string, string | undefined> = {};

  beforeEach(() => {
    vi.clearAllMocks();
    for (const key of ENV_KEYS) saved[key] = process.env[key];
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

  it("lists each anchor id and the text it covers", async () => {
    mockGet.mockResolvedValueOnce(
      pageResponse({
        type: "doc",
        content: [
          {
            type: "paragraph",
            content: [
              {
                type: "text",
                text: "anchored",
                marks: [
                  {
                    type: "annotation",
                    attrs: { id: "abc-123", annotationType: "inlineComment" },
                  },
                ],
              },
            ],
          },
        ],
      }),
    );

    const out = await listConfluenceAnchorsTool.handler({
      pageId: "2923724969",
    });

    expect(out).toContain("1 anchor(s)");
    expect(out).toContain("abc-123");
    expect(out).toContain('"anchored"');
  });

  it("reports when a page has no anchors", async () => {
    mockGet.mockResolvedValueOnce(
      pageResponse({
        type: "doc",
        content: [
          { type: "paragraph", content: [{ type: "text", text: "plain" }] },
        ],
      }),
    );

    const out = await listConfluenceAnchorsTool.handler({
      pageId: "2923724969",
    });

    expect(out).toContain("No inline-comment anchors found");
  });

  it("rejects a non-numeric page id before making a request", async () => {
    // Validation runs before the fetch; the server wrapper turns the throw into
    // an error result. What matters here is that no request goes out.
    await expect(
      listConfluenceAnchorsTool.handler({ pageId: "../secret" }),
    ).rejects.toThrow(/numeric Confluence page id/);
    expect(mockGet).not.toHaveBeenCalled();
  });
});
