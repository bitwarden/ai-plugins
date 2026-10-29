import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

const mockGet = vi.fn();
const mockPost = vi.fn();

vi.mock("axios", () => {
  const mockAxios: any = {
    create: vi.fn(() => ({
      get: mockGet,
      post: mockPost,
      interceptors: { response: { use: vi.fn() } },
    })),
  };
  return { default: mockAxios };
});

import createConfluencePageTool, {
  buildCreatePagePayload,
} from "./create-confluence-page.js";
import {
  validateInput,
  CreateConfluencePageSchema,
} from "../utils/validation.js";

const draft = {
  spaceId: "98765",
  title: "SHOT-315 spike summary",
  body: "## Summary\n\n- **One** item\n- [docs](https://example.test/docs)",
};
const expectedStorage =
  "<h2>Summary</h2>\n<ul><li><strong>One</strong> item</li>" +
  '<li><a href="https://example.test/docs">docs</a></li></ul>';

/** `GET /wiki/api/v2/spaces/{id}` */
const spaceResponse = {
  data: {
    id: "98765",
    key: "~kh",
    name: "Sam Example",
    type: "personal",
    status: "current",
    homepageId: "5000",
  },
};

/** `GET /wiki/api/v2/pages/{id}?get-draft=true`, or the create response. */
function draftResponse(overrides: Record<string, unknown> = {}) {
  return {
    data: {
      id: "111",
      status: "draft",
      title: draft.title,
      spaceId: "98765",
      parentId: "5000",
      parentType: "page",
      authorId: "557058:abc",
      createdAt: "2026-10-29T09:00:00.000Z",
      version: { number: 1, message: "", minorEdit: false },
      body: { storage: { representation: "storage", value: expectedStorage } },
      _links: {
        webui: "/spaces/~kh/pages/111/SHOT-315",
        editui: "/pages/edit-v2/111",
        tinyui: "/x/AbCd",
        base: "https://example.atlassian.net/wiki",
      },
      ...overrides,
    },
  };
}

describe("CreateConfluencePageSchema", () => {
  it("defaults to a dry run", () => {
    expect(validateInput(CreateConfluencePageSchema, draft).dryRun).toBe(true);
  });

  it("rejects non-numeric ids, which end up in REST paths", () => {
    expect(() =>
      validateInput(CreateConfluencePageSchema, { ...draft, spaceId: "~kh" }),
    ).toThrow(/numeric Confluence space id/);
    expect(() =>
      validateInput(CreateConfluencePageSchema, {
        ...draft,
        parentId: "1/../2",
      }),
    ).toThrow(/numeric Confluence page id/);
  });

  it("rejects an empty body", () => {
    expect(() =>
      validateInput(CreateConfluencePageSchema, { ...draft, body: "  " }),
    ).toThrow(/Body cannot be empty/);
  });
});

describe("buildCreatePagePayload", () => {
  it("always creates a draft, and omits an absent parent", () => {
    const input = validateInput(CreateConfluencePageSchema, draft);

    expect(buildCreatePagePayload(input, "<p>x</p>")).toEqual({
      spaceId: "98765",
      status: "draft",
      title: draft.title,
      body: { representation: "storage", value: "<p>x</p>" },
    });
  });

  it("includes the parent when given", () => {
    const input = validateInput(CreateConfluencePageSchema, {
      ...draft,
      parentId: "4242",
    });

    expect(buildCreatePagePayload(input, "<p>x</p>").parentId).toBe("4242");
  });
});

describe("create_confluence_page handler", () => {
  const ENV_KEYS = [
    "ATLASSIAN_CLOUD_ID",
    "ATLASSIAN_EMAIL",
    "ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN",
    "ATLASSIAN_CONFLUENCE_WRITE_TOKEN",
    "ATLASSIAN_JIRA_WRITE_TOKEN",
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
      if (saved[key] === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = saved[key];
      }
    }
  });

  it("names the space and returns the exact request on a dry run, writing nothing", async () => {
    mockGet.mockResolvedValueOnce(spaceResponse);

    const out = await createConfluencePageTool.handler(draft);

    expect(out).toContain(
      '# Dry run: create Confluence draft "SHOT-315 spike summary"',
    );
    expect(out).toContain("POST /wiki/api/v2/pages");
    expect(out).toContain('"status": "draft"');
    expect(out).toContain(JSON.stringify(expectedStorage));
    expect(out).toContain("ATLASSIAN_CONFLUENCE_WRITE_TOKEN is not set");
    expect(out).toContain("- **Space:** Sam Example (~kh, id 98765)");
    expect(out).toContain("Confirm the space below with the user");
    expect(mockGet).toHaveBeenCalledWith("/wiki/api/v2/spaces/98765");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("tells the caller to ask the user when the space id matches no space", async () => {
    mockGet.mockRejectedValueOnce(
      new Error("Confluence resource not found: /wiki/api/v2/spaces/98765"),
    );

    const out = await createConfluencePageTool.handler(draft);

    expect(out).toContain("No Confluence space with id 98765 could be read");
    expect(out).toContain("Ask the user which space");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("lists links the conversion dropped", async () => {
    mockGet.mockResolvedValueOnce(spaceResponse);
    const out = await createConfluencePageTool.handler({
      ...draft,
      body: "See [README](README.md).",
    });

    expect(out).toContain("## Conversion notes");
    expect(out).toContain(
      'Link "README" (README.md) was rendered as plain text',
    );
  });

  it("refuses a live create without the Confluence write token, even with the Jira one", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "jira-write-token";

    const out = await createConfluencePageTool.handler({
      ...draft,
      dryRun: false,
    });

    expect(out).toContain("Refusing to create");
    expect(out).toContain("ATLASSIAN_CONFLUENCE_WRITE_TOKEN");
    expect(mockGet).not.toHaveBeenCalled();
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("creates the draft and verifies it by reading the draft back", async () => {
    process.env.ATLASSIAN_CONFLUENCE_WRITE_TOKEN = "write-token";
    mockGet.mockResolvedValueOnce(spaceResponse);
    mockPost.mockResolvedValueOnce(draftResponse());
    mockGet.mockResolvedValueOnce(draftResponse());

    const out = await createConfluencePageTool.handler({
      ...draft,
      parentId: "4242",
      dryRun: false,
    });

    expect(mockPost).toHaveBeenCalledWith("/wiki/api/v2/pages", {
      spaceId: "98765",
      status: "draft",
      title: draft.title,
      parentId: "4242",
      body: { representation: "storage", value: expectedStorage },
    });
    expect(mockGet).toHaveBeenCalledWith("/wiki/api/v2/pages/111", {
      params: { "body-format": "storage", "get-draft": true },
    });
    expect(out).toContain("Created draft **SHOT-315 spike summary** (id 111).");
    expect(out).toContain("- Space: Sam Example (~kh, id 98765)");
    expect(out).toContain(
      "- Link: https://example.atlassian.net/wiki/pages/edit-v2/111",
    );
    expect(out).toContain(
      "Verified: reading page 111 back shows an unpublished draft",
    );
  });

  it("verifies through the markup Confluence normalizes on save", async () => {
    process.env.ATLASSIAN_CONFLUENCE_WRITE_TOKEN = "write-token";
    mockGet.mockResolvedValueOnce(spaceResponse);
    mockPost.mockResolvedValueOnce(draftResponse());
    mockGet.mockResolvedValueOnce(
      draftResponse({
        body: {
          storage: {
            representation: "storage",
            value:
              '<h2 local-id="a1">Summary</h2><ul><li><p><strong>One</strong> item</p></li>' +
              '<li><p><a href="https://example.test/docs">docs</a></p></li></ul>',
          },
        },
      }),
    );

    const out = await createConfluencePageTool.handler({
      ...draft,
      dryRun: false,
    });

    expect(out).toContain("Verified");
  });

  it("reports a read-back that does not match what was sent", async () => {
    process.env.ATLASSIAN_CONFLUENCE_WRITE_TOKEN = "write-token";
    mockGet.mockResolvedValueOnce(spaceResponse);
    mockPost.mockResolvedValueOnce(draftResponse());
    mockGet.mockResolvedValueOnce(
      draftResponse({
        status: "current",
        body: { storage: { representation: "storage", value: "<p>Other</p>" } },
      }),
    );

    const out = await createConfluencePageTool.handler({
      ...draft,
      dryRun: false,
    });

    expect(out).toContain("Created draft");
    expect(out).toContain(
      'Could not verify: reading page 111 back shows that the status is "current"',
    );
    expect(out).toContain("the body text differs from what was sent");
    expect(out).not.toContain("Verified:");
  });

  it("reports a failed read-back without treating the create as failed", async () => {
    process.env.ATLASSIAN_CONFLUENCE_WRITE_TOKEN = "write-token";
    mockGet.mockResolvedValueOnce(spaceResponse);
    mockPost.mockResolvedValueOnce(draftResponse());
    mockGet.mockRejectedValueOnce(new Error("Confluence resource not found"));

    const out = await createConfluencePageTool.handler({
      ...draft,
      dryRun: false,
    });

    expect(out).toContain("Created draft");
    expect(out).toContain("Could not verify the draft by reading 111 back");
  });

  it("reports the API error rather than throwing on a failed create", async () => {
    process.env.ATLASSIAN_CONFLUENCE_WRITE_TOKEN = "write-token";
    mockGet.mockResolvedValueOnce(spaceResponse);
    mockPost.mockRejectedValueOnce(
      new Error(
        "Confluence authentication failed. Check your API token and email.",
      ),
    );

    const out = await createConfluencePageTool.handler({
      ...draft,
      dryRun: false,
    });

    expect(out).toContain(
      "Error creating draft: Confluence authentication failed",
    );
    expect(mockGet).toHaveBeenCalledTimes(1);
  });
});
