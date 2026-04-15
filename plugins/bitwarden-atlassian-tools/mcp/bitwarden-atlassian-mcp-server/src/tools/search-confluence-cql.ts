/**
 * Search Confluence CQL Tool
 * Search for Confluence content using CQL (Confluence Query Language)
 */

import { ConfluenceClient } from '../confluence/client.js';
import { validateInput, SearchConfluenceCqlSchema, SearchConfluenceCqlInput, ToolDefinition } from '../utils/validation.js';


/**
 * Format CQL search results for display
 */
function formatCqlSearchResults(results: any, params: SearchConfluenceCqlInput): string {
  let output = `# Confluence CQL Search Results\n\n`;

  output += `**CQL:** \`${params.cql}\`\n`;
  output += `**Limit:** ${params.limit || 10}\n`;

  if (params.start && params.start > 0) {
    output += `**Start:** ${params.start}\n`;
  }

  output += `\n`;

  if (!results.results || results.results.length === 0) {
    output += `No content found matching your CQL query.\n`;
    return output;
  }

  output += `**Found:** ${results.size} of ${results.totalSize} total result(s)\n\n`;
  output += `---\n\n`;

  for (const item of results.results) {
    output += `## ${item.title}\n\n`;
    output += `**Content ID:** ${item.id}\n`;
    output += `**Type:** ${item.type}\n`;
    output += `**Status:** ${item.status}\n`;

    if (item.space) {
      output += `**Space:** ${item.space.name} (${item.space.key})\n`;
    }

    if (item._links?.webui) {
      output += `**URL:** ${item._links.webui}\n`;
    }

    output += `\n---\n\n`;
  }

  if (results.size < results.totalSize) {
    output += `\n**Note:** Showing ${results.size} of ${results.totalSize} total results. Use the \`start\` parameter to paginate (next start: ${(params.start || 0) + results.size}).\n`;
  }

  return output;
}

/**
 * Handler function for search-confluence-cql tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(SearchConfluenceCqlSchema, input);
  const client = new ConfluenceClient();

  try {
    const limit = validated.limit ?? 10;
    const start = validated.start ?? 0;

    const results = await client.searchCql({
      cql: validated.cql,
      limit,
      start,
    });

    return formatCqlSearchResults(results, { cql: validated.cql, limit, start });
  } catch (error) {
    return `Error searching Confluence with CQL: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const searchConfluenceCqlTool: ToolDefinition = {
  name: 'search_confluence_cql',
  description: 'Search for Confluence content using CQL (Confluence Query Language). Supports text search, label filtering, space filtering, ancestor queries, and date-based queries. Examples: text ~ "search term", space = "EN" AND label = "architecture", ancestor = 123456789.',
  inputSchema: {
    type: 'object',
    properties: {
      cql: {
        type: 'string',
        description: 'CQL query string (e.g., \'text ~ "search term"\', \'space = "EN" AND label = "docs"\')',
      },
      limit: {
        type: 'number',
        description: 'Maximum number of results to return (default: 10, max: 100)',
        default: 10,
        minimum: 1,
        maximum: 100,
      },
      start: {
        type: 'number',
        description: 'Pagination offset for retrieving next set of results (default: 0)',
        default: 0,
        minimum: 0,
      },
    },
    required: ['cql'],
  },
  handler,
};

export default searchConfluenceCqlTool;
