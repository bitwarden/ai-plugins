/**
 * Confluence API Authentication Module
 * Handles Basic Auth with API tokens for Confluence Cloud
 * Uses the same Atlassian authentication as Jira
 */

import { ConfluenceConfig } from "./types.js";

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
 * Whether this install has the optional Confluence write token, which is used
 * only to create pages. The Jira write token is never used for Confluence.
 */
export function hasConfluenceWriteToken(): boolean {
  return resolveEnv("ATLASSIAN_CONFLUENCE_WRITE_TOKEN") !== undefined;
}

/**
 * Load Confluence configuration from environment variables
 * @param mode - "write" uses ATLASSIAN_CONFLUENCE_WRITE_TOKEN. Defaults to read-only.
 * @throws {Error} If required environment variables are missing
 */
export function loadConfluenceConfig(
  mode: "read" | "write" = "read",
): ConfluenceConfig {
  const cloudId = resolveEnv("ATLASSIAN_CLOUD_ID");
  const email = resolveEnv("ATLASSIAN_EMAIL");
  const tokenVar =
    mode === "write"
      ? "ATLASSIAN_CONFLUENCE_WRITE_TOKEN"
      : "ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN";
  const apiToken = resolveEnv(tokenVar);

  if (!cloudId || !email || !apiToken) {
    throw new Error(
      "Missing required Confluence environment variables. " +
        `Please set ATLASSIAN_CLOUD_ID, ATLASSIAN_EMAIL, and ${tokenVar}`,
    );
  }

  const gatewayBaseUrl = `https://api.atlassian.com/ex/confluence/${cloudId}`;

  return {
    cloudId,
    gatewayBaseUrl,
    email,
    apiToken,
  };
}

/**
 * Generate Basic Auth header for Confluence API requests
 * Confluence Cloud uses email:api_token encoded as Base64 (same as Jira)
 */
export function getAuthHeader(config: ConfluenceConfig): string {
  const credentials = `${config.email}:${config.apiToken}`;
  const base64Credentials = Buffer.from(credentials).toString("base64");
  return `Basic ${base64Credentials}`;
}

/**
 * Get common headers for Confluence API requests
 */
export function getConfluenceHeaders(
  config: ConfluenceConfig,
): Record<string, string> {
  return {
    Authorization: getAuthHeader(config),
    Accept: "application/json",
    "Content-Type": "application/json",
  };
}
