/**
 * List Boards Tool
 * List JIRA Agile boards, optionally filtered by project
 */

import { JiraClient } from '../jira/client.js';
import { validateInput, ListBoardsSchema } from '../utils/validation.js';
import { ToolDefinition } from '../utils/filesystem-api.js';
import { JiraBoard } from '../jira/types.js';

/**
 * Format board list for display
 */
function formatBoards(boards: JiraBoard[], projectFilter?: string): string {
  let output = `# JIRA Boards\n\n`;

  if (projectFilter) {
    output += `**Project Filter:** ${projectFilter}\n`;
  }

  output += `**Found:** ${boards.length} board(s)\n\n`;

  if (boards.length === 0) {
    output += `No boards found.\n`;
    return output;
  }

  output += `---\n\n`;

  for (const board of boards) {
    output += `**${board.name}** (ID: ${board.id})\n`;
    output += `- Type: ${board.type}\n`;
    if (board.location) {
      output += `- Project: ${board.location.projectName} (${board.location.projectKey})\n`;
    }
    output += `\n`;
  }

  return output;
}

/**
 * Handler function for list-boards tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(ListBoardsSchema, input);
  const client = new JiraClient();

  try {
    const maxResults = validated.maxResults ?? 50;
    const result = await client.listBoards(validated.projectKeyOrId, maxResults);

    return formatBoards(result.values, validated.projectKeyOrId);
  } catch (error) {
    return `Error listing boards: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const listBoardsTool: ToolDefinition = {
  name: 'list_boards',
  description: 'List JIRA Agile boards, optionally filtered by project. Returns board names, IDs, types, and associated projects. Use board IDs with get_sprints to find sprints.',
  inputSchema: {
    type: 'object',
    properties: {
      projectKeyOrId: {
        type: 'string',
        description: 'Filter boards by project key (e.g., "PM") or project ID. Omit to list all accessible boards.',
      },
      maxResults: {
        type: 'number',
        description: 'Maximum number of boards to return (default: 50, max: 100)',
        default: 50,
        minimum: 1,
        maximum: 100,
      },
    },
  },
  handler,
};

export default listBoardsTool;
