/**
 * Get Confluence Page ADF Tool (read-only)
 *
 * Fetches a page as raw ADF (Atlas Document Format) JSON plus the metadata a
 * subsequent edit needs: id, title, and current version. This is the fetch half
 * of the anchor-preserving edit workflow — edit the returned `body`, keeping the
 * `marks` arrays on any text node you want to stay anchored, then hand it to
 * update_confluence_page.
 *
 * Prefer replace_confluence_text for small edits: it never routes the whole
 * document through the conversation, whereas this tool necessarily does.
 */

import { ConfluenceClient } from "../confluence/client.js";
import {
  validateInput,
  GetConfluencePageAdfSchema,
  ToolDefinition,
} from "../utils/validation.js";
import { collectInlineCommentAnchors } from "../utils/confluence-adf.js";

async function handler(input: any): Promise<string> {
  const validated = validateInput(GetConfluencePageAdfSchema, input);
  const client = new ConfluenceClient();

  try {
    const page = await client.getPageAdf(validated.pageId);
    const anchors = collectInlineCommentAnchors(page.body);

    return [
      `# ${page.title}`,
      "",
      `- **Page ID:** ${page.id}`,
      `- **Version:** ${page.version} (pass this as \`expectedVersion\` to update_confluence_page; it will write ${page.version + 1})`,
      `- **Inline-comment anchors:** ${anchors.length}`,
      "",
      "Edit the `body` below and pass it to `update_confluence_page`, along with " +
        `\`expectedVersion: ${page.version}\` so a concurrent edit is refused ` +
        "rather than overwritten. Keep the `marks` array on any text node whose " +
        "inline comment should stay attached.",
      "",
      "```json",
      JSON.stringify(page.body, null, 2),
      "```",
    ].join("\n");
  } catch (error) {
    return `Error retrieving Confluence page ADF: ${error instanceof Error ? error.message : String(error)}`;
  }
}

const getConfluencePageAdfTool: ToolDefinition = {
  name: "get_confluence_page_adf",
  description:
    "Fetch a Confluence page as raw ADF (Atlas Document Format) JSON plus its " +
    "current version, for an anchor-preserving edit. Use this as the fetch step " +
    "before update_confluence_page when a page has open inline comments, since " +
    "ADF round-trips the annotation marks that anchor them (markdown does not). " +
    "For a simple find/replace, prefer replace_confluence_text, which avoids " +
    "routing the whole document through the conversation.",
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

export default getConfluencePageAdfTool;
