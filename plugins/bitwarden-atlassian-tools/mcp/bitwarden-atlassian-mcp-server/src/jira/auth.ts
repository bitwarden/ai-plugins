/**
 * JIRA API Authentication Module
 * Handles Basic Auth with API tokens for JIRA Cloud
 */

import { JiraConfig } from './types.js';

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
 * Load JIRA configuration from environment variables
 * @throws {Error} If required environment variables are missing
 */
export function loadJiraConfig(): JiraConfig {
  const cloudId = resolveEnv('ATLASSIAN_CLOUD_ID');
  const email = resolveEnv('ATLASSIAN_EMAIL');
  const apiToken = resolveEnv('ATLASSIAN_JIRA_READ_ONLY_TOKEN');

  if (!cloudId || !email || !apiToken) {
    throw new Error(
      'Missing required JIRA environment variables. ' +
      'Please set ATLASSIAN_CLOUD_ID, ATLASSIAN_EMAIL, and ATLASSIAN_JIRA_READ_ONLY_TOKEN'
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
  const base64Credentials = Buffer.from(credentials).toString('base64');
  return `Basic ${base64Credentials}`;
}

/**
 * Get common headers for JIRA API requests
 */
export function getJiraHeaders(config: JiraConfig): Record<string, string> {
  return {
    'Authorization': getAuthHeader(config),
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  };
}
