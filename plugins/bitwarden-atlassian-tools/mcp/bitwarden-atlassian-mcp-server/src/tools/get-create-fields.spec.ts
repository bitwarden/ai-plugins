import { describe, it, expect, vi, beforeEach } from "vitest";

/**
 * The tool constructs a JiraClient, whose constructor reads env via
 * loadJiraConfig(), so auth and axios are both mocked.
 */
const mockGet = vi.fn();

vi.mock("axios", () => {
  const mockAxios: any = {
    create: vi.fn(() => ({
      get: mockGet,
      post: vi.fn(),
      interceptors: { response: { use: vi.fn() } },
    })),
  };
  return { default: mockAxios };
});

vi.mock("../jira/auth.js", () => ({
  loadJiraConfig: () => ({
    cloudId: "test-cloud-id",
    gatewayBaseUrl: "https://api.atlassian.com/ex/jira/test-cloud-id",
    email: "user@example.com",
    apiToken: "read-token",
  }),
  getJiraHeaders: () => ({ Accept: "application/json" }),
  hasJiraWriteToken: () => false,
}));

const { default: getCreateFields } = await import("./get-create-fields.js");

const PM_TYPES = {
  data: {
    issueTypes: [
      { id: "10027", name: "Story", subtask: false },
      { id: "10000", name: "Epic", subtask: false },
      { id: "10177", name: "Subtask", subtask: true },
    ],
  },
};

describe("get_create_fields", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("lists creatable types when no issueType is given", async () => {
    mockGet.mockResolvedValueOnce(PM_TYPES);

    const out = await getCreateFields.handler({ project: "PM" });

    expect(out).toContain("Creatable issue types in PM");
    expect(out).toContain("**Story** (id 10027)");
    expect(out).toContain("Sub-task types:");
    expect(mockGet).toHaveBeenCalledOnce();
  });

  it("reports the available types when the requested one does not exist", async () => {
    mockGet.mockResolvedValueOnce(PM_TYPES);

    const out = await getCreateFields.handler({
      project: "PM",
      issueType: "Platform Initiative",
    });

    expect(out).toContain('has no issue type named "Platform Initiative"');
    expect(out).toContain("- Story");
    // Should not have gone on to fetch fields.
    expect(mockGet).toHaveBeenCalledOnce();
  });

  it("matches the issue type name case-insensitively", async () => {
    mockGet.mockResolvedValueOnce(PM_TYPES).mockResolvedValueOnce({
      data: { fields: [] },
    });

    const out = await getCreateFields.handler({
      project: "PM",
      issueType: "story",
    });

    expect(out).toContain("PM / Story create screen");
  });

  it("separates required from optional and surfaces allowed values", async () => {
    mockGet.mockResolvedValueOnce(PM_TYPES).mockResolvedValueOnce({
      data: {
        fields: [
          {
            fieldId: "customfield_11519",
            name: "Business Driver",
            required: true,
            hasDefaultValue: false,
            schema: { type: "option" },
            allowedValues: [{ value: "Tech debt" }, { value: "Architecture" }],
          },
          {
            fieldId: "customfield_10192",
            name: "Acceptance criteria",
            required: false,
            schema: { type: "string" },
          },
        ],
      },
    });

    const out = await getCreateFields.handler({
      project: "PM",
      issueType: "Epic",
    });

    expect(out).toContain("## Required");
    expect(out).toContain("`customfield_11519` **Business Driver**");
    expect(out).toContain("allowed: Tech debt, Architecture");
    expect(out).toContain("## Optional");
    expect(out).toContain("`customfield_10192` **Acceptance criteria**");
  });

  it("does not mangle a field name with 'type' surrounded by spaces", async () => {
    mockGet.mockResolvedValueOnce(PM_TYPES).mockResolvedValueOnce({
      data: {
        fields: [
          {
            fieldId: "customfield_10300",
            name: "Issue type detail",
            required: false,
            schema: { type: "string" },
          },
        ],
      },
    });

    const out = await getCreateFields.handler({
      project: "PM",
      issueType: "Epic",
    });

    expect(out).toContain(
      "`customfield_10300` **Issue type detail** (optional, type string)",
    );
  });

  it("explains a project the user cannot create in rather than throwing", async () => {
    mockGet.mockRejectedValueOnce(
      new Error("JIRA resource not found: /rest/api/3/issue/createmeta/ARCH"),
    );

    const out = await getCreateFields.handler({ project: "ARCH" });

    expect(out).toContain("Cannot read the create screen for ARCH");
    expect(out).toContain("cannot create issues in this project");
  });

  it("handles a project reporting no creatable types", async () => {
    mockGet.mockResolvedValueOnce({ data: { issueTypes: [] } });

    const out = await getCreateFields.handler({ project: "TES" });

    expect(out).toContain("no creatable issue types");
  });

  it("rejects a project key that isn't a bare Jira key, without ever calling the API", async () => {
    await expect(
      getCreateFields.handler({
        project: "../../../rest/api/3/user/search",
      }),
    ).rejects.toThrow(/project key/i);

    expect(mockGet).not.toHaveBeenCalled();
  });
});
