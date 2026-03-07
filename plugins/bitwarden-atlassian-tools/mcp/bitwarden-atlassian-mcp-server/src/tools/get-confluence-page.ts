/**
 * Get Confluence Page Tool
 * Retrieve a Confluence page by ID with full content
 */

import { ConfluenceClient } from '../confluence/client.js';
import { validateInput, GetConfluencePageSchema, GetConfluencePageInput, ToolDefinition } from '../utils/validation.js';
import { htmlToMarkdown, resolveWebuiUrl } from '../utils/format.js';

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
    output += `**URL:** ${resolveWebuiUrl(page._links.webui)}\n`;
  }

  output += `\n---\n\n`;

  // Add page content if available
  if (page.body?.storage?.value) {
    output += `## Content\n\n`;
    const formattedContent = htmlToMarkdown(page.body.storage.value);
    output += formattedContent + '\n';
  } else if (page.body?.view?.value) {
    output += `## Content\n\n`;
    const formattedContent = htmlToMarkdown(page.body.view.value);
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
