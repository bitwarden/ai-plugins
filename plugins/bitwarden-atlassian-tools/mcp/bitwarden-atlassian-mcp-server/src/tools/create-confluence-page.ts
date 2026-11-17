/**
 * Create Confluence Page Tool (write, opt-in)
 *
 * Creates a new page in a Confluence space. Three properties are deliberate:
 *
 *  - `dryRun` defaults to true. Forgetting the flag yields a payload preview,
 *    not a live page. Dry runs need no write token at all.
 *  - Body content can be markdown or Confluence storage format (XHTML).
 *    Markdown is auto-converted; storage format is passed through as-is.
 *  - Confluence is the validator. Title uniqueness and space permissions
 *    come back from the API verbatim.
 */

import { ConfluenceClient } from "../confluence/client.js";
import { hasConfluenceWriteToken } from "../confluence/auth.js";
import {
  validateInput,
  CreateConfluencePageSchema,
  CreateConfluencePageInput,
  ToolDefinition,
} from "../utils/validation.js";
import {
  writeTokenDryRunNote,
  writeTokenRefusalMessage,
  isWriteAuthError,
  writeScopeHint,
} from "../utils/write-guard.js";
import { markdownToStorage } from "../utils/markdown-to-storage.js";

function renderDryRun(
  input: CreateConfluencePageInput,
  storageBody: string,
): string {
  const lines: string[] = [
    "# Dry run: create Confluence page",
    "",
    "No request was sent. Re-run with `dryRun: false` to create this page.",
    "",
    "## Summary of what would be created",
    "",
    `- **Space ID:** ${input.spaceId}`,
    `- **Title:** ${input.title}`,
    `- **Parent ID:** ${input.parentId ?? "(space root)"}`,
    `- **Status:** ${input.status}`,
    `- **Body length:** ${storageBody.length} characters (storage format)`,
    "",
    "## Exact request",
    "",
    "```",
    "POST /wiki/api/v2/pages",
    "```",
    "",
    "```json",
    JSON.stringify(
      {
        spaceId: input.spaceId,
        status: input.status,
        title: input.title,
        parentId: input.parentId || undefined,
        body: {
          representation: "storage",
          value:
            storageBody.length > 500
              ? storageBody.slice(0, 500) + "... (truncated)"
              : storageBody,
        },
      },
      null,
      2,
    ),
    "```",
    "",
  ];

  if (!hasConfluenceWriteToken()) {
    lines.push(...writeTokenDryRunNote("create", "confluence"));
  }

  return lines.join("\n");
}

async function handler(input: any): Promise<string> {
  const validated = validateInput(CreateConfluencePageSchema, input);
  const storageBody = markdownToStorage(validated.body);

  if (validated.dryRun) {
    return renderDryRun(validated, storageBody);
  }

  if (!hasConfluenceWriteToken()) {
    return writeTokenRefusalMessage("create a Confluence page", "confluence");
  }

  try {
    const client = new ConfluenceClient("write");
    const created = await client.createPage({
      spaceId: validated.spaceId,
      title: validated.title,
      parentId: validated.parentId,
      body: {
        representation: "storage",
        value: storageBody,
      },
      status: validated.status,
    });

    const webUrl = created._links?.webui
      ? `https://bitwarden.atlassian.net/wiki${created._links.webui}`
      : "(link unavailable)";

    return [
      `Created Confluence page **${created.title}** (ID: ${created.id}).`,
      "",
      `- Space ID: ${created.spaceId}`,
      `- Status: ${created.status}`,
      `- URL: ${webUrl}`,
    ].join("\n");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);

    if (isWriteAuthError(message, "confluence")) {
      return [
        `Error creating Confluence page: ${message}`,
        "",
        writeScopeHint("confluence"),
      ].join("\n");
    }

    return `Error creating Confluence page: ${message}`;
  }
}

const createConfluencePageTool: ToolDefinition = {
  name: "create_confluence_page",
  description:
    "Create a new Confluence page in a space. Defaults to a dry run that " +
    "returns the exact payload without sending it; pass dryRun: false to " +
    "create for real. Body content can be markdown (auto-converted) or " +
    "Confluence storage format (XHTML). Use list_spaces to find space IDs. " +
    "Requires ATLASSIAN_CONFLUENCE_WRITE_TOKEN for live creation.",
  inputSchema: {
    type: "object",
    properties: {
      spaceId: {
        type: "string",
        description:
          'Confluence space ID (numeric string, e.g. "229380"). ' +
          "Use list_spaces to discover space IDs.",
      },
      title: {
        type: "string",
        description: "Page title. Must be unique within the space.",
        maxLength: 255,
      },
      parentId: {
        type: "string",
        description:
          "Parent page ID to nest under. Omit to create at the space root.",
      },
      body: {
        type: "string",
        description:
          "Page content as markdown or Confluence storage format (XHTML). " +
          "Markdown is auto-converted to storage format. If the body starts " +
          "with an HTML tag it is treated as storage format and passed through as-is.",
      },
      status: {
        type: "string",
        enum: ["current", "draft"],
        default: "current",
        description: 'Page status: "current" (published) or "draft".',
      },
      dryRun: {
        type: "boolean",
        default: true,
        description:
          "When true (the default), returns the exact payload without sending it.",
      },
    },
    required: ["spaceId", "title", "body"],
  },
  handler,
};

export default createConfluencePageTool;
