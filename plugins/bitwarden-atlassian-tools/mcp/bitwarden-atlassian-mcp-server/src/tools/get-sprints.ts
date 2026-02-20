/**
 * Get Sprints Tool
 * Get sprints for a JIRA Agile board
 */

import { JiraClient } from '../jira/client.js';
import { validateInput, GetSprintsSchema } from '../utils/validation.js';
import { ToolDefinition } from '../utils/filesystem-api.js';
import { JiraSprint } from '../jira/types.js';

/**
 * Format sprint list for display
 */
function formatSprints(sprints: JiraSprint[], boardId: number, stateFilter?: string): string {
  let output = `# Sprints for Board ${boardId}\n\n`;

  if (stateFilter) {
    output += `**State Filter:** ${stateFilter}\n`;
  }

  output += `**Found:** ${sprints.length} sprint(s)\n\n`;

  if (sprints.length === 0) {
    output += `No sprints found.\n`;
    return output;
  }

  output += `---\n\n`;

  for (const sprint of sprints) {
    output += `**${sprint.name}** (ID: ${sprint.id})\n`;
    output += `- State: ${sprint.state}\n`;
    if (sprint.startDate) {
      output += `- Start: ${new Date(sprint.startDate).toLocaleDateString()}\n`;
    }
    if (sprint.endDate) {
      output += `- End: ${new Date(sprint.endDate).toLocaleDateString()}\n`;
    }
    if (sprint.completeDate) {
      output += `- Completed: ${new Date(sprint.completeDate).toLocaleDateString()}\n`;
    }
    if (sprint.goal) {
      output += `- Goal: ${sprint.goal}\n`;
    }
    output += `\n`;
  }

  return output;
}

/**
 * Handler function for get-sprints tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(GetSprintsSchema, input);
  const client = new JiraClient();

  try {
    const maxResults = validated.maxResults ?? 50;
    const result = await client.getSprints(validated.boardId, validated.state, maxResults);

    return formatSprints(result.values, validated.boardId, validated.state);
  } catch (error) {
    return `Error getting sprints: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const getSprintsTool: ToolDefinition = {
  name: 'get_sprints',
  description: 'Get sprints for a JIRA Agile board. Returns sprint names, IDs, states, dates, and goals. Filter by state (active, closed, future). Use sprint IDs with get_sprint_issues to list issues.',
  inputSchema: {
    type: 'object',
    properties: {
      boardId: {
        type: 'number',
        description: 'Board ID (get from list_boards tool)',
      },
      state: {
        type: 'string',
        description: 'Filter by sprint state: "active", "closed", or "future"',
        enum: ['active', 'closed', 'future'],
      },
      maxResults: {
        type: 'number',
        description: 'Maximum number of sprints to return (default: 50, max: 100)',
        default: 50,
        minimum: 1,
        maximum: 100,
      },
    },
    required: ['boardId'],
  },
  handler,
};

export default getSprintsTool;
