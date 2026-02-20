/**
 * Confluence API Authentication Module
 * Handles Basic Auth with API tokens for Confluence Cloud
 * Uses the same Atlassian authentication as JIRA
 */

import { ConfluenceConfig } from './types.js';

/**
 * Load Confluence configuration from environment variables
 * Falls back to JIRA credentials if Confluence-specific ones aren't set
 * @throws {Error} If required environment variables are missing
 */
export function loadConfluenceConfig(): ConfluenceConfig {
  // Try Confluence-specific variables first, fall back to JIRA variables
  const url = process.env.CONFLUENCE_URL || process.env.JIRA_URL;
  const email = process.env.CONFLUENCE_EMAIL || process.env.JIRA_EMAIL;
  const apiToken = process.env.CONFLUENCE_API_TOKEN || process.env.JIRA_API_TOKEN;

  if (!url || !email || !apiToken) {
    throw new Error(
      'Missing required Confluence environment variables. ' +
      'Please set either CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN ' +
      'or use JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN (same Atlassian credentials)'
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
 * Generate Basic Auth header for Confluence API requests
 * Confluence Cloud uses email:api_token encoded as Base64 (same as JIRA)
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
