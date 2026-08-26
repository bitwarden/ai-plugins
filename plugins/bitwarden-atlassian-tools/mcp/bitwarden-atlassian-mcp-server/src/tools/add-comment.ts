/**
 * Add Comment Tool (write, opt-in)
 *
 * Adds a plain-text comment to an existing Jira issue. Mirrors create-issue.ts:
 * `dryRun` defaults to true, and a live comment requires ATLASSIAN_JIRA_WRITE_TOKEN.
 */

import { JiraClient } from "../jira/client.js";
import { hasJiraWriteToken } from "../jira/auth.js";
import {
  validateInput,
  AddCommentSchema,
  AddCommentInput,
  ToolDefinition,
} from "../utils/validation.js";
import { buildCommentAdf } from "../utils/adf-build.js";
import {
  writeTokenDryRunNote,
  writeTokenRefusalMessage,
  isWriteAuthError,
  writeScopeHint,
} from "../utils/write-guard.js";

function renderDryRun(input: AddCommentInput, body: unknown): string {
  const lines: string[] = [
    `# Dry run: add comment to ${input.issueIdOrKey}`,
    "",
    "No request was sent. Re-run with `dryRun: false` to post this comment.",
    "",
    "## Comment body",
    "",
    input.body,
    "",
    "## Exact request",
    "",
    "```",
    `POST /rest/api/3/issue/${input.issueIdOrKey}/comment`,
    "```",
    "",
    "```json",
    JSON.stringify({ body }, null, 2),
    "```",
    "",
  ];

  if (!hasJiraWriteToken()) {
    lines.push(...writeTokenDryRunNote("comment"));
  }

  return lines.join("\n");
}

async function handler(input: any): Promise<string> {
  const validated = validateInput(AddCommentSchema, input);
  const body = buildCommentAdf(validated.body);

  if (validated.dryRun) {
    return renderDryRun(validated, body);
  }

  if (!hasJiraWriteToken()) {
    return writeTokenRefusalMessage("comment");
  }

  try {
    const client = new JiraClient("write");
    const created = await client.addComment(validated.issueIdOrKey, body);

    return [
      `Added comment to **${validated.issueIdOrKey}**.`,
      "",
      `- Comment id: ${created.id}`,
      `- Created: ${new Date(created.created).toLocaleString()}`,
    ].join("\n");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);

    return isWriteAuthError(message)
      ? [`Error adding comment: ${message}`, "", writeScopeHint()].join("\n")
      : `Error adding comment: ${message}`;
  }
}

const addCommentTool: ToolDefinition = {
  name: "add_issue_comment",
  description:
    "Add a plain-text comment to an existing Jira issue. Defaults to a dry run " +
    "that returns the exact payload without sending it; pass dryRun: false to " +
    "post for real. Requires ATLASSIAN_JIRA_WRITE_TOKEN for live posting.",
  inputSchema: {
    type: "object",
    properties: {
      issueIdOrKey: {
        type: "string",
        description: "Jira issue key, e.g. PM-12345.",
        pattern: "^[A-Z][A-Z0-9_]+-\\d+$",
      },
      body: {
        type: "string",
        description:
          "Comment text. Blank lines split the text into separate paragraphs.",
      },
      dryRun: {
        type: "boolean",
        default: true,
        description:
          "When true (the default), returns the exact payload without sending it.",
      },
    },
    required: ["issueIdOrKey", "body"],
  },
  handler,
};

export default addCommentTool;
