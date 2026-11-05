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

import transitionIssueTool from "./transition-issue.js";
import { validateInput, TransitionIssueSchema } from "../utils/validation.js";

function statusResponse(name: string) {
  return { data: { key: "AI-27", fields: { status: { name } } } };
}

const transitionsResponse = {
  data: {
    transitions: [
      { id: "11", name: "Start Progress", to: { name: "In Progress" } },
      { id: "31", name: "Resolve", to: { name: "Done" } },
      { id: "32", name: "Close", to: { name: "Done" } },
    ],
  },
};

describe("TransitionIssueSchema", () => {
  it("defaults dryRun to true", () => {
    const parsed = validateInput(TransitionIssueSchema, {
      issueIdOrKey: "AI-27",
      status: "Done",
    });

    expect(parsed.dryRun).toBe(true);
  });

  it("rejects a whitespace-only status", () => {
    expect(() =>
      validateInput(TransitionIssueSchema, {
        issueIdOrKey: "AI-27",
        status: "   ",
      }),
    ).toThrow(/Target status cannot be empty/);
  });

  it("rejects a malformed issue key", () => {
    expect(() =>
      validateInput(TransitionIssueSchema, {
        issueIdOrKey: "AI-27/../../myself",
        status: "Done",
      }),
    ).toThrow(/valid Jira issue key/);
  });
});

describe("transition_issue handler", () => {
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

  it("is a no-op when the issue is already in the target status", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockGet.mockResolvedValueOnce(statusResponse("Done"));

    const out = await transitionIssueTool.handler({
      issueIdOrKey: "AI-27",
      status: "done",
      dryRun: false,
    });

    expect(out).toContain("AI-27 is already in Done");
    expect(mockGet).toHaveBeenCalledTimes(1);
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("reports reachable statuses when no transition leads to the target", async () => {
    mockGet
      .mockResolvedValueOnce(statusResponse("To Do"))
      .mockResolvedValueOnce(transitionsResponse);

    const out = await transitionIssueTool.handler({
      issueIdOrKey: "AI-27",
      status: "In Review",
    });

    expect(out).toContain("No transition from To Do to In Review");
    expect(out).toContain("Statuses reachable from To Do: In Progress, Done.");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("previews the matching transition on a dry run without posting", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockGet
      .mockResolvedValueOnce(statusResponse("To Do"))
      .mockResolvedValueOnce(transitionsResponse);

    const out = await transitionIssueTool.handler({
      issueIdOrKey: "AI-27",
      status: "in progress",
    });

    expect(out).toContain("Dry run: transition AI-27");
    expect(out).toContain("**To Do** -> **In Progress**");
    expect(out).toContain('"id": "11"');
    expect(out).not.toContain("ATLASSIAN_JIRA_WRITE_TOKEN is not set");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("notes the missing write token on a dry run from a read-only install", async () => {
    mockGet
      .mockResolvedValueOnce(statusResponse("To Do"))
      .mockResolvedValueOnce(transitionsResponse);

    const out = await transitionIssueTool.handler({
      issueIdOrKey: "AI-27",
      status: "Done",
    });

    expect(out).toContain("ATLASSIAN_JIRA_WRITE_TOKEN is not set");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("refuses a live transition when no write token is set", async () => {
    mockGet
      .mockResolvedValueOnce(statusResponse("To Do"))
      .mockResolvedValueOnce(transitionsResponse);

    const out = await transitionIssueTool.handler({
      issueIdOrKey: "AI-27",
      status: "Done",
      dryRun: false,
    });

    expect(out).toContain("Refusing to transition");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("posts the first matching transition and verifies the new status", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockGet
      .mockResolvedValueOnce(statusResponse("To Do"))
      .mockResolvedValueOnce(transitionsResponse)
      .mockResolvedValueOnce(statusResponse("Done"));
    mockPost.mockResolvedValueOnce({ status: 204 });

    const out = await transitionIssueTool.handler({
      issueIdOrKey: "AI-27",
      status: "Done",
      dryRun: false,
    });

    expect(mockPost).toHaveBeenCalledWith(
      "/rest/api/3/issue/AI-27/transitions",
      { transition: { id: "31" } },
    );
    expect(out).toContain("Transitioned **AI-27**: To Do -> Done.");
    expect(out).toContain("Verified: reading AI-27 back shows status Done.");
  });

  it("flags a status that moved on after the transition", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockGet
      .mockResolvedValueOnce(statusResponse("To Do"))
      .mockResolvedValueOnce(transitionsResponse)
      .mockResolvedValueOnce(statusResponse("Closed"));
    mockPost.mockResolvedValueOnce({ status: 204 });

    const out = await transitionIssueTool.handler({
      issueIdOrKey: "AI-27",
      status: "Done",
      dryRun: false,
    });

    expect(out).toContain("Could not verify");
    expect(out).toContain("shows status Closed, not Done");
  });

  it("adds the scope hint when the live transition fails authentication", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockGet
      .mockResolvedValueOnce(statusResponse("To Do"))
      .mockResolvedValueOnce(transitionsResponse);
    mockPost.mockRejectedValueOnce(
      new Error("JIRA authentication failed. Check your API token and email."),
    );

    const out = await transitionIssueTool.handler({
      issueIdOrKey: "AI-27",
      status: "Done",
      dryRun: false,
    });

    expect(out).toContain("Error transitioning issue");
    expect(out).toContain("verify it carries the full scope");
  });
});
