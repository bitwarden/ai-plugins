/**
 * Update Confluence Page Tool (write, opt-in)
 *
 * Overwrites a page's body with a full ADF document, for edits too large or
 * structural for replace_confluence_text (a rewritten section, reordered
 * blocks). Pair it with get_confluence_page_adf: fetch, edit the `body`, push it
 * back here.
 *
 *  - `dryRun` defaults to true. Forgetting the flag diffs the anchors and
 *    previews without writing. Dry runs need no write token.
 *  - Before writing, it compares the inline-comment anchors in the submitted
 *    body against those on the live page and warns about any that would be
 *    dropped — the failure mode this whole workflow exists to prevent.
 *  - Pass `expectedVersion` (the version get_confluence_page_adf reported) to
 *    guard against a concurrent edit. Because the edit spans two tool calls, the
 *    live page can move underneath it; without the guard a full-body write is
 *    last-write-wins and silently clobbers whatever changed in between.
 */

import { ConfluenceClient } from "../confluence/client.js";
import { hasConfluenceWriteToken } from "../confluence/auth.js";
import {
  validateInput,
  UpdateConfluencePageSchema,
  ToolDefinition,
} from "../utils/validation.js";
import { collectInlineCommentAnchors } from "../utils/confluence-adf.js";
import {
  writeTokenDryRunNote,
  writeTokenRefusalMessage,
  isWriteAuthError,
  writeScopeHint,
} from "../utils/write-guard.js";

const WRITE_TOKEN = "ATLASSIAN_CONFLUENCE_WRITE_TOKEN";

async function handler(input: any): Promise<string> {
  const validated = validateInput(UpdateConfluencePageSchema, input);

  // Read the live page for its current version, title, and anchor set, using the
  // always-present read token so the dry-run path needs no write credential.
  const reader = new ConfluenceClient();
  let page;
  try {
    page = await reader.getPageAdf(validated.pageId);
  } catch (error) {
    return `Error fetching Confluence page: ${error instanceof Error ? error.message : String(error)}`;
  }

  const anchorsBefore = collectInlineCommentAnchors(page.body);
  const anchorsAfter = collectInlineCommentAnchors(validated.adfBody);
  const droppedAnchors = anchorsBefore.filter(
    (a) => !anchorsAfter.some((b) => b.id === a.id),
  );

  const anchorSummary =
    `${anchorsBefore.length} on the live page, ${anchorsAfter.length} in the ` +
    "submitted body" +
    (droppedAnchors.length > 0
      ? ` — ⚠️ ${droppedAnchors.length} would be dropped: ${droppedAnchors
          .map((a) => a.id)
          .join(", ")}`
      : " (all preserved)");

  // The submitted body was edited against a version the caller fetched earlier;
  // if the live page has moved since, a full-body overwrite would silently
  // clobber that intervening edit. When the caller passes the version the body
  // came from, refuse on mismatch instead.
  const staleVersion =
    validated.expectedVersion !== undefined &&
    validated.expectedVersion !== page.version;

  if (validated.dryRun) {
    const lines = [
      `# Dry run: overwrite "${page.title}"`,
      "",
      "No request was sent. Re-run with `dryRun: false` to apply this edit.",
      "",
      `- **Page:** ${page.id} (version ${page.version} → ${page.version + 1})`,
      `- **Inline-comment anchors:** ${anchorSummary}`,
    ];
    if (validated.expectedVersion !== undefined) {
      lines.push(
        `- **Version guard:** body fetched at ${validated.expectedVersion}, live is ${page.version}` +
          (staleVersion
            ? " — ⚠️ a live write would be refused; re-fetch and re-apply"
            : " (match)"),
      );
    }
    lines.push("");
    if (staleVersion) {
      lines.push(
        "> The page changed since the body was fetched. Writing now would " +
          "overwrite that intervening edit. Re-fetch with get_confluence_page_adf " +
          "and re-apply before writing.",
        "",
      );
    }
    if (droppedAnchors.length > 0) {
      lines.push(
        "> Dropping an anchor leaves its inline comment dangling with no " +
          "highlight on the page. Keep the annotation mark on at least one text " +
          "node, or confirm this is intended before writing.",
        "",
      );
    }
    lines.push(
      "## Exact request",
      "",
      "```",
      `PUT /wiki/api/v2/pages/${page.id}`,
      "```",
      "",
    );
    if (!hasConfluenceWriteToken()) {
      lines.push(...writeTokenDryRunNote("edit", WRITE_TOKEN));
    }
    return lines.join("\n");
  }

  if (staleVersion) {
    return (
      `Refusing to overwrite: the page is now at version ${page.version}, but the ` +
      `submitted body was fetched at version ${validated.expectedVersion}. ` +
      "Someone edited the page in between, and a full-body write would discard " +
      "that change. Re-fetch with get_confluence_page_adf and re-apply the edit."
    );
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
      adfBody: validated.adfBody,
      message: validated.message ?? "update via update_confluence_page",
    });

    return [
      `Updated **${page.title}** to version ${updated.version?.number ?? page.version + 1}.`,
      "",
      `- Inline-comment anchors: ${anchorSummary}`,
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

const updateConfluencePageTool: ToolDefinition = {
  name: "update_confluence_page",
  description:
    "Overwrite a Confluence page's body with a full ADF document, for edits too " +
    "large or structural for replace_confluence_text. Fetch the body first with " +
    "get_confluence_page_adf, edit it (keeping annotation marks on anchored " +
    "text), then push it here. Pass expectedVersion (the version that fetch " +
    "reported) so a concurrent edit is refused rather than silently overwritten. " +
    "Defaults to a dry run that diffs inline-comment anchors and previews " +
    "without writing; pass dryRun: false to apply. Requires " +
    "ATLASSIAN_CONFLUENCE_WRITE_TOKEN for a live edit.",
  inputSchema: {
    type: "object",
    properties: {
      pageId: {
        type: "string",
        description: 'Confluence page ID (numeric string, e.g. "2923724969").',
        pattern: "^\\d+$",
      },
      adfBody: {
        type: "object",
        description:
          'The full ADF document to store (a node with type "doc" and a ' +
          "content array), typically the edited body from get_confluence_page_adf.",
        additionalProperties: true,
      },
      expectedVersion: {
        type: "integer",
        minimum: 1,
        description:
          "The page version the edited body was fetched at (reported by " +
          "get_confluence_page_adf). If given and the live page has since moved, " +
          "the write is refused instead of overwriting the newer version.",
      },
      message: {
        type: "string",
        description: "Optional version message recorded in the page history.",
      },
      dryRun: {
        type: "boolean",
        default: true,
        description:
          "When true (the default), diffs anchors and previews without writing.",
      },
    },
    required: ["pageId", "adfBody"],
  },
  handler,
};

export default updateConfluencePageTool;
