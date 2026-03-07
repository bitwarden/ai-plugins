/**
 * Search Confluence Tool
 * Search for Confluence pages by space and/or title
 */

import { ConfluenceClient } from '../confluence/client.js';
import { validateInput, SearchConfluenceSchema, SearchConfluenceInput, ToolDefinition } from '../utils/validation.js';
import { resolveWebuiUrl } from '../utils/format.js';

/**
 * Format search results for display
 */
function formatSearchResults(results: any, params: SearchConfluenceInput): string {
  let output = `# Confluence Search Results\n\n`;

  // Display search parameters
  if (params.spaceKey) {
    output += `**Space:** ${params.spaceKey}\n`;
  }
  if (params.title) {
    output += `**Title Filter:** "${params.title}"\n`;
  }
  output += `**Limit:** ${params.limit || 25}\n\n`;

  if (!results.results || results.results.length === 0) {
    output += `No pages found matching your criteria.\n`;
    return output;
  }

  output += `**Found:** ${results.results.length} page(s)\n\n`;
  output += `---\n\n`;

  // List each page
  for (const page of results.results) {
    output += `## ${page.title}\n\n`;
    output += `**Page ID:** ${page.id}\n`;
    output += `**Type:** ${page.type}\n`;
    output += `**Status:** ${page.status}\n`;

    if (page.space) {
      output += `**Space:** ${page.space.name} (${page.space.key})\n`;
    }

    if (page.version) {
      output += `**Last Modified:** ${new Date(page.version.when).toLocaleString()}\n`;
      if (page.version.by?.displayName) {
        output += `**Modified By:** ${page.version.by.displayName}\n`;
      }
    }

    if (page._links?.webui) {
      output += `**URL:** ${resolveWebuiUrl(page._links.webui)}\n`;
    }

    output += `\n---\n\n`;
  }

  // Pagination info
  if (results._links?.next) {
    output += `\n**Note:** More results available. Use the cursor parameter from the next link to paginate.\n`;
  }

  return output;
}

/**
 * Handler function for search-confluence tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(SearchConfluenceSchema, input);
  const client = new ConfluenceClient();

  // Validate at least one search parameter is provided
  if (!validated.spaceKey && !validated.title) {
    return 'Error: At least one search parameter (spaceKey or title) must be provided';
  }

  try {
    // Zod applies defaults, but TypeScript doesn't know, so we provide fallbacks
    const limit = validated.limit ?? 25;

    // Create params object with explicit types
    const searchParams: SearchConfluenceInput = {
      spaceKey: validated.spaceKey,
      title: validated.title,
      limit,
      cursor: validated.cursor,
    };

    const results = await client.searchPages(searchParams);

    return formatSearchResults(results, searchParams);
  } catch (error) {
    return `Error searching Confluence: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const searchConfluenceTool: ToolDefinition = {
  name: 'search_confluence',
  description: 'Search for Confluence pages by space key and/or title. Returns a list of matching pages with metadata and links. At least one search parameter (spaceKey or title) must be provided.',
  inputSchema: {
    type: 'object',
    properties: {
      spaceKey: {
        type: 'string',
        description: 'Filter by Confluence space key (e.g., "EN" for Engineering space)',
      },
      title: {
        type: 'string',
        description: 'Filter by page title (partial match supported)',
      },
      limit: {
        type: 'number',
        description: 'Maximum number of results to return (default: 25, max: 250)',
        default: 25,
        minimum: 1,
        maximum: 250,
      },
      cursor: {
        type: 'string',
        description: 'Pagination cursor for retrieving next set of results',
      },
    },
  },
  handler,
};

export default searchConfluenceTool;
