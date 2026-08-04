/**
 * JIRA API Authentication Module
 * Handles Basic Auth with API tokens for JIRA Cloud
 */

import { JiraConfig } from "./types.js";

/**
 * Resolve an environment variable, treating unexpanded template strings
 * (e.g. literal "${VAR_NAME}") as undefined so validation catches missing vars.
 */
function resolveEnv(name: string): string | undefined {
  const value = process.env[name];
  if (!value || /^\$\{.+\}$/.test(value)) {
    return undefined;
  }
  return value;
}

/**
 * Access mode for a Jira client.
 *
 * "read" uses ATLASSIAN_JIRA_READ_ONLY_TOKEN, which every install already sets.
 * "write" uses ATLASSIAN_JIRA_WRITE_TOKEN, which is optional: when it is absent
 * the server exposes exactly the read-only surface it always has, and the write
 * tools refuse to execute. Write capability is therefore opt-in per install
 * rather than shipped to everyone.
 */
export type JiraAccessMode = "read" | "write";

const TOKEN_ENV_VAR: Record<JiraAccessMode, string> = {
  read: "ATLASSIAN_JIRA_READ_ONLY_TOKEN",
  write: "ATLASSIAN_JIRA_WRITE_TOKEN",
};

/**
 * Whether this install has been given a write-capable Jira token.
 */
export function hasJiraWriteToken(): boolean {
  return resolveEnv(TOKEN_ENV_VAR.write) !== undefined;
}

/**
 * Load JIRA configuration from environment variables
 * @param mode - Which token to authenticate with. Defaults to read-only.
 * @throws {Error} If required environment variables are missing
 */
export function loadJiraConfig(mode: JiraAccessMode = "read"): JiraConfig {
  const cloudId = resolveEnv("ATLASSIAN_CLOUD_ID");
  const email = resolveEnv("ATLASSIAN_EMAIL");
  const tokenVar = TOKEN_ENV_VAR[mode];
  const apiToken = resolveEnv(tokenVar);

  if (!cloudId || !email || !apiToken) {
    throw new Error(
      "Missing required JIRA environment variables. " +
        `Please set ATLASSIAN_CLOUD_ID, ATLASSIAN_EMAIL, and ${tokenVar}`,
    );
  }

  const gatewayBaseUrl = `https://api.atlassian.com/ex/jira/${cloudId}`;

  return {
    cloudId,
    gatewayBaseUrl,
    email,
    apiToken,
  };
}

/**
 * Generate Basic Auth header for JIRA API requests
 * JIRA Cloud uses email:api_token encoded as Base64
 */
export function getAuthHeader(config: JiraConfig): string {
  const credentials = `${config.email}:${config.apiToken}`;
  const base64Credentials = Buffer.from(credentials).toString("base64");
  return `Basic ${base64Credentials}`;
}

/**
 * Get common headers for JIRA API requests
 */
export function getJiraHeaders(config: JiraConfig): Record<string, string> {
  return {
    Authorization: getAuthHeader(config),
    Accept: "application/json",
    "Content-Type": "application/json",
  };
}
