/**
 * Confluence API Authentication Module
 * Handles Basic Auth with API tokens for Confluence Cloud
 * Uses the same Atlassian authentication as Jira
 */

import { ConfluenceConfig } from './types.js';

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
 * Load Confluence configuration from environment variables
 * @throws {Error} If required environment variables are missing
 */
export function loadConfluenceConfig(): ConfluenceConfig {
  const cloudId = resolveEnv('ATLASSIAN_CLOUD_ID');
  const email = resolveEnv('ATLASSIAN_EMAIL');
  const apiToken = resolveEnv('ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN');

  if (!cloudId || !email || !apiToken) {
    throw new Error(
      'Missing required Confluence environment variables. ' +
      'Please set ATLASSIAN_CLOUD_ID, ATLASSIAN_EMAIL, and ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN'
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
  const base64Credentials = Buffer.from(credentials).toString('base64');
  return `Basic ${base64Credentials}`;
}

/**
 * Get common headers for Confluence API requests
 */
export function getConfluenceHeaders(config: ConfluenceConfig): Record<string, string> {
  return {
    'Authorization': getAuthHeader(config),
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  };
}
