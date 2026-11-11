/**
 * Update Confluence Page Tool (write, opt-in)
 *
 * Updates an existing page by ID. Three properties are deliberate:
 *
 *  - `dryRun` defaults to true. Forgetting the flag yields a payload preview,
 *    not a live update. Dry runs need no write token at all.
 *  - Version number is auto-incremented: the tool fetches the current page to
 *    read its version, then sends currentVersion + 1. The caller never needs
 *    to know or manage version numbers.
 *  - Body content can be markdown or Confluence storage format (XHTML).
 *    Markdown is auto-converted; storage format is passed through as-is.
 */

import { ConfluenceClient } from "../confluence/client.js";
import { hasConfluenceWriteToken } from "../confluence/auth.js";
import {
  validateInput,
  UpdateConfluencePageSchema,
  UpdateConfluencePageInput,
  ToolDefinition,
} from "../utils/validation.js";
import {
  writeTokenDryRunNote,
  writeTokenRefusalMessage,
  isWriteAuthError,
  writeScopeHint,
} from "../utils/write-guard.js";
import { markdownToStorage } from "../utils/markdown-to-storage.js";

async function renderDryRun(
  input: UpdateConfluencePageInput,
  storageBody: string,
): Promise<string> {
  // Fetch current version even in dry-run so the preview shows the real
  // version number that would be sent.
  let currentVersion = "?";
  let nextVersion = "?";
  let currentTitle = "(unknown)";
  try {
    const readClient = new ConfluenceClient("read");
    const page = await readClient.getPage({
      pageId: input.pageId,
      includeBody: false,
    });
    currentVersion = String(page.version?.number ?? "?");
    nextVersion = page.version?.number ? String(page.version.number + 1) : "?";
    currentTitle = page.title;
  } catch {
    // Non-fatal: the dry run still works, just without version info.
  }

  const lines: string[] = [
    "# Dry run: update Confluence page",
    "",
    "No request was sent. Re-run with `dryRun: false` to apply this update.",
    "",
    "## Summary of what would change",
    "",
    `- **Page ID:** ${input.pageId}`,
    `- **Current title:** ${currentTitle}`,
    `- **New title:** ${input.title}`,
    `- **Current version:** ${currentVersion}`,
    `- **Next version:** ${nextVersion}`,
    `- **Version message:** ${input.versionMessage ?? "(none)"}`,
    `- **Status:** ${input.status}`,
    `- **Body length:** ${storageBody.length} characters (storage format)`,
    "",
    "## Exact request",
    "",
    "```",
    `PUT /wiki/api/v2/pages/${input.pageId}`,
    "```",
    "",
    "```json",
    JSON.stringify(
      {
        id: input.pageId,
        status: input.status,
        title: input.title,
        body: {
          representation: "storage",
          value:
            storageBody.length > 500
              ? storageBody.slice(0, 500) + "... (truncated)"
              : storageBody,
        },
        version: {
          number: nextVersion,
          message: input.versionMessage || undefined,
        },
      },
      null,
      2,
    ),
    "```",
    "",
  ];

  if (!hasConfluenceWriteToken()) {
    lines.push(...writeTokenDryRunNote("update", "confluence"));
  }

  return lines.join("\n");
}

async function handler(input: any): Promise<string> {
  const validated = validateInput(UpdateConfluencePageSchema, input);
  const storageBody = markdownToStorage(validated.body);

  if (validated.dryRun) {
    return renderDryRun(validated, storageBody);
  }

  if (!hasConfluenceWriteToken()) {
    return writeTokenRefusalMessage("update a Confluence page", "confluence");
  }

  try {
    // Fetch current version to auto-increment
    const readClient = new ConfluenceClient("read");
    const currentPage = await readClient.getPage({
      pageId: validated.pageId,
      includeBody: false,
    });

    const currentVersionNumber = currentPage.version?.number;
    if (!currentVersionNumber) {
      return `Error: could not read current version for page ${validated.pageId}. The page may not exist.`;
    }

    const writeClient = new ConfluenceClient("write");
    const updated = await writeClient.updatePage({
      id: validated.pageId,
      title: validated.title,
      body: {
        representation: "storage",
        value: storageBody,
      },
      version: {
        number: currentVersionNumber + 1,
        message: validated.versionMessage,
      },
      status: validated.status,
    });

    const webUrl = updated._links?.webui
      ? `https://bitwarden.atlassian.net/wiki${updated._links.webui}`
      : "(link unavailable)";

    return [
      `Updated Confluence page **${updated.title}** (ID: ${updated.id}).`,
      "",
      `- Version: ${currentVersionNumber} -> ${updated.version?.number}`,
      `- Status: ${updated.status}`,
      `- URL: ${webUrl}`,
    ].join("\n");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);

    if (isWriteAuthError(message, "confluence")) {
      return [
        `Error updating Confluence page: ${message}`,
        "",
        writeScopeHint("confluence"),
      ].join("\n");
    }

    return `Error updating Confluence page: ${message}`;
  }
}

const updateConfluencePageTool: ToolDefinition = {
  name: "update_confluence_page",
  description:
    "Update an existing Confluence page by ID. Defaults to a dry run that " +
    "returns the exact payload without sending it; pass dryRun: false to " +
    "update for real. Version number is auto-incremented — no need to " +
    "manage it manually. Body content can be markdown (auto-converted) or " +
    "Confluence storage format (XHTML). Requires " +
    "ATLASSIAN_CONFLUENCE_WRITE_TOKEN for live updates.",
  inputSchema: {
    type: "object",
    properties: {
      pageId: {
        type: "string",
        description:
          "Confluence page ID (numeric string). Use get_confluence_page " +
          "or search_confluence to find page IDs.",
      },
      title: {
        type: "string",
        description: "New page title. Must be unique within the space.",
        maxLength: 255,
      },
      body: {
        type: "string",
        description:
          "New page content as markdown or Confluence storage format (XHTML). " +
          "Markdown is auto-converted to storage format. If the body starts " +
          "with an HTML tag it is treated as storage format and passed through " +
          "as-is. This replaces the entire page body.",
      },
      versionMessage: {
        type: "string",
        description:
          "Optional version comment describing the change (visible in page history).",
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
    required: ["pageId", "title", "body"],
  },
  handler,
};

export default updateConfluencePageTool;
