/**
 * List Spaces Tool
 * List accessible Confluence spaces
 */

import { ConfluenceClient } from '../confluence/client.js';
import { validateInput, ListSpacesSchema, ToolDefinition } from '../utils/validation.js';
import { ConfluenceSpace } from '../confluence/types.js';


/**
 * Format space list for display
 */
function formatSpaces(spaces: ConfluenceSpace[]): string {
  let output = `# Confluence Spaces\n\n`;
  output += `**Found:** ${spaces.length} space(s)\n\n`;

  if (spaces.length === 0) {
    output += `No accessible spaces found.\n`;
    return output;
  }

  output += `---\n\n`;

  for (const space of spaces) {
    output += `**${space.name}** (${space.key})\n`;
    output += `- ID: ${space.id}\n`;
    output += `- Type: ${space.type}\n`;
    output += `- Status: ${space.status}\n`;
    if (space._links?.webui) {
      output += `- URL: ${space._links.webui}\n`;
    }
    output += `\n`;
  }

  return output;
}

/**
 * Handler function for list-spaces tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(ListSpacesSchema, input);
  const client = new ConfluenceClient();

  try {
    const limit = validated.limit ?? 25;
    const result = await client.listSpaces(limit, validated.type);

    return formatSpaces(result.results);
  } catch (error) {
    return `Error listing spaces: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const listSpacesTool: ToolDefinition = {
  name: 'list_spaces',
  description: 'List accessible Confluence spaces. Returns space names, keys, types, and statuses. Use space keys with search_confluence to find pages in a specific space.',
  inputSchema: {
    type: 'object',
    properties: {
      limit: {
        type: 'number',
        description: 'Maximum number of spaces to return (default: 25, max: 250)',
        default: 25,
        minimum: 1,
        maximum: 250,
      },
      type: {
        type: 'string',
        description: 'Filter by space type (e.g., "global", "personal")',
      },
    },
  },
  handler,
};

export default listSpacesTool;
