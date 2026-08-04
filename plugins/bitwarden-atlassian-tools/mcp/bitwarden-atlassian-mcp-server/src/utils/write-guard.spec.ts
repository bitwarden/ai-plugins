import { describe, it, expect } from "vitest";

import {
  writeTokenDryRunNote,
  writeTokenRefusalMessage,
} from "./write-guard.js";

describe("writeTokenDryRunNote", () => {
  it("names the action in the no-token dry-run note", () => {
    const lines = writeTokenDryRunNote("create");

    expect(lines.join("\n")).toContain("create would fail");
    expect(lines.join("\n")).toContain("ATLASSIAN_JIRA_WRITE_TOKEN");
  });
});

describe("writeTokenRefusalMessage", () => {
  it("names the action in the live-refusal message", () => {
    const message = writeTokenRefusalMessage("link");

    expect(message).toContain("Refusing to link");
    expect(message).toContain("ATLASSIAN_JIRA_WRITE_TOKEN");
    expect(message).toContain("dryRun: true");
  });
});
