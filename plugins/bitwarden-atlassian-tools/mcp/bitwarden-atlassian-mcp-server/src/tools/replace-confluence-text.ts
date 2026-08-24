/**
 * Replace Confluence Text Tool (write, opt-in)
 *
 * Replaces every occurrence of a literal string across a page's text nodes,
 * preserving marks — including the annotation marks that anchor inline comments.
 * This is the anchor-safe path for small edits (a typo, a renamed symbol, a
 * reworded phrase): it never routes the whole document through the conversation.
 *
 *  - `dryRun` defaults to true. Forgetting the flag counts the matches and
 *    previews the change without writing. Dry runs need no write token.
 *  - The current body is always fetched with the read-only token; a live write
 *    pushes the edited body back with the write token.
 */

import { ConfluenceClient } from "../confluence/client.js";
import { hasConfluenceWriteToken } from "../confluence/auth.js";
import {
  validateInput,
  ReplaceConfluenceTextSchema,
  ToolDefinition,
} from "../utils/validation.js";
import {
  replaceInTextNodes,
  collectInlineCommentAnchors,
} from "../utils/confluence-adf.js";
import {
  writeTokenDryRunNote,
  writeTokenRefusalMessage,
  isWriteAuthError,
  writeScopeHint,
} from "../utils/write-guard.js";

const WRITE_TOKEN = "ATLASSIAN_CONFLUENCE_WRITE_TOKEN";

async function handler(input: any): Promise<string> {
  const validated = validateInput(ReplaceConfluenceTextSchema, input);

  // Fetch with the always-present read token so the dry-run path needs no write
  // credential and the anchor baseline is computed the same way in both paths.
  const reader = new ConfluenceClient();
  let page;
  try {
    page = await reader.getPageAdf(validated.pageId);
  } catch (error) {
    return `Error fetching Confluence page: ${error instanceof Error ? error.message : String(error)}`;
  }

  const anchorsBefore = collectInlineCommentAnchors(page.body);
  const result = replaceInTextNodes(
    page.body,
    validated.oldText,
    validated.newText,
  );
  const anchorsAfter = collectInlineCommentAnchors(page.body);
  const droppedAnchors = anchorsBefore.filter(
    (a) => !anchorsAfter.some((b) => b.id === a.id),
  );

  if (result.nodeCount === 0) {
    return [
      `No occurrences of ${JSON.stringify(validated.oldText)} found on "${page.title}" ` +
        `(page ${page.id}, version ${page.version}).`,
      "",
      "Nothing was written. Check the exact text, including whitespace and case.",
    ].join("\n");
  }

  if (validated.dryRun) {
    const lines = [
      `# Dry run: replace text on "${page.title}"`,
      "",
      "No request was sent. Re-run with `dryRun: false` to apply this edit.",
      "",
      `- **Page:** ${page.id} (version ${page.version} → ${page.version + 1})`,
      `- **Replace:** ${JSON.stringify(validated.oldText)} → ${JSON.stringify(validated.newText)}`,
      `- **Matches:** ${result.occurrenceCount} occurrence(s) across ${result.nodeCount} text node(s)`,
      `- **Inline-comment anchors:** ${anchorsBefore.length} before, ${anchorsAfter.length} after` +
        (droppedAnchors.length > 0
          ? ` — ⚠️ ${droppedAnchors.length} would be dropped`
          : " (all preserved)"),
      "",
      "## Exact request",
      "",
      "```",
      `PUT /wiki/api/v2/pages/${page.id}`,
      "```",
      "",
    ];
    if (!hasConfluenceWriteToken()) {
      lines.push(...writeTokenDryRunNote("edit", WRITE_TOKEN));
    }
    return lines.join("\n");
  }

  if (!hasConfluenceWriteToken()) {
    return writeTokenRefusalMessage("edit", WRITE_TOKEN);
  }

  try {
    const writer = new ConfluenceClient("write");
    const updated = await writer.updatePage({
      pageId: page.id,
      title: page.title,
      currentVersion: page.version,
      adfBody: page.body,
      message:
        validated.message ??
        `replace-text: ${validated.oldText} -> ${validated.newText}`,
    });

    return [
      `Updated **${page.title}** to version ${updated.version?.number ?? page.version + 1}.`,
      "",
      `- Replaced ${result.occurrenceCount} occurrence(s) across ${result.nodeCount} text node(s).`,
      `- Inline-comment anchors: ${anchorsAfter.length} preserved` +
        (droppedAnchors.length > 0
          ? `, ⚠️ ${droppedAnchors.length} dropped (${droppedAnchors.map((a) => a.id).join(", ")}).`
          : "."),
    ].join("\n");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (isWriteAuthError(message, "Confluence")) {
      return [
        `Error updating page: ${message}`,
        "",
        writeScopeHint(WRITE_TOKEN, "Confluence"),
      ].join("\n");
    }
    return `Error updating page: ${message}`;
  }
}

const replaceConfluenceTextTool: ToolDefinition = {
  name: "replace_confluence_text",
  description:
    "Replace every occurrence of a literal string on a Confluence page, " +
    "preserving inline-comment anchors and all other ADF formatting. Defaults " +
    "to a dry run that counts matches without writing; pass dryRun: false to " +
    "apply. This is the safe path for small edits on pages with open inline " +
    "comments. Requires ATLASSIAN_CONFLUENCE_WRITE_TOKEN for a live edit.",
  inputSchema: {
    type: "object",
    properties: {
      pageId: {
        type: "string",
        description: 'Confluence page ID (numeric string, e.g. "2923724969").',
        pattern: "^\\d+$",
      },
      oldText: {
        type: "string",
        description:
          "Exact literal text to find. Matched verbatim, including whitespace " +
          "and case; not a regex.",
      },
      newText: {
        type: "string",
        description:
          "Replacement text. May be empty to delete the matched text.",
      },
      message: {
        type: "string",
        description: "Optional version message recorded in the page history.",
      },
      dryRun: {
        type: "boolean",
        default: true,
        description:
          "When true (the default), counts matches and previews without writing.",
      },
    },
    required: ["pageId", "oldText", "newText"],
  },
  handler,
};

export default replaceConfluenceTextTool;
