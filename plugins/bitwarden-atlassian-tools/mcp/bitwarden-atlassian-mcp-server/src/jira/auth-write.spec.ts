import { describe, it, expect, beforeEach, afterEach } from "vitest";

import { loadJiraConfig, hasJiraWriteToken } from "./auth.js";

const ENV_KEYS = [
  "ATLASSIAN_CLOUD_ID",
  "ATLASSIAN_EMAIL",
  "ATLASSIAN_JIRA_READ_ONLY_TOKEN",
  "ATLASSIAN_JIRA_WRITE_TOKEN",
] as const;

describe("Jira write-token access mode", () => {
  const saved: Record<string, string | undefined> = {};

  beforeEach(() => {
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

  it("reports no write token on a read-only install", () => {
    expect(hasJiraWriteToken()).toBe(false);
  });

  it("still loads read config on a read-only install", () => {
    expect(loadJiraConfig().apiToken).toBe("read-token");
  });

  it("defaults to the read token when no mode is given", () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";

    expect(loadJiraConfig().apiToken).toBe("read-token");
  });

  it("uses the write token in write mode", () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "write-token";

    expect(hasJiraWriteToken()).toBe(true);
    expect(loadJiraConfig("write").apiToken).toBe("write-token");
  });

  it("throws naming the write variable when write mode has no token", () => {
    expect(() => loadJiraConfig("write")).toThrow(/ATLASSIAN_JIRA_WRITE_TOKEN/);
  });

  it("treats an unexpanded template placeholder as absent", () => {
    process.env.ATLASSIAN_JIRA_WRITE_TOKEN = "${ATLASSIAN_JIRA_WRITE_TOKEN}";

    expect(hasJiraWriteToken()).toBe(false);
  });
});
