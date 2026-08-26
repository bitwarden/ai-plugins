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

import addCommentTool from "./add-comment.js";
import { validateInput, AddCommentSchema } from "../utils/validation.js";

describe("AddCommentSchema", () => {
  it("defaults dryRun to true", () => {
    const parsed = validateInput(AddCommentSchema, {
      issueIdOrKey: "AI-27",
      body: "Looks good.",
    });

    expect(parsed.dryRun).toBe(true);
  });

  it("rejects an empty body", () => {
    expect(() =>
      validateInput(AddCommentSchema, { issueIdOrKey: "AI-27", body: "" }),
    ).toThrow(/Comment body cannot be empty/);
  });

  it("rejects a whitespace-only body", () => {
    expect(() =>
      validateInput(AddCommentSchema, {
        issueIdOrKey: "AI-27",
        body: "   \n\t  ",
      }),
    ).toThrow(/Comment body cannot be empty/);
  });

  it("rejects a malformed issue key", () => {
    expect(() =>
      validateInput(AddCommentSchema, { issueIdOrKey: "ai-27", body: "hi" }),
    ).toThrow(/valid Jira issue key/);
  });
});

describe("add_comment handler", () => {
  const ENV_KEYS = [
    "ATLASSIAN_CLOUD_ID",
    "ATLASSIAN_EMAIL",
    "ATLASSIAN_JIRA_READ_ONLY_TOKEN",
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

    const out = await addCommentTool.handler({
      issueIdOrKey: "AI-27",
      body: "Looks good.",
      dryRun: true,
    });

    expect(out).toContain("Dry run: add comment to AI-27");
    expect(out).toContain("Looks good.");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("refuses a live comment when no write token is set", async () => {
    const out = await addCommentTool.handler({
      issueIdOrKey: "AI-27",
      body: "Looks good.",
      dryRun: false,
    });

    expect(out).toContain("Refusing to comment");
    expect(out).toContain("ATLASSIAN_JIRA_WRITE_TOKEN");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("posts the comment body as ADF and reports the created comment", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockResolvedValueOnce({
      data: { id: "10050", created: "2026-08-26T12:00:00.000Z" },
    });

    const out = await addCommentTool.handler({
      issueIdOrKey: "AI-27",
      body: "Looks good.",
      dryRun: false,
    });

    expect(out).toContain("Added comment to **AI-27**");
    expect(out).toContain("Comment id: 10050");
    expect(mockPost).toHaveBeenCalledWith("/rest/api/3/issue/AI-27/comment", {
      body: {
        version: 1,
        type: "doc",
        content: [
          {
            type: "paragraph",
            content: [{ type: "text", text: "Looks good." }],
          },
        ],
      },
    });
  });

  it("reports the API error rather than throwing on a failed live comment", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockRejectedValueOnce(new Error("JIRA API error (400): boom"));

    const out = await addCommentTool.handler({
      issueIdOrKey: "AI-27",
      body: "Looks good.",
      dryRun: false,
    });

    expect(out).toContain("Error adding comment");
    expect(out).toContain("boom");
    expect(out).not.toContain("full scope");
  });

  it("hints at partial write-token scopes on a 401", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockRejectedValueOnce(
      new Error("JIRA authentication failed. Check your API token and email."),
    );

    const out = await addCommentTool.handler({
      issueIdOrKey: "AI-27",
      body: "Looks good.",
      dryRun: false,
    });

    expect(out).toContain("Error adding comment");
    expect(out).toContain("full scope");
  });
});
