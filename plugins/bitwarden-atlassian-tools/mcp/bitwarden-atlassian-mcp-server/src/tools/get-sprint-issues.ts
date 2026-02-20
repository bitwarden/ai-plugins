/**
 * Get Sprint Issues Tool
 * Get all issues in a specific sprint
 */

import { JiraClient } from '../jira/client.js';
import { validateInput, GetSprintIssuesSchema } from '../utils/validation.js';
import { ToolDefinition } from '../utils/filesystem-api.js';

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
 * Format sprint issues for display
 */
function formatSprintIssues(result: any, sprintId: number): string {
  let output = `# Issues in Sprint ${sprintId}\n\n`;
  output += `**Total:** ${result.total} issue(s)\n`;
  output += `**Showing:** ${result.issues.length}\n\n`;

  if (result.issues.length === 0) {
    output += `No issues found in this sprint.\n`;
    return output;
  }

  output += `---\n\n`;

  for (const issue of result.issues) {
    const fields = issue.fields;
    const assignee = fields.assignee?.displayName || 'Unassigned';
    const priority = fields.priority?.name || 'None';

    output += `**[${issue.key}]** ${fields.summary || 'No summary'}\n`;
    output += `- Status: ${fields.status?.name || 'Unknown'}`;
    output += ` | Type: ${fields.issuetype?.name || 'Unknown'}`;
    output += ` | Priority: ${priority}\n`;
    output += `- Assignee: ${assignee}\n`;
    if (fields.story_points || fields.customfield_10016) {
      output += `- Story Points: ${fields.story_points || fields.customfield_10016 || 'N/A'}\n`;
    }
    output += `\n`;
  }

  if (result.total > result.issues.length) {
    const remaining = result.total - result.issues.length;
    output += `\n**Note:** ${remaining} more issues available. Increase maxResults to see more.\n`;
  }

  return output;
}

/**
 * Handler function for get-sprint-issues tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(GetSprintIssuesSchema, input);
  const client = new JiraClient();

  try {
    const maxResults = validated.maxResults ?? 50;
    const result = await client.getSprintIssues(validated.sprintId, validated.fields, maxResults);

    return formatSprintIssues(result, validated.sprintId);
  } catch (error) {
    return `Error getting sprint issues: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const getSprintIssuesTool: ToolDefinition = {
  name: 'get_sprint_issues',
  description: 'Get all issues in a specific JIRA sprint. Returns issue keys, summaries, statuses, assignees, and priorities. Use sprint IDs from get_sprints tool.',
  inputSchema: {
    type: 'object',
    properties: {
      sprintId: {
        type: 'number',
        description: 'Sprint ID (get from get_sprints tool)',
      },
      fields: {
        type: 'array',
        items: { type: 'string' },
        description: 'Specific fields to return (e.g., ["summary", "status", "assignee"])',
      },
      maxResults: {
        type: 'number',
        description: 'Maximum number of issues to return (default: 50, max: 100)',
        default: 50,
        minimum: 1,
        maximum: 100,
      },
    },
    required: ['sprintId'],
  },
  handler,
};

export default getSprintIssuesTool;
