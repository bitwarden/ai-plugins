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

import updateConfluencePageTool from "./update-confluence-page.js";

const ANNOTATION = {
  type: "annotation",
  attrs: { id: "anchor-1", annotationType: "inlineComment" },
};

/** Live page body: one anchored span. */
function livePageBody() {
  return {
    type: "doc",
    content: [
      {
        type: "paragraph",
        content: [{ type: "text", text: "keep me", marks: [ANNOTATION] }],
      },
    ],
  };
}

function pageResponse(version = 5) {
  return {
    data: {
      id: "2923724969",
      title: "Design Notes",
      status: "current",
      version: { number: version },
      spaceId: "42",
      body: {
        atlas_doc_format: {
          value: JSON.stringify(livePageBody()),
          representation: "atlas_doc_format",
        },
      },
      _links: { webui: "/wiki/spaces/EN/pages/2923724969" },
    },
  };
}

/** A rewritten body that still carries the anchor. */
function bodyWithAnchor() {
  return {
    type: "doc",
    content: [
      {
        type: "paragraph",
        content: [
          { type: "text", text: "kept, reworded", marks: [ANNOTATION] },
        ],
      },
    ],
  };
}

/** A rewritten body that dropped the anchored node. */
function bodyWithoutAnchor() {
  return {
    type: "doc",
    content: [
      {
        type: "paragraph",
        content: [{ type: "text", text: "no anchor here" }],
      },
    ],
  };
}

describe("update_confluence_page handler", () => {
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

  it("previews and reports anchors preserved on a dry run", async () => {
    mockGet.mockResolvedValueOnce(pageResponse());

    const out = await updateConfluencePageTool.handler({
      pageId: "2923724969",
      adfBody: bodyWithAnchor(),
      dryRun: true,
    });

    expect(out).toContain("Dry run: overwrite");
    expect(out).toContain("all preserved");
    expect(out).not.toContain("would be dropped");
    expect(mockPut).not.toHaveBeenCalled();
  });

  it("warns on a dry run when the submitted body drops an anchor", async () => {
    mockGet.mockResolvedValueOnce(pageResponse());

    const out = await updateConfluencePageTool.handler({
      pageId: "2923724969",
      adfBody: bodyWithoutAnchor(),
      dryRun: true,
    });

    expect(out).toContain("would be dropped: anchor-1");
    expect(out).toContain("dangling");
    expect(mockPut).not.toHaveBeenCalled();
  });

  it("refuses a live write when no write token is set", async () => {
    mockGet.mockResolvedValueOnce(pageResponse());

    const out = await updateConfluencePageTool.handler({
      pageId: "2923724969",
      adfBody: bodyWithAnchor(),
      dryRun: false,
    });

    expect(out).toContain("Refusing to edit");
    expect(out).toContain("ATLASSIAN_CONFLUENCE_WRITE_TOKEN");
    expect(mockPut).not.toHaveBeenCalled();
  });

  it("pushes the submitted body on a live write", async () => {
    process.env.ATLASSIAN_CONFLUENCE_WRITE_TOKEN = "write-token";
    mockGet.mockResolvedValueOnce(pageResponse(5));
    mockPut.mockResolvedValueOnce({ data: { version: { number: 6 } } });

    const body = bodyWithAnchor();
    const out = await updateConfluencePageTool.handler({
      pageId: "2923724969",
      adfBody: body,
      dryRun: false,
    });

    expect(out).toContain("Updated **Design Notes** to version 6");
    const [url, payload] = mockPut.mock.calls[0];
    expect(url).toBe("/wiki/api/v2/pages/2923724969");
    expect(payload.version.number).toBe(6);
    expect(JSON.parse(payload.body.value)).toEqual(body);
  });

  it("writes when expectedVersion matches the live version", async () => {
    process.env.ATLASSIAN_CONFLUENCE_WRITE_TOKEN = "write-token";
    mockGet.mockResolvedValueOnce(pageResponse(5));
    mockPut.mockResolvedValueOnce({ data: { version: { number: 6 } } });

    const out = await updateConfluencePageTool.handler({
      pageId: "2923724969",
      adfBody: bodyWithAnchor(),
      expectedVersion: 5,
      dryRun: false,
    });

    expect(out).toContain("Updated **Design Notes** to version 6");
    expect(mockPut).toHaveBeenCalledOnce();
  });

  it("refuses a live write when the page moved past expectedVersion", async () => {
    process.env.ATLASSIAN_CONFLUENCE_WRITE_TOKEN = "write-token";
    // Live page is at 7; the body was fetched at 5 — someone edited in between.
    mockGet.mockResolvedValueOnce(pageResponse(7));

    const out = await updateConfluencePageTool.handler({
      pageId: "2923724969",
      adfBody: bodyWithAnchor(),
      expectedVersion: 5,
      dryRun: false,
    });

    expect(out).toContain("Refusing to overwrite");
    expect(out).toContain("version 7");
    expect(out).toContain("fetched at version 5");
    expect(mockPut).not.toHaveBeenCalled();
  });

  it("warns on a dry run when the page moved past expectedVersion", async () => {
    mockGet.mockResolvedValueOnce(pageResponse(7));

    const out = await updateConfluencePageTool.handler({
      pageId: "2923724969",
      adfBody: bodyWithAnchor(),
      expectedVersion: 5,
      dryRun: true,
    });

    expect(out).toContain("body fetched at 5, live is 7");
    expect(out).toContain("a live write would be refused");
    expect(mockPut).not.toHaveBeenCalled();
  });
});
