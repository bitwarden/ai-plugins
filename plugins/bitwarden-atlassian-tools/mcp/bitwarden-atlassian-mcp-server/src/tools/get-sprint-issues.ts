/**
 * Get Sprint Issues Tool
 * List all issues in a JIRA sprint
 */

import { JiraClient } from "../jira/client.js";
import {
  validateInput,
  GetSprintIssuesSchema,
  ToolDefinition,
} from "../utils/validation.js";
import { formatIssue } from "../utils/format-issue.js";

/**
 * Handler function for get-sprint-issues tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(GetSprintIssuesSchema, input);
  const client = new JiraClient();

  try {
    const maxResults = validated.maxResults ?? 50;
    const result = await client.getSprintIssues(
      validated.sprintId,
      validated.fields,
      maxResults,
    );

    if (result.issues.length === 0) {
      return `No issues found in sprint ${validated.sprintId}.`;
    }

    let output = `# Issues in Sprint ${validated.sprintId}\n\n`;
    output += `**Results:** ${result.issues.length}${result.total != null ? ` of ${result.total} total` : ""}\n\n`;
    output += `---\n\n`;

    for (const issue of result.issues) {
      output += formatIssue(issue);
      output += `\n---\n`;
    }

    if (result.total != null && result.total > result.issues.length) {
      output += `\n**Note:** More issues available. Increase maxResults to see more.\n`;
    }

    return output;
  } catch (error) {
    return `Error retrieving sprint issues: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const getSprintIssuesTool: ToolDefinition = {
  name: "get_sprint_issues",
  description:
    "List all issues in a Jira sprint. Requires a numeric sprintId (from get_sprints).",
  inputSchema: {
    type: "object",
    properties: {
      sprintId: {
        type: "number",
        description: "Numeric sprint ID (from get_sprints)",
      },
      fields: {
        type: "array",
        items: { type: "string" },
        description:
          'Specific fields to return (e.g., ["summary", "status", "assignee"])',
      },
      maxResults: {
        type: "number",
        description:
          "Maximum number of issues to return (default: 50, max: 100)",
        default: 50,
        minimum: 1,
        maximum: 100,
      },
    },
    required: ["sprintId"],
  },
  handler,
};

export default getSprintIssuesTool;
