/**
 * List Confluence Anchors Tool (read-only)
 *
 * Lists every inline-comment anchor on a page and the text each one covers. Run
 * it before and after an anchor-preserving edit and compare the id sets: an id
 * that vanished means that comment lost its anchor and now dangles.
 */

import { ConfluenceClient } from "../confluence/client.js";
import {
  validateInput,
  ListConfluenceAnchorsSchema,
  ToolDefinition,
} from "../utils/validation.js";
import { collectInlineCommentAnchors } from "../utils/confluence-adf.js";

async function handler(input: any): Promise<string> {
  const validated = validateInput(ListConfluenceAnchorsSchema, input);
  const client = new ConfluenceClient();

  try {
    const page = await client.getPageAdf(validated.pageId);
    const anchors = collectInlineCommentAnchors(page.body);

    if (anchors.length === 0) {
      return `No inline-comment anchors found on "${page.title}" (page ${page.id}, version ${page.version}).`;
    }

    const lines = [
      `# Inline-comment anchors on "${page.title}"`,
      "",
      `Page ${page.id}, version ${page.version} — ${anchors.length} anchor(s).`,
      "",
    ];

    for (const anchor of anchors) {
      lines.push(`- **${anchor.id}**`);
      for (const fragment of anchor.fragments) {
        lines.push(`  - ${JSON.stringify(fragment)}`);
      }
    }

    return lines.join("\n");
  } catch (error) {
    return `Error listing Confluence anchors: ${error instanceof Error ? error.message : String(error)}`;
  }
}

const listConfluenceAnchorsTool: ToolDefinition = {
  name: "list_confluence_anchors",
  description:
    "List every inline-comment anchor on a Confluence page and the text it " +
    "covers. Use it to establish a baseline before an edit and to verify " +
    "afterwards that the same anchor ids are still present — a missing id means " +
    "that comment has become dangling.",
  inputSchema: {
    type: "object",
    properties: {
      pageId: {
        type: "string",
        description: 'Confluence page ID (numeric string, e.g. "2923724969").',
        pattern: "^\\d+$",
      },
    },
    required: ["pageId"],
  },
  handler,
};

export default listConfluenceAnchorsTool;
