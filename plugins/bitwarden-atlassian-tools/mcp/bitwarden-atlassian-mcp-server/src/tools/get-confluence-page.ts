/**
 * Get Confluence Page Tool
 * Retrieve a Confluence page by ID with full content
 */

import { ConfluenceClient } from '../confluence/client.js';
import { validateInput, GetConfluencePageSchema, GetConfluencePageInput } from '../utils/validation.js';
import { ToolDefinition } from '../utils/filesystem-api.js';

/**
 * Convert Confluence storage format to readable text
 * Confluence uses XHTML-like storage format
 */
function formatStorageContent(html: string): string {
  if (!html) return '';

  // Basic HTML to plain text conversion
  let text = html;

  // Replace common tags with readable equivalents
  text = text.replace(/<br\s*\/?>/gi, '\n');
  text = text.replace(/<\/p>/gi, '\n\n');
  text = text.replace(/<p[^>]*>/gi, '');
  text = text.replace(/<h([1-6])[^>]*>/gi, (_, level) => '\n' + '#'.repeat(parseInt(level)) + ' ');
  text = text.replace(/<\/h[1-6]>/gi, '\n');
  text = text.replace(/<li[^>]*>/gi, '- ');
  text = text.replace(/<\/li>/gi, '\n');
  text = text.replace(/<ul[^>]*>|<\/ul>/gi, '\n');
  text = text.replace(/<ol[^>]*>|<\/ol>/gi, '\n');
  text = text.replace(/<strong[^>]*>|<\/strong>/gi, '**');
  text = text.replace(/<b[^>]*>|<\/b>/gi, '**');
  text = text.replace(/<em[^>]*>|<\/em>/gi, '_');
  text = text.replace(/<i[^>]*>|<\/i>/gi, '_');
  text = text.replace(/<code[^>]*>|<\/code>/gi, '`');
  text = text.replace(/<pre[^>]*>/gi, '\n```\n');
  text = text.replace(/<\/pre>/gi, '\n```\n');

  // Remove remaining HTML tags
  text = text.replace(/<[^>]+>/g, '');

  // Decode HTML entities
  text = text.replace(/&nbsp;/g, ' ');
  text = text.replace(/&lt;/g, '<');
  text = text.replace(/&gt;/g, '>');
  text = text.replace(/&amp;/g, '&');
  text = text.replace(/&quot;/g, '"');
  text = text.replace(/&#39;/g, "'");

  // Clean up excessive newlines
  text = text.replace(/\n{3,}/g, '\n\n');

  return text.trim();
}

/**
 * Format page for display
 */
function formatPage(page: any): string {
  let output = `# ${page.title}\n\n`;

  output += `**Page ID:** ${page.id}\n`;
  output += `**Status:** ${page.status}\n`;

  if (page.space) {
    output += `**Space:** ${page.space.name} (${page.space.key})\n`;
  }

  if (page.version) {
    output += `**Version:** ${page.version.number}\n`;
    if (page.version.when) {
      output += `**Last Modified:** ${new Date(page.version.when).toLocaleString()}\n`;
    }
    if (page.version.by?.displayName) {
      output += `**Modified By:** ${page.version.by.displayName}\n`;
    }
  }

  if (page._links?.webui) {
    const baseUrl = page._links.webui.startsWith('http')
      ? page._links.webui
      : `${process.env.JIRA_URL || process.env.CONFLUENCE_URL}${page._links.webui}`;
    output += `**URL:** ${baseUrl}\n`;
  }

  output += `\n---\n\n`;

  // Add page content if available
  if (page.body?.storage?.value) {
    output += `## Content\n\n`;
    const formattedContent = formatStorageContent(page.body.storage.value);
    output += formattedContent + '\n';
  } else if (page.body?.view?.value) {
    output += `## Content\n\n`;
    const formattedContent = formatStorageContent(page.body.view.value);
    output += formattedContent + '\n';
  } else {
    output += `_No content available_\n`;
  }

  return output;
}

/**
 * Handler function for get-confluence-page tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(GetConfluencePageSchema, input);
  const client = new ConfluenceClient();

  try {
    const page = await client.getPage({
      pageId: validated.pageId,
      includeBody: validated.includeBody ?? true,
      bodyFormat: validated.bodyFormat ?? 'storage',
    });

    return formatPage(page);
  } catch (error) {
    return `Error retrieving Confluence page: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const getConfluencePageTool: ToolDefinition = {
  name: 'get_confluence_page',
  description: 'Get detailed content from a specific Confluence page by ID. Retrieves the page title, metadata, and full content in readable format. Useful for reading documentation, requirements, and other knowledge base articles.',
  inputSchema: {
    type: 'object',
    properties: {
      pageId: {
        type: 'string',
        description: 'Confluence page ID (numeric string, e.g., "2270330935")',
      },
      includeBody: {
        type: 'boolean',
        description: 'Whether to include page content (default: true)',
        default: true,
      },
      bodyFormat: {
        type: 'string',
        description: 'Content format to retrieve: "storage" (raw), "view" (rendered HTML), or "export_view" (export format)',
        enum: ['storage', 'view', 'export_view'],
        default: 'storage',
      },
    },
    required: ['pageId'],
  },
  handler,
};

export default getConfluencePageTool;
