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

import createIssueTool, { buildCreateFields } from "./create-issue.js";
import {
  validateInput,
  CreateIssueSchema,
  RESERVED_FIELD_KEYS,
} from "../utils/validation.js";

function fields(input: Record<string, unknown>) {
  return buildCreateFields(validateInput(CreateIssueSchema, input));
}

const story = {
  project: "PM",
  issueType: "Story",
  summary: "Add CSV export to the item list (web)",
};

describe("buildCreateFields", () => {
  it("sends only the common core when nothing else is supplied", () => {
    expect(fields(story)).toEqual({
      project: { key: "PM" },
      issuetype: { name: "Story" },
      summary: "Add CSV export to the item list (web)",
    });
  });

  it("passes an arbitrary field id through untouched", () => {
    // customfield_10192 is PM and SM's Acceptance criteria field. The tool does
    // not know that; the caller discovers it via get_create_fields.
    const result = fields({
      ...story,
      fields: { customfield_10192: "Given X When Y Then Z" },
    });

    expect(result.customfield_10192).toBe("Given X When Y Then Z");
  });

  it("passes structured option fields through untouched", () => {
    const result = fields({
      project: "PM",
      issueType: "Epic",
      summary: "Data export capability",
      fields: {
        customfield_11518: { value: "Internal" },
        customfield_11519: { value: "Tech debt" },
      },
    });

    expect(result.customfield_11518).toEqual({ value: "Internal" });
    expect(result.customfield_11519).toEqual({ value: "Tech debt" });
  });

  it("accepts an issue type no other project has", () => {
    // PLT's only creatable type. An enum of PM's types would reject this.
    const result = fields({
      project: "PLT",
      issueType: "Platform Initiative",
      summary: "Adopt the new telemetry pipeline",
    });

    expect(result.issuetype).toEqual({ name: "Platform Initiative" });
    expect(result.project).toEqual({ key: "PLT" });
  });

  it("builds description ADF from paragraphs", () => {
    const result = fields({
      ...story,
      descriptionParagraphs: ["First.", "Second."],
    });

    expect(result.description).toMatchObject({ version: 1, type: "doc" });
  });

  it("omits description entirely when no paragraphs are supplied", () => {
    expect(fields(story)).not.toHaveProperty("description");
  });

  it("sets parent as a key reference", () => {
    expect(fields({ ...story, parentKey: "PM-12345" }).parent).toEqual({
      key: "PM-12345",
    });
  });

  it("omits labels rather than sending an empty array", () => {
    expect(fields(story)).not.toHaveProperty("labels");
    expect(fields({ ...story, labels: ["web"] }).labels).toEqual(["web"]);
  });
});

describe("CreateIssueSchema", () => {
  it("defaults dryRun to true so a forgotten flag previews instead of creating", () => {
    expect(validateInput(CreateIssueSchema, story).dryRun).toBe(true);
  });

  it("requires an explicit project, privileging none", () => {
    expect(() =>
      validateInput(CreateIssueSchema, {
        issueType: "Story",
        summary: "No project given",
      }),
    ).toThrow(/project/i);
  });

  it("rejects a project key that isn't a bare Jira key", () => {
    expect(() =>
      validateInput(CreateIssueSchema, {
        ...story,
        project: "../../../rest/api/3/user/search",
      }),
    ).toThrow(/project key/i);
  });

  it("does not constrain issue type to any project's list", () => {
    expect(() =>
      validateInput(CreateIssueSchema, {
        project: "VULN",
        issueType: "Security",
        summary: "Remediate the reported finding",
      }),
    ).not.toThrow();
  });

  it.each(RESERVED_FIELD_KEYS)(
    "rejects reserved key %s inside fields",
    (key) => {
      expect(() =>
        validateInput(CreateIssueSchema, {
          ...story,
          fields: { [key]: "anything" },
        }),
      ).toThrow(/named parameters/);
    },
  );

  it("rejects a summary over Jira's 255 character limit", () => {
    expect(() =>
      validateInput(CreateIssueSchema, { ...story, summary: "x".repeat(256) }),
    ).toThrow(/255/);
  });

  it("rejects a malformed parent key", () => {
    expect(() =>
      validateInput(CreateIssueSchema, { ...story, parentKey: "pm-1" }),
    ).toThrow(/valid Jira issue key/);
  });
});

describe("create_issue handler", () => {
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

    const out = await createIssueTool.handler({ ...story, dryRun: true });

    expect(out).toContain("Dry run: create Story in PM");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("refuses a live create when no write token is set", async () => {
    const out = await createIssueTool.handler({ ...story, dryRun: false });

    expect(out).toContain("Refusing to create");
    expect(out).toContain("ATLASSIAN_JIRA_WRITE_TOKEN");
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("posts the previewed payload on a live create with a write token", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockResolvedValueOnce({
      data: { id: "140050", key: "AI-60", self: "https://example" },
    });

    const out = await createIssueTool.handler({ ...story, dryRun: false });

    expect(out).toContain("Created **AI-60**");
    expect(mockPost).toHaveBeenCalledOnce();
    expect(mockPost).toHaveBeenCalledWith("/rest/api/3/issue", {
      fields: fields(story),
    });
  });

  it("reports the API error rather than throwing on a failed live create", async () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";
    mockPost.mockRejectedValueOnce(new Error("JIRA API error (400): boom"));

    const out = await createIssueTool.handler({ ...story, dryRun: false });

    expect(out).toContain("Error creating issue");
    expect(out).toContain("boom");
  });
});
