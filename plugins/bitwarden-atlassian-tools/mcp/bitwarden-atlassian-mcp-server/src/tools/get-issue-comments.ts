/**
 * Get Issue Comments Tool
 * Retrieve all comments for a specific JIRA issue
 */

import { JiraClient } from '../jira/client.js';
import { validateInput, GetIssueCommentsSchema, GetIssueCommentsInput, ToolDefinition } from '../utils/validation.js';
import { extractPlainText } from '../utils/adf.js';

/**
 * Format comments for display
 */
function formatComments(issueKey: string, commentsResponse: any): string {
  let output = `# Comments for ${issueKey}\n\n`;
  output += `**Total Comments:** ${commentsResponse.total}\n`;
  output += `**Showing:** ${commentsResponse.startAt + 1} - ${commentsResponse.startAt + commentsResponse.comments.length}\n\n`;

  if (commentsResponse.comments.length === 0) {
    output += `No comments found.\n`;
    return output;
  }

  output += `---\n\n`;

  for (const comment of commentsResponse.comments) {
    const commentText = extractPlainText(comment.body);

    output += `## Comment by ${comment.author.displayName}\n\n`;
    output += `**Created:** ${new Date(comment.created).toLocaleString()}\n`;

    if (comment.updated !== comment.created) {
      output += `**Updated:** ${new Date(comment.updated).toLocaleString()}\n`;
    }

    output += `\n${commentText}\n\n`;
    output += `---\n\n`;
  }

  if (commentsResponse.total > commentsResponse.startAt + commentsResponse.comments.length) {
    const remaining = commentsResponse.total - (commentsResponse.startAt + commentsResponse.comments.length);
    output += `\n**Note:** ${remaining} more comments available. Use startAt parameter to paginate.\n`;
  }

  return output;
}

/**
 * Handler function for get-issue-comments tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(GetIssueCommentsSchema, input);
  const client = new JiraClient();

  try {
    // Zod applies defaults, but TypeScript doesn't know, so we provide fallbacks
    const startAt = validated.startAt ?? 0;
    const maxResults = validated.maxResults ?? 50;

    const comments = await client.getIssueComments(
      validated.issueIdOrKey,
      startAt,
      maxResults
    );

    return formatComments(validated.issueIdOrKey, comments);
  } catch (error) {
    return `Error retrieving comments: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const getIssueCommentsTool: ToolDefinition = {
  name: 'get_issue_comments',
  description: 'Get all comments for a specific JIRA issue. Useful for understanding discussions, clarifications, and additional context around requirements.',
  inputSchema: {
    type: 'object',
    properties: {
      issueIdOrKey: {
        type: 'string',
        description: 'JIRA issue key (e.g., "PM-12345") or numeric ID',
        pattern: '^[A-Z][A-Z0-9_]+-\\d+$|^\\d+$',
      },
      startAt: {
        type: 'number',
        description: 'Pagination offset (default: 0)',
        default: 0,
        minimum: 0,
      },
      maxResults: {
        type: 'number',
        description: 'Number of comments to return (default: 50, max: 100)',
        default: 50,
        minimum: 1,
        maximum: 100,
      },
    },
    required: ['issueIdOrKey'],
  },
  handler,
};

export default getIssueCommentsTool;
