/**
 * Get Sprints Tool
 * List sprints for a JIRA Agile board, optionally filtered by state
 */

import { JiraClient } from "../jira/client.js";
import {
  validateInput,
  GetSprintsSchema,
  ToolDefinition,
} from "../utils/validation.js";
import { JiraSprint } from "../jira/types.js";

/**
 * Format sprint list for display
 */
function formatSprints(boardId: number, sprints: JiraSprint[]): string {
  let output = `# Sprints for Board ${boardId}\n\n`;
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
    const response = await client.getSprints(
      validated.boardId,
      validated.state,
      maxResults,
    );

    return formatSprints(validated.boardId, response.values);
  } catch (error) {
    return `Error retrieving sprints: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const getSprintsTool: ToolDefinition = {
  name: "get_sprints",
  description:
    "List sprints for a Jira board. Filter by state (active/future/closed). Requires a numeric boardId (from list_boards). Use a sprint id with get_sprint_issues.",
  inputSchema: {
    type: "object",
    properties: {
      boardId: {
        type: "number",
        description: "Numeric board ID (from list_boards)",
      },
      state: {
        type: "string",
        enum: ["active", "future", "closed"],
        description: "Filter sprints by state",
      },
      maxResults: {
        type: "number",
        description:
          "Maximum number of sprints to return (default: 50, max: 100)",
        default: 50,
        minimum: 1,
        maximum: 100,
      },
    },
    required: ["boardId"],
  },
  handler,
};

export default getSprintsTool;
