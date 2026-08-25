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
 * Access mode for a Confluence client.
 *
 * "read" uses ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN, which every install already
 * sets. "write" uses ATLASSIAN_CONFLUENCE_WRITE_TOKEN, which is optional: when
 * it is absent, the write tools are still listed and their dry-run preview still
 * works, but a live edit refuses to execute. Confluence write capability is
 * therefore opt-in per install, exactly like Jira write.
 */
export type ConfluenceAccessMode = "read" | "write";

const TOKEN_ENV_VAR: Record<ConfluenceAccessMode, string> = {
  read: "ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN",
  write: "ATLASSIAN_CONFLUENCE_WRITE_TOKEN",
};

/**
 * Whether this install has been given a write-capable Confluence token.
 */
export function hasConfluenceWriteToken(): boolean {
  return resolveEnv(TOKEN_ENV_VAR.write) !== undefined;
}

/**
 * Load Confluence configuration from environment variables
 * @param mode - Which token to authenticate with. Defaults to read-only.
 * @throws {Error} If required environment variables are missing
 */
export function loadConfluenceConfig(
  mode: ConfluenceAccessMode = "read",
): ConfluenceConfig {
  const cloudId = resolveEnv("ATLASSIAN_CLOUD_ID");
  const email = resolveEnv("ATLASSIAN_EMAIL");
  const tokenVar = TOKEN_ENV_VAR[mode];
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
