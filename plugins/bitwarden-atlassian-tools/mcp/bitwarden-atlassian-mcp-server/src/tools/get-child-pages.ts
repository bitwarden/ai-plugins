/**
 * Get Child Pages Tool
 * Retrieve child pages of a Confluence page
 */

import { ConfluenceClient } from '../confluence/client.js';
import { validateInput, GetChildPagesSchema, ToolDefinition } from '../utils/validation.js';
import { ConfluencePage } from '../confluence/types.js';
import { resolveWebuiUrl } from '../utils/format.js';

/**
 * Format child pages for display
 */
function formatChildPages(pages: ConfluencePage[], parentPageId: string): string {
  let output = `# Child Pages of ${parentPageId}\n\n`;
  output += `**Found:** ${pages.length} page(s)\n\n`;

  if (pages.length === 0) {
    output += `No child pages found.\n`;
    return output;
  }

  output += `---\n\n`;

  for (const page of pages) {
    output += `**${page.title}** (ID: ${page.id})\n`;
    output += `- Status: ${page.status}\n`;
    if (page.version) {
      output += `- Last Modified: ${new Date(page.version.when).toLocaleString()}\n`;
      if (page.version.by?.displayName) {
        output += `- Modified By: ${page.version.by.displayName}\n`;
      }
    }
    if (page._links?.webui) {
      output += `- URL: ${resolveWebuiUrl(page._links.webui)}\n`;
    }
    output += `\n`;
  }

  return output;
}

/**
 * Handler function for get-child-pages tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(GetChildPagesSchema, input);
  const client = new ConfluenceClient();

  try {
    const limit = validated.limit ?? 25;
    const result = await client.getChildPages(validated.pageId, limit);

    return formatChildPages(result.results, validated.pageId);
  } catch (error) {
    return `Error getting child pages: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const getChildPagesTool: ToolDefinition = {
  name: 'get_child_pages',
  description: 'Get child pages of a specific Confluence page. Returns page titles, IDs, statuses, and modification info. Useful for navigating page hierarchies and finding documentation.',
  inputSchema: {
    type: 'object',
    properties: {
      pageId: {
        type: 'string',
        description: 'Parent Confluence page ID (numeric string)',
      },
      limit: {
        type: 'number',
        description: 'Maximum number of child pages to return (default: 25, max: 250)',
        default: 25,
        minimum: 1,
        maximum: 250,
      },
    },
    required: ['pageId'],
  },
  handler,
};

export default getChildPagesTool;
