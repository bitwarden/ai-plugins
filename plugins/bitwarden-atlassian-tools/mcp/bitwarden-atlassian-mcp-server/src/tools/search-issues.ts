/**
 * Search Issues Tool
 * Search for JIRA issues using JQL (JIRA Query Language)
 */

import { JiraClient } from "../jira/client.js";
import {
  validateInput,
  SearchIssuesSchema,
  SearchIssuesInput,
  ToolDefinition,
} from "../utils/validation.js";
import { formatIssue } from "../utils/format-issue.js";

/**
 * Handler function for search-issues tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(SearchIssuesSchema, input);
  const client = new JiraClient();

  try {
    const maxResults = validated.maxResults ?? 50;

    const result = await client.searchIssues({
      jql: validated.jql,
      maxResults,
      fields: validated.fields,
      expand: validated.expand,
      nextPageToken: validated.nextPageToken,
    });

    if (result.issues.length === 0) {
      return `No issues found matching query: ${validated.jql}`;
    }

    let output = `# JIRA Search Results\n\n`;
    output += `**Query:** ${validated.jql}\n`;
    output += `**Results:** ${result.issues.length}${result.total != null ? ` of ${result.total} total` : ""}\n\n`;
    output += `---\n\n`;

    for (const issue of result.issues) {
      output += formatIssue(issue);
      output += `\n---\n`;
    }

    if (result.nextPageToken) {
      output += `\n**Note:** More issues available. Use nextPageToken="${result.nextPageToken}" to fetch the next page.\n`;
    } else if (result.total != null && result.total > result.issues.length) {
      output += `\n**Note:** More issues available. Refine your query or increase maxResults to see more.\n`;
    }

    return output;
  } catch (error) {
    return `Error searching issues: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const searchIssuesTool: ToolDefinition = {
  name: "search_issues",
  description:
    'Search for JIRA issues using JQL (JIRA Query Language). Supports pagination and field selection. Examples: "project = PM AND status = Open", "assignee = currentUser() ORDER BY priority DESC"',
  inputSchema: {
    type: "object",
    properties: {
      jql: {
        type: "string",
        description:
          'JQL query string (e.g., "project = ABC AND status = Open")',
      },
      maxResults: {
        type: "number",
        description: "Number of results to return (default: 50, max: 100)",
        default: 50,
        minimum: 1,
        maximum: 100,
      },
      fields: {
        type: "array",
        items: { type: "string" },
        description:
          'Specific fields to return (e.g., ["summary", "status", "assignee"])',
      },
      expand: {
        type: "array",
        items: { type: "string" },
        description:
          'Additional entities to expand (e.g., ["changelog", "renderedFields"])',
      },
      nextPageToken: {
        type: "string",
        description:
          "Token for fetching the next page of results (returned in previous response)",
      },
    },
    required: ["jql"],
  },
  handler,
};

export default searchIssuesTool;
