/**
 * Get Issue Remote Links Tool
 * Retrieve remote links for a JIRA issue (Confluence pages, PRs, external URLs)
 */

import { JiraClient } from '../jira/client.js';
import { JiraRemoteLink } from '../jira/types.js';
import { validateInput, GetIssueRemoteLinksSchema, ToolDefinition } from '../utils/validation.js';

/**
 * Categorize a remote link as Confluence, GitHub, or Other
 */
function categorizeLink(link: JiraRemoteLink): 'confluence' | 'github' | 'other' {
  const url = link.object.url;
  const appName = link.application?.name?.toLowerCase() || '';

  if (appName.includes('confluence') || url.includes('bitwarden.atlassian.net/wiki')) {
    return 'confluence';
  }
  if (appName.includes('github') || url.includes('github.com')) {
    return 'github';
  }
  return 'other';
}

/**
 * Format a single link for display
 */
function formatLink(link: JiraRemoteLink): string {
  let output = `- **[${link.object.title}](${link.object.url})**`;
  if (link.relationship) {
    output += ` (${link.relationship})`;
  }
  if (link.object.summary) {
    output += `\n  ${link.object.summary}`;
  }
  if (link.object.status?.resolved !== undefined) {
    output += `\n  Status: ${link.object.status.resolved ? 'Resolved' : 'Open'}`;
  }
  return output;
}

/**
 * Format remote links grouped by type
 */
function formatRemoteLinks(issueKey: string, links: JiraRemoteLink[]): string {
  if (links.length === 0) {
    return `No remote links found for ${issueKey}.`;
  }

  const grouped: Record<string, JiraRemoteLink[]> = {
    confluence: [],
    github: [],
    other: [],
  };

  for (const link of links) {
    grouped[categorizeLink(link)].push(link);
  }

  let output = `# Remote Links for ${issueKey}\n\n`;
  output += `**Total Links:** ${links.length}\n\n`;

  if (grouped.confluence.length > 0) {
    output += `## Confluence Pages\n\n`;
    output += grouped.confluence.map(formatLink).join('\n\n');
    output += `\n\n`;
  }

  if (grouped.github.length > 0) {
    output += `## GitHub\n\n`;
    output += grouped.github.map(formatLink).join('\n\n');
    output += `\n\n`;
  }

  if (grouped.other.length > 0) {
    output += `## Other Links\n\n`;
    output += grouped.other.map(formatLink).join('\n\n');
    output += `\n\n`;
  }

  return output;
}

/**
 * Handler function for get-issue-remote-links tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(GetIssueRemoteLinksSchema, input);
  const client = new JiraClient();

  try {
    const links = await client.getRemoteLinks(validated.issueIdOrKey);
    return formatRemoteLinks(validated.issueIdOrKey, links);
  } catch (error) {
    return `Error retrieving remote links: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const getIssueRemoteLinksTool: ToolDefinition = {
  name: 'get_issue_remote_links',
  description: 'Get all remote links for a JIRA issue. Returns linked Confluence pages, GitHub PRs, and other external resources connected to the issue. Useful for discovering related documentation and pull requests.',
  inputSchema: {
    type: 'object',
    properties: {
      issueIdOrKey: {
        type: 'string',
        description: 'JIRA issue key (e.g., "PM-12345") or numeric ID',
        pattern: '^[A-Z][A-Z0-9_]+-\\d+$|^\\d+$',
      },
    },
    required: ['issueIdOrKey'],
  },
  handler,
};

export default getIssueRemoteLinksTool;
