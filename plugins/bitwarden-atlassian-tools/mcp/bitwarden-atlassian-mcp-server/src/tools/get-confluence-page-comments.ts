/**
 * Get Confluence Page Comments Tool
 * Retrieve footer and inline comments for a Confluence page
 */

import { ConfluenceClient } from '../confluence/client.js';
import { ConfluenceComment } from '../confluence/types.js';
import { validateInput, GetConfluencePageCommentsSchema, GetConfluencePageCommentsInput, ToolDefinition } from '../utils/validation.js';
import { htmlToMarkdown } from '../utils/format.js';

/**
 * Format a single comment
 */
function formatComment(comment: ConfluenceComment, indent: number = 0): string {
  const prefix = '  '.repeat(indent);
  let output = '';

  const author = comment.version?.by?.displayName || 'Unknown';
  const date = comment.createdAt
    ? new Date(comment.createdAt).toLocaleString()
    : comment.version?.when
      ? new Date(comment.version.when).toLocaleString()
      : 'Unknown date';

  output += `${prefix}**${author}** (${date})`;

  // Add resolution status for inline comments if present
  if (comment.resolutionStatus) {
    output += ` [${comment.resolutionStatus.toUpperCase()}]`;
  }

  output += `\n`;

  // Add the highlighted text for inline comments
  if (comment.properties?.inlineOriginalSelection) {
    output += `${prefix}> "${comment.properties.inlineOriginalSelection}"\n`;
  }

  // Add comment body
  const bodyContent = comment.body?.storage?.value || comment.body?.view?.value || '';
  if (bodyContent) {
    const formattedContent = htmlToMarkdown(bodyContent);
    // Indent multi-line content
    const indentedContent = formattedContent
      .split('\n')
      .map(line => `${prefix}${line}`)
      .join('\n');
    output += `${indentedContent}\n`;
  }

  return output;
}

interface CommentThread {
  comment: ConfluenceComment;
  replies: ConfluenceComment[];
}

/**
 * Handler function for get-confluence-page-comments tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(GetConfluencePageCommentsSchema, input);
  const client = new ConfluenceClient();

  try {
    let output = '';

    // Fetch footer comments
    const footerComments = await client.getPageComments({
      pageId: validated.pageId,
      bodyFormat: validated.bodyFormat ?? 'storage',
      limit: validated.limit ?? 25,
    });

    // Fetch inline comments
    const inlineComments = await client.getPageInlineComments({
      pageId: validated.pageId,
      bodyFormat: validated.bodyFormat ?? 'storage',
      limit: validated.limit ?? 25,
    });

    // Process footer comments with replies
    if (footerComments.results.length > 0) {
      output += `## Footer Comments (${footerComments.results.length})\n\n`;

      for (const comment of footerComments.results) {
        output += formatComment(comment);

        // Fetch replies if requested
        if (validated.includeReplies) {
          try {
            const replies = await client.getCommentReplies({
              commentId: comment.id,
              bodyFormat: validated.bodyFormat ?? 'storage',
              limit: 50,
            });

            for (const reply of replies.results) {
              output += formatComment(reply, 1);
            }
          } catch {
            // Ignore errors fetching replies
          }
        }

        output += '\n---\n\n';
      }
    }

    // Process inline comments with replies
    if (inlineComments.results.length > 0) {
      output += `## Inline Comments (${inlineComments.results.length})\n\n`;

      for (const comment of inlineComments.results) {
        output += formatComment(comment);

        // Fetch replies if requested
        if (validated.includeReplies) {
          try {
            const replies = await client.getInlineCommentReplies({
              commentId: comment.id,
              bodyFormat: validated.bodyFormat ?? 'storage',
              limit: 50,
            });

            for (const reply of replies.results) {
              output += formatComment(reply, 1);
            }
          } catch {
            // Ignore errors fetching replies
          }
        }

        output += '\n---\n\n';
      }
    }

    if (!output) {
      return `No comments found for page ${validated.pageId}`;
    }

    return `# Comments for Page ${validated.pageId}\n\n${output}`;
  } catch (error) {
    return `Error retrieving Confluence page comments: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const getConfluencePageCommentsTool: ToolDefinition = {
  name: 'get_confluence_page_comments',
  description: 'Get all comments (footer and inline) for a specific Confluence page by ID. Retrieves comment text, author, timestamp, and optionally all replies. Useful for reading discussions, clarifications, and feedback on documentation pages.',
  inputSchema: {
    type: 'object',
    properties: {
      pageId: {
        type: 'string',
        description: 'Confluence page ID (numeric string, e.g., "2503245825")',
      },
      bodyFormat: {
        type: 'string',
        description: 'Content format for comment body: "storage" (raw XML)',
        enum: ['storage'],
        default: 'storage',
      },
      limit: {
        type: 'number',
        description: 'Maximum number of comments to return per type (default: 25, max: 100)',
        default: 25,
        minimum: 1,
        maximum: 100,
      },
      includeReplies: {
        type: 'boolean',
        description: 'Whether to include replies to comments (default: true)',
        default: true,
      },
    },
    required: ['pageId'],
  },
  handler,
};

export default getConfluencePageCommentsTool;
