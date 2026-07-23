import { describe, it, expect } from "vitest";
import { formatIssue } from "./format-issue.js";

describe("formatIssue", () => {
  it("should render key, summary, and core fields", () => {
    const result = formatIssue({
      key: "PM-1",
      fields: {
        summary: "A bug",
        status: { name: "Open" },
        issuetype: { name: "Bug" },
        priority: { name: "High" },
        assignee: { displayName: "John" },
        reporter: { displayName: "Jane" },
        labels: ["frontend"],
      },
    });

    expect(result).toContain("**[PM-1]** A bug");
    expect(result).toContain("Status: Open");
    expect(result).toContain("Type: Bug");
    expect(result).toContain("Priority: High");
    expect(result).toContain("Assignee: John");
    expect(result).toContain("Reporter: Jane");
    expect(result).toContain("Labels: frontend");
  });

  it("should apply fallbacks when optional fields are absent", () => {
    const result = formatIssue({
      key: "PM-2",
      fields: { summary: "No metadata" },
    });

    expect(result).toContain("**[PM-2]** No metadata");
    expect(result).toContain("Status: Unknown");
    expect(result).toContain("Type: Unknown");
    expect(result).toContain("Priority: None");
    expect(result).toContain("Assignee: Unassigned");
    expect(result).toContain("Reporter: Unknown");
    expect(result).toContain("Labels: None");
  });

  it("should render 'No summary' when summary is missing", () => {
    const result = formatIssue({ key: "PM-3", fields: {} });
    expect(result).toContain("**[PM-3]** No summary");
  });
});
