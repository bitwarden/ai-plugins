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

import getIssueTool from "./get-issue.js";

describe("get_issue issue links", () => {
  const ENV_KEYS = [
    "ATLASSIAN_CLOUD_ID",
    "ATLASSIAN_EMAIL",
    "ATLASSIAN_JIRA_READ_ONLY_TOKEN",
  ] as const;
  const saved: Record<string, string | undefined> = {};
  const blocksType = {
    name: "Blocks",
    inward: "is blocked by",
    outward: "blocks",
  };

  const mockIssue = (fields: Record<string, unknown>) =>
    mockGet.mockResolvedValueOnce({
      data: { key: "PM-1", fields: { summary: "Issue", ...fields } },
    });

  beforeEach(() => {
    vi.clearAllMocks();
    for (const key of ENV_KEYS) {
      saved[key] = process.env[key];
    }
    process.env.ATLASSIAN_CLOUD_ID = "test-cloud-id";
    process.env.ATLASSIAN_EMAIL = "user@example.com";
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = "read-token";
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

  it("renders an outward link with the outward phrase", async () => {
    mockIssue({
      issuelinks: [
        {
          type: blocksType,
          outwardIssue: {
            key: "PM-2",
            fields: { summary: "Blocked work", status: { name: "To Do" } },
          },
        },
      ],
    });

    const out = await getIssueTool.handler({ issueIdOrKey: "PM-1" });

    expect(out).toContain("## Issue Links");
    expect(out).toContain("- blocks **[PM-2]** Blocked work - To Do");
  });

  it("renders an inward link with the inward phrase", async () => {
    mockIssue({
      issuelinks: [
        {
          type: blocksType,
          inwardIssue: {
            key: "PM-3",
            fields: { summary: "Blocker", status: { name: "In Progress" } },
          },
        },
      ],
    });

    const out = await getIssueTool.handler({ issueIdOrKey: "PM-1" });

    expect(out).toContain("- is blocked by **[PM-3]** Blocker - In Progress");
  });

  it("renders no section when issuelinks is empty", async () => {
    mockIssue({ issuelinks: [] });

    const out = await getIssueTool.handler({ issueIdOrKey: "PM-1" });

    expect(out).not.toContain("## Issue Links");
  });

  it("renders no section when issuelinks is missing", async () => {
    mockIssue({});

    const out = await getIssueTool.handler({ issueIdOrKey: "PM-1" });

    expect(out).not.toContain("## Issue Links");
  });

  it("falls back to No summary and Unknown for a sparse linked issue", async () => {
    mockIssue({
      issuelinks: [{ type: blocksType, outwardIssue: { key: "PM-2" } }],
    });

    const out = await getIssueTool.handler({ issueIdOrKey: "PM-1" });

    expect(out).toContain("- blocks **[PM-2]** No summary - Unknown");
  });

  it("renders the links when only the issuelinks field is requested", async () => {
    mockIssue({
      issuelinks: [
        {
          type: blocksType,
          inwardIssue: {
            key: "PM-3",
            fields: { summary: "Blocker", status: { name: "Done" } },
          },
        },
      ],
    });

    const out = await getIssueTool.handler({
      issueIdOrKey: "PM-1",
      fields: ["issuelinks"],
    });

    expect(mockGet).toHaveBeenCalledWith(
      "/rest/api/3/issue/PM-1",
      expect.objectContaining({
        params: expect.objectContaining({ fields: "issuelinks" }),
      }),
    );
    expect(out).toContain("- is blocked by **[PM-3]** Blocker - Done");
  });
});
