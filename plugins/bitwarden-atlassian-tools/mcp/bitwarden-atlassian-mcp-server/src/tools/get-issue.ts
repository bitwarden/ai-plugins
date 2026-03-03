/**
 * Get Issue Tool
 * Retrieve detailed information about a specific JIRA issue
 */

import { JiraClient } from '../jira/client.js';
import { validateInput, GetIssueSchema, GetIssueInput, ToolDefinition } from '../utils/validation.js';
import { extractPlainText } from '../utils/adf.js';

/**
 * Format issue details for display
 */
function formatIssueDetails(issue: any): string {
  const fields = issue.fields;
  let output = `# ${issue.key}: ${fields.summary || 'No summary'}\n\n`;

  // Basic information
  output += `## Basic Information\n\n`;
  output += `- **Issue Key:** ${issue.key}\n`;
  if (fields.issuetype) {
    output += `- **Type:** ${fields.issuetype?.name || 'Unknown'}\n`;
  }
  if (fields.status) {
    output += `- **Status:** ${fields.status?.name || 'Unknown'} (${fields.status?.statusCategory?.name || 'Unknown'})\n`;
  }
  output += `- **Priority:** ${fields.priority?.name || 'None'}\n`;
  if (fields.project) {
    output += `- **Project:** ${fields.project?.name || 'Unknown'} (${fields.project?.key || 'Unknown'})\n`;
  }
  output += `\n`;

  // People (only render if reporter or assignee present)
  if (fields.reporter || fields.assignee) {
    output += `## People\n\n`;
    if (fields.reporter) {
      output += `- **Reporter:** ${fields.reporter?.displayName || 'Unknown'}`;
      if (fields.reporter?.emailAddress) {
        output += ` (${fields.reporter.emailAddress})`;
      }
      output += `\n`;
    }
    output += `- **Assignee:** ${fields.assignee?.displayName || 'Unassigned'}`;
    if (fields.assignee?.emailAddress) {
      output += ` (${fields.assignee.emailAddress})`;
    }
    output += `\n\n`;
  }

  // Dates (only render if created or updated present)
  if (fields.created || fields.updated) {
    output += `## Dates\n\n`;
    if (fields.created) {
      output += `- **Created:** ${new Date(fields.created).toLocaleString()}\n`;
    }
    if (fields.updated) {
      output += `- **Updated:** ${new Date(fields.updated).toLocaleString()}\n`;
    }
    if (fields.duedate) {
      output += `- **Due Date:** ${new Date(fields.duedate).toLocaleDateString()}\n`;
    }
    if (fields.resolutiondate) {
      output += `- **Resolved:** ${new Date(fields.resolutiondate).toLocaleString()}\n`;
    }
    output += `\n`;
  }

  // Description
  if (fields.description) {
    output += `## Description\n\n`;
    const descText = extractPlainText(fields.description);
    output += descText || '(Empty description)';
    output += `\n\n`;
  }

  // Labels
  if (fields.labels && fields.labels.length > 0) {
    output += `## Labels\n\n`;
    output += fields.labels.map((label: string) => `- ${label}`).join('\n');
    output += `\n\n`;
  }

  // Components
  if (fields.components && fields.components.length > 0) {
    output += `## Components\n\n`;
    for (const component of fields.components) {
      output += `- **${component?.name || 'Unknown'}**`;
      if (component?.description) {
        output += `: ${component.description}`;
      }
      output += `\n`;
    }
    output += `\n`;
  }

  // Fix Versions
  if (fields.fixVersions && fields.fixVersions.length > 0) {
    output += `## Fix Versions\n\n`;
    for (const version of fields.fixVersions) {
      output += `- **${version?.name || 'Unknown'}**`;
      if (version?.released) {
        output += ` (Released)`;
      }
      if (version.description) {
        output += `: ${version.description}`;
      }
      output += `\n`;
    }
    output += `\n`;
  }

  // Subtasks
  if (fields.subtasks && fields.subtasks.length > 0) {
    output += `## Subtasks\n\n`;
    for (const subtask of fields.subtasks) {
      output += `- **[${subtask.key}]** ${subtask.fields?.summary || 'No summary'} - ${subtask.fields?.status?.name || 'Unknown'}\n`;
    }
    output += `\n`;
  }

  // Parent (if this is a subtask)
  if (fields.parent) {
    output += `## Parent Issue\n\n`;
    output += `**[${fields.parent.key}]** ${fields.parent.fields?.summary || 'No summary'}\n\n`;
  }

  // Attachments
  if (fields.attachment && fields.attachment.length > 0) {
    output += `## Attachments\n\n`;
    for (const attachment of fields.attachment) {
      output += `- **${attachment?.filename || 'Unknown'}** (${((attachment?.size || 0) / 1024).toFixed(2)} KB)\n`;
      output += `  - Added by ${attachment?.author?.displayName || 'Unknown'} on ${attachment?.created ? new Date(attachment.created).toLocaleDateString() : 'Unknown'}\n`;
      output += `  - URL: ${attachment?.content || 'N/A'}\n`;
    }
    output += `\n`;
  }

  // Comments summary
  if (fields.comment) {
    output += `## Comments\n\n`;
    output += `**Total Comments:** ${fields.comment.total}\n\n`;
    if (fields.comment.comments && fields.comment.comments.length > 0) {
      output += `**Recent Comments:**\n\n`;
      for (const comment of fields.comment.comments.slice(0, 3)) {
        const commentText = extractPlainText(comment.body);
        output += `---\n`;
        output += `**${comment.author?.displayName || 'Unknown'}** on ${new Date(comment.created).toLocaleString()}:\n\n`;
        output += commentText.substring(0, 300) + (commentText.length > 300 ? '...' : '');
        output += `\n\n`;
      }
      if (fields.comment.total > 3) {
        output += `_...and ${fields.comment.total - 3} more comments. Use get_issue_comments tool for all comments._\n\n`;
      }
    }
  }

  return output;
}

/**
 * Handler function for get-issue tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(GetIssueSchema, input);
  const client = new JiraClient();

  try {
    const issue = await client.getIssue(
      validated.issueIdOrKey,
      validated.fields,
      validated.expand || ['renderedFields']
    );

    return formatIssueDetails(issue);
  } catch (error) {
    return `Error retrieving issue: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const getIssueTool: ToolDefinition = {
  name: 'get_issue',
  description: 'Get detailed information about a specific JIRA issue by key (e.g., "PM-12345") or ID. Returns comprehensive issue details including description, comments, attachments, and relationships.',
  inputSchema: {
    type: 'object',
    properties: {
      issueIdOrKey: {
        type: 'string',
        description: 'JIRA issue key (e.g., "PM-12345") or numeric ID',
        pattern: '^[A-Z][A-Z0-9_]+-\\d+$|^\\d+$',
      },
      fields: {
        type: 'array',
        items: { type: 'string' },
        description: 'Specific fields to return. Omit to get all fields.',
      },
      expand: {
        type: 'array',
        items: { type: 'string' },
        description: 'Additional entities to expand (e.g., ["changelog", "renderedFields"])',
      },
    },
    required: ['issueIdOrKey'],
  },
  handler,
};

export default getIssueTool;
