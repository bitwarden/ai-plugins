/**
 * JIRA API Authentication Module
 * Handles Basic Auth with API tokens for JIRA Cloud
 */

import { JiraConfig } from './types.js';

/**
 * Load JIRA configuration from environment variables
 * @throws {Error} If required environment variables are missing
 */
export function loadJiraConfig(): JiraConfig {
  const url = process.env.JIRA_URL;
  const email = process.env.JIRA_EMAIL;
  const apiToken = process.env.JIRA_API_TOKEN;

  if (!url || !email || !apiToken) {
    throw new Error(
      'Missing required JIRA environment variables. ' +
      'Please set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN'
    );
  }

  // Normalize URL by removing trailing slash
  const normalizedUrl = url.endsWith('/') ? url.slice(0, -1) : url;

  return {
    url: normalizedUrl,
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
