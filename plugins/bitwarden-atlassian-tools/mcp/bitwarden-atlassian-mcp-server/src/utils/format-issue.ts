/**
 * Shared formatting utility for JIRA issues.
 * Used by tools that render issue lists (search_issues, get_sprint_issues).
 */

import { extractPlainTextTruncated } from "./adf.js";

/**
 * Format a single issue for display in results.
 */
export function formatIssue(issue: any): string {
  const fields = issue.fields;
  const assignee = fields.assignee?.displayName || "Unassigned";
  const priority = fields.priority?.name || "None";
  const labels = fields.labels?.join(", ") || "None";

  return `
**[${issue.key}]** ${fields.summary || "No summary"}
- Status: ${fields.status?.name || "Unknown"}
- Type: ${fields.issuetype?.name || "Unknown"}
- Priority: ${priority}
- Assignee: ${assignee}
- Reporter: ${fields.reporter?.displayName || "Unknown"}
${fields.created ? `- Created: ${new Date(fields.created).toLocaleDateString()}` : ""}
${fields.updated ? `- Updated: ${new Date(fields.updated).toLocaleDateString()}` : ""}
- Labels: ${labels}
${fields.description ? `- Description: ${extractPlainTextTruncated(fields.description)}` : ""}
`;
}
