import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

const mockPost = vi.fn();

vi.mock("axios", () => {
  const mockAxios: any = {
    create: vi.fn(() => ({
      post: mockPost,
      interceptors: { response: { use: vi.fn() } },
    })),
  };
  return { default: mockAxios };
});

import linkIssuesTool, { resolveLinkDirection } from "./link-issues.js";
import { validateInput, LinkIssuesSchema } from "../utils/validation.js";

describe("resolveLinkDirection", () => {
  it("puts the blocker on outwardIssue for a Blocks link", () => {
    // Ground truth, verified read-only against the live PM project: the same
    // Blocks link is reported from PM-39203 as inwardIssue: PM-38796 and from
    // PM-38796 as outwardIssue: PM-39203, so outward is the blocker.
    const resolved = resolveLinkDirection(
      validateInput(LinkIssuesSchema, {
        linkType: "Blocks",
        blockerKey: "PM-39203",
        blockedKey: "PM-38796",
      }),
    );

    expect(resolved).toEqual({
      typeName: "Blocks",
      outwardKey: "PM-39203",
      inwardKey: "PM-38796",
    });
  });

  it("does not invert when the caller lists the blocked item first", () => {
    const resolved = resolveLinkDirection(
      validateInput(LinkIssuesSchema, {
        linkType: "Blocks",
        blockedKey: "PM-2",
        blockerKey: "PM-1",
      }),
    );

    expect(resolved.outwardKey).toBe("PM-1");
    expect(resolved.inwardKey).toBe("PM-2");
  });

  it("maps a symmetric Relates link in argument order", () => {
    const resolved = resolveLinkDirection(
      validateInput(LinkIssuesSchema, {
        linkType: "Relates",
        firstKey: "PM-10",
        secondKey: "PM-11",
      }),
    );

    expect(resolved).toEqual({
      typeName: "Relates",
      outwardKey: "PM-10",
      inwardKey: "PM-11",
    });
  });
});

describe("LinkIssuesSchema", () => {
  it("defaults dryRun to true", () => {
    const parsed = validateInput(LinkIssuesSchema, {
      linkType: "Blocks",
      blockerKey: "PM-1",
      blockedKey: "PM-2",
    });

    expect(parsed.dryRun).toBe(true);
  });

  it("rejects a Blocks link missing one end", () => {
    expect(() =>
      validateInput(LinkIssuesSchema, {
        linkType: "Blocks",
        blockerKey: "PM-1",
      }),
    ).toThrow(/blockedKey/);
  });

  it("rejects a malformed issue key", () => {
    expect(() =>
      validateInput(LinkIssuesSchema, {
        linkType: "Blocks",
        blockerKey: "pm-1",
        blockedKey: "PM-2",
      }),
    ).toThrow(/valid Jira issue key/);
  });
});

describe("link_issues handler", () => {
  const ENV_KEYS = [
    "ATLASSIAN_CLOUD_ID",
    "ATLASSIAN_EMAIL",
    "ATLASSIAN_JIRA_READ_ONLY_TOKEN",
    "ATLASSIAN_JIRA_WRITE_TOKEN",
  ] as const;
  const saved: Record<string, string | undefined> = {};
  const blocksLink = {
    linkType: "Blocks",
    blockerKey: "PM-1",
    blockedKey: "PM-2",
  };

  beforeEach(() => {
    vi.clearAllMocks();
    for (const key of ENV_KEYS) {
      saved[key] = process.env[key];
      delete process.env[key];
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

  it("sends no request on a dry run, even with a write token set", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";

    const out = await linkIssuesTool.handler({ ...blocksLink, dryRun: true });

    expect(out).toContain("Dry run: link Blocks");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("refuses a live link when no write token is set", async () => {
    const out = await linkIssuesTool.handler({
      ...blocksLink,
      dryRun: false,
    });

    expect(out).toContain("Refusing to link");
    expect(out).toContain("ATLASSIAN_JIRA_WRITE_TOKEN");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("posts the resolved link direction on a live link with a write token", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockResolvedValueOnce({ data: undefined });

    const out = await linkIssuesTool.handler({
      ...blocksLink,
      dryRun: false,
    });

    expect(out).toContain("Linked: PM-1 blocks PM-2");
    expect(mockPost).toHaveBeenCalledOnce();
    expect(mockPost).toHaveBeenCalledWith("/rest/api/3/issueLink", {
      type: { name: "Blocks" },
      outwardIssue: { key: "PM-1" },
      inwardIssue: { key: "PM-2" },
    });
  });

  it("reports the API error rather than throwing on a failed live link", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockRejectedValueOnce(new Error("JIRA API error (400): boom"));

    const out = await linkIssuesTool.handler({
      ...blocksLink,
      dryRun: false,
    });

    expect(out).toContain("Error creating link");
    expect(out).toContain("boom");
  });
});
