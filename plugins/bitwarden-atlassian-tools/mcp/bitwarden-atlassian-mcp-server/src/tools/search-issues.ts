/**
 * Search Issues Tool
 * Search for JIRA issues using JQL (JIRA Query Language)
 */

import { JiraClient } from '../jira/client.js';
import { validateInput, SearchIssuesSchema, SearchIssuesInput, ToolDefinition } from '../utils/validation.js';

/**
 * Format issue for display in results
 */
function formatIssue(issue: any): string {
  const fields = issue.fields;
  const assignee = fields.assignee?.displayName || 'Unassigned';
  const priority = fields.priority?.name || 'None';
  const labels = fields.labels?.join(', ') || 'None';

  return `
**[${issue.key}]** ${fields.summary || 'No summary'}
- Status: ${fields.status?.name || 'Unknown'}
- Type: ${fields.issuetype?.name || 'Unknown'}
- Priority: ${priority}
- Assignee: ${assignee}
- Reporter: ${fields.reporter?.displayName || 'Unknown'}
${fields.created ? `- Created: ${new Date(fields.created).toLocaleDateString()}` : ''}
${fields.updated ? `- Updated: ${new Date(fields.updated).toLocaleDateString()}` : ''}
- Labels: ${labels}
${fields.description ? `- Description: ${extractPlainText(fields.description)}` : ''}
`;
}

/**
 * Extract plain text from JIRA ADF (Atlassian Document Format)
 */
function extractPlainText(adf: any): string {
  if (!adf || !adf.content) return '';

  let text = '';
  for (const node of adf.content) {
    if (node.type === 'paragraph' && node.content) {
      for (const contentNode of node.content) {
        if (contentNode.type === 'text') {
          text += contentNode.text + ' ';
        }
      }
    }
  }

  return text.trim().substring(0, 200) + (text.length > 200 ? '...' : '');
}

/**
 * Handler function for search-issues tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(SearchIssuesSchema, input);
  const client = new JiraClient();

  try {
    // Zod applies defaults, but TypeScript doesn't know, so we provide fallbacks
    const startAt = validated.startAt ?? 0;
    const maxResults = validated.maxResults ?? 50;

    const result = await client.searchIssues({
      jql: validated.jql,
      startAt,
      maxResults,
      fields: validated.fields,
      expand: validated.expand,
    });

    if (result.issues.length === 0) {
      return `No issues found matching query: ${validated.jql}`;
    }

    let output = `# JIRA Search Results\n\n`;
    output += `**Query:** ${validated.jql}\n`;
    output += `**Results:** ${result.issues.length}${result.total != null ? ` of ${result.total} total` : ''}\n`;
    output += `**Page:** ${startAt + 1} - ${startAt + result.issues.length}\n\n`;
    output += `---\n\n`;

    for (const issue of result.issues) {
      output += formatIssue(issue);
      output += `\n---\n`;
    }

    if (result.nextPageToken) {
      output += `\n**Note:** More issues available. Use nextPageToken="${result.nextPageToken}" to fetch the next page.\n`;
    } else if (result.total != null && result.total > startAt + result.issues.length) {
      const remaining = result.total - (startAt + result.issues.length);
      output += `\n**Note:** ${remaining} more issues available.\n`;
    }

    return output;
  } catch (error) {
    return `Error searching issues: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const searchIssuesTool: ToolDefinition = {
  name: 'search_issues',
  description: 'Search for JIRA issues using JQL (JIRA Query Language). Supports pagination and field selection. Examples: "project = PM AND status = Open", "assignee = currentUser() ORDER BY priority DESC"',
  inputSchema: {
    type: 'object',
    properties: {
      jql: {
        type: 'string',
        description: 'JQL query string (e.g., "project = ABC AND status = Open")',
      },
      startAt: {
        type: 'number',
        description: 'Pagination offset (default: 0)',
        default: 0,
        minimum: 0,
      },
      maxResults: {
        type: 'number',
        description: 'Number of results to return (default: 50, max: 100)',
        default: 50,
        minimum: 1,
        maximum: 100,
      },
      fields: {
        type: 'array',
        items: { type: 'string' },
        description: 'Specific fields to return (e.g., ["summary", "status", "assignee"])',
      },
      expand: {
        type: 'array',
        items: { type: 'string' },
        description: 'Additional entities to expand (e.g., ["changelog", "renderedFields"])',
      },
    },
    required: ['jql'],
  },
  handler,
};

export default searchIssuesTool;
