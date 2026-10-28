import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

const mockPost = vi.fn();
const mockGet = vi.fn();

vi.mock("axios", () => {
  const mockAxios: any = {
    create: vi.fn(() => ({
      post: mockPost,
      get: mockGet,
      interceptors: { response: { use: vi.fn() } },
    })),
  };
  return { default: mockAxios };
});

import linkIssuesTool, { resolveLinkDirection } from "./link-issues.js";
import { validateInput, LinkIssuesSchema } from "../utils/validation.js";

describe("resolveLinkDirection", () => {
  it("puts the blocker on inwardIssue for a Blocks link", () => {
    // Ground truth from the live PM project: the same Blocks link is reported
    // from PM-39203 as inwardIssue: PM-38796 ("is blocked by") and from
    // PM-38796 as outwardIssue: PM-39203 ("blocks"), so PM-38796 blocks
    // PM-39203. Creating it takes inwardIssue: blocker, outwardIssue: blocked.
    const resolved = resolveLinkDirection(
      validateInput(LinkIssuesSchema, {
        linkType: "Blocks",
        blockerKey: "PM-38796",
        blockedKey: "PM-39203",
      }),
    );

    expect(resolved).toEqual({
      typeName: "Blocks",
      inwardKey: "PM-38796",
      outwardKey: "PM-39203",
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

    expect(resolved.inwardKey).toBe("PM-1");
    expect(resolved.outwardKey).toBe("PM-2");
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
      inwardKey: "PM-10",
      outwardKey: "PM-11",
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
  const blocksType = {
    id: "10000",
    name: "Blocks",
    inward: "is blocked by",
    outward: "blocks",
  };
  const relatesType = {
    id: "10003",
    name: "Relates",
    inward: "relates to",
    outward: "relates to",
  };
  // An issue's `issuelinks` read-back, in the shape GET /issue/{key} returns.
  const issueLinksResponse = (...issuelinks: unknown[]) => ({
    data: {
      id: "1",
      key: "PM-1",
      self: "https://example",
      fields: { issuelinks },
    },
  });
  const linkedIssue = (key: string) => ({
    id: key.split("-")[1],
    key,
    self: `https://example/rest/api/3/issue/${key}`,
    fields: {
      summary: `Summary of ${key}`,
      status: { name: "To Do" },
      priority: { name: "Medium" },
      issuetype: { name: "Task" },
    },
  });

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

  it("shows the blocker on inwardIssue in the dry-run payload", async () => {
    const out = await linkIssuesTool.handler({ ...blocksLink, dryRun: true });
    const payload = JSON.parse(out.split("```json\n")[1].split("\n```")[0]);

    expect(out).toContain("Reads as: **PM-1 blocks PM-2**");
    expect(payload).toEqual({
      type: { name: "Blocks" },
      inwardIssue: { key: "PM-1" },
      outwardIssue: { key: "PM-2" },
    });
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

  it("posts the blocker as inwardIssue and verifies by reading the blocker back", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockResolvedValueOnce({ data: undefined });
    // The blocker's own record names the blocked item as outwardIssue,
    // labelled by type.outward: "PM-1 blocks PM-2".
    mockGet.mockResolvedValueOnce(
      issueLinksResponse({
        id: "10001",
        self: "https://example/rest/api/3/issueLink/10001",
        type: blocksType,
        outwardIssue: linkedIssue("PM-2"),
      }),
    );

    const out = await linkIssuesTool.handler({
      ...blocksLink,
      dryRun: false,
    });

    expect(out).toContain("Linked: PM-1 blocks PM-2");
    expect(out).toContain("Verified: reading PM-1 back shows it blocks PM-2");
    expect(mockPost).toHaveBeenCalledOnce();
    expect(mockPost).toHaveBeenCalledWith("/rest/api/3/issueLink", {
      type: { name: "Blocks" },
      inwardIssue: { key: "PM-1" },
      outwardIssue: { key: "PM-2" },
    });
    expect(mockGet).toHaveBeenCalledWith(
      "/rest/api/3/issue/PM-1",
      expect.objectContaining({ params: { fields: "issuelinks" } }),
    );
  });

  it("reports a link that landed inverted instead of verifying it", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockResolvedValueOnce({ data: undefined });
    // The blocker's record names the blocked item as inwardIssue, labelled
    // "is blocked by": "PM-1 is blocked by PM-2", the reverse of the request.
    mockGet.mockResolvedValueOnce(
      issueLinksResponse({
        id: "88495",
        self: "https://example/rest/api/3/issueLink/88495",
        type: blocksType,
        inwardIssue: linkedIssue("PM-2"),
      }),
    );

    const out = await linkIssuesTool.handler({
      ...blocksLink,
      dryRun: false,
    });

    expect(out).toContain("Created inverted");
    expect(out).toContain("link 88495 as PM-2 blocks PM-1");
    expect(out).not.toContain("Verified");
    expect(out).not.toContain("Could not verify");
  });

  it("does not count a link of another type as verification", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockResolvedValueOnce({ data: undefined });
    mockGet.mockResolvedValueOnce(
      issueLinksResponse({
        id: "10002",
        self: "https://example/rest/api/3/issueLink/10002",
        type: relatesType,
        outwardIssue: linkedIssue("PM-2"),
      }),
    );

    const out = await linkIssuesTool.handler({
      ...blocksLink,
      dryRun: false,
    });

    expect(out).toContain("Could not verify");
    expect(out).not.toContain("Verified");
  });

  it.each([
    ["outwardIssue", { outwardIssue: linkedIssue("PM-11") }],
    ["inwardIssue", { inwardIssue: linkedIssue("PM-11") }],
  ])(
    "verifies a Relates link whichever side the read-back names (%s)",
    async (_side, end) => {
      process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
      mockPost.mockResolvedValueOnce({ data: undefined });
      mockGet.mockResolvedValueOnce(
        issueLinksResponse({
          id: "10003",
          self: "https://example/rest/api/3/issueLink/10003",
          type: relatesType,
          ...end,
        }),
      );

      const out = await linkIssuesTool.handler({
        linkType: "Relates",
        firstKey: "PM-10",
        secondKey: "PM-11",
        dryRun: false,
      });

      expect(out).toContain("Linked: PM-10 relates to PM-11");
      expect(out).toContain(
        "Verified: reading PM-10 back shows it relates to PM-11",
      );
      expect(mockGet).toHaveBeenCalledWith(
        "/rest/api/3/issue/PM-10",
        expect.objectContaining({ params: { fields: "issuelinks" } }),
      );
    },
  );

  it("reports when the read-back does not show the expected link", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockResolvedValueOnce({ data: undefined });
    mockGet.mockResolvedValueOnce(issueLinksResponse());

    const out = await linkIssuesTool.handler({
      ...blocksLink,
      dryRun: false,
    });

    expect(out).toContain("Linked: PM-1 blocks PM-2");
    expect(out).toContain("Could not verify");
    expect(out).toContain("Linked Issues panel");
  });

  it("reports a verification failure without treating the link creation as failed", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockResolvedValueOnce({ data: undefined });
    mockGet.mockRejectedValueOnce(new Error("JIRA API error (404): not found"));

    const out = await linkIssuesTool.handler({
      ...blocksLink,
      dryRun: false,
    });

    expect(out).toContain("Linked: PM-1 blocks PM-2");
    expect(out).toContain("Could not verify the link by reading PM-1 back");
    expect(out).toContain("not found");
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
    expect(out).not.toContain("full scope");
    expect(mockGet).not.toHaveBeenCalled();
  });

  it("hints at partial write-token scopes on a 401", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockRejectedValueOnce(
      new Error("JIRA authentication failed. Check your API token and email."),
    );

    const out = await linkIssuesTool.handler({
      ...blocksLink,
      dryRun: false,
    });

    expect(out).toContain("Error creating link");
    expect(out).toContain("full scope");
    expect(mockGet).not.toHaveBeenCalled();
  });
});
