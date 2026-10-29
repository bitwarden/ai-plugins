/**
 * Create Confluence Page Tool (write, opt-in)
 *
 * Creates an unpublished draft from markdown; publishing is left to a person
 * in Confluence. Follows the Jira write tools:
 *
 *  - The space is never guessed. The tool looks the space id up and names the
 *    space in its result, so the user can confirm it, and an id that matches
 *    no space is reported with an instruction to ask the user.
 *  - `dryRun` defaults to true and returns the exact request without writing.
 *  - A live create needs ATLASSIAN_CONFLUENCE_WRITE_TOKEN, used for the create
 *    request alone, and refuses before any request when it is not set.
 *  - The draft is read back with the read-only token and checked against what
 *    was sent.
 */

import { ConfluenceClient } from "../confluence/client.js";
import { hasConfluenceWriteToken } from "../confluence/auth.js";
import {
  ConfluencePage,
  ConfluencePageCreateRequest,
  ConfluenceSpace,
} from "../confluence/types.js";
import {
  validateInput,
  CreateConfluencePageSchema,
  CreateConfluencePageInput,
  ToolDefinition,
} from "../utils/validation.js";
import { markdownToStorage } from "../utils/markdown-storage.js";

/**
 * Assemble the create request. Exported so the payload, which is the whole
 * contract, can be asserted directly.
 */
export function buildCreatePagePayload(
  input: CreateConfluencePageInput,
  storage: string,
): ConfluencePageCreateRequest {
  return {
    spaceId: input.spaceId,
    status: "draft",
    title: input.title,
    ...(input.parentId !== undefined ? { parentId: input.parentId } : {}),
    body: { representation: "storage", value: storage },
  };
}

/**
 * The text of a storage body with markup, entities, and whitespace removed.
 * Confluence normalizes markup on save, so the stored body is compared with
 * the one sent by text content rather than byte for byte.
 */
export function storageText(storage: string): string {
  const entities: Record<string, string> = {
    amp: "&",
    lt: "<",
    gt: ">",
    quot: '"',
    nbsp: " ",
  };

  return storage
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/<[^>]*>/g, "")
    .replace(
      /&(?:#(\d+)|#x([0-9a-f]+)|(\w+));/gi,
      (entity, dec?: string, hex?: string, name?: string) => {
        if (dec) return String.fromCodePoint(Number(dec));
        if (hex) return String.fromCodePoint(parseInt(hex, 16));
        return entities[name!.toLowerCase()] ?? entity;
      },
    )
    .replace(/\s+/g, "");
}

/**
 * Read the draft back and check its status, title, and body text. A mismatch
 * or failed read is reported, never thrown, since the create has succeeded.
 */
async function verifyDraft(
  pageId: string,
  payload: ConfluencePageCreateRequest,
): Promise<string> {
  try {
    const page = await new ConfluenceClient("read").getPage({
      pageId,
      includeBody: true,
      bodyFormat: "storage",
      getDraft: true,
    });
    const problems: string[] = [];

    if (page.status !== "draft") {
      problems.push(`the status is "${page.status}", not "draft"`);
    }
    if (page.title !== payload.title) {
      problems.push(`the title is "${page.title}"`);
    }
    const stored = page.body?.storage?.value;
    if (
      stored === undefined ||
      storageText(stored) !== storageText(payload.body.value)
    ) {
      problems.push("the body text differs from what was sent");
    }

    return problems.length === 0
      ? `Verified: reading page ${pageId} back shows an unpublished draft with the title and body text that were sent.`
      : `Could not verify: reading page ${pageId} back shows that ${problems.join("; ")}. Check the draft in Confluence.`;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return `Could not verify the draft by reading ${pageId} back: ${message}`;
  }
}

/** A draft opens in the editor, so link there. */
function draftUrl(page: ConfluencePage): string | undefined {
  const path = page._links?.editui ?? page._links?.webui;
  if (!path) return undefined;
  return page._links?.base ? `${page._links.base}${path}` : path;
}

function describeSpace(space: ConfluenceSpace): string {
  return `${space.name} (${space.key}, id ${space.id})`;
}

async function handler(input: any): Promise<string> {
  const validated = validateInput(CreateConfluencePageSchema, input);

  if (!validated.dryRun && !hasConfluenceWriteToken()) {
    return (
      "Refusing to create: ATLASSIAN_CONFLUENCE_WRITE_TOKEN is not set.\n\n" +
      "Set a Confluence API token with the write:page:confluence scope as " +
      "ATLASSIAN_CONFLUENCE_WRITE_TOKEN to enable this, or call this tool " +
      "with dryRun: true to preview the request."
    );
  }

  let space: ConfluenceSpace;
  try {
    space = await new ConfluenceClient("read").getSpace(validated.spaceId);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return (
      `No Confluence space with id ${validated.spaceId} could be read ` +
      `(${message}). Ask the user which space to create the draft in; ` +
      "do not guess."
    );
  }

  const { storage, warnings } = markdownToStorage(validated.body);
  const payload = buildCreatePagePayload(validated, storage);
  const notes =
    warnings.length > 0
      ? ["## Conversion notes", "", ...warnings.map((w) => `- ${w}`), ""]
      : [];

  if (validated.dryRun) {
    return [
      `# Dry run: create Confluence draft "${validated.title}"`,
      "",
      "No draft was created. Confirm the space below with the user, then " +
        "re-run with `dryRun: false` to create it.",
      "",
      `- **Space:** ${describeSpace(space)}`,
      `- **Parent page:** ${validated.parentId ?? "(the space homepage)"}`,
      "",
      ...notes,
      "## Exact request",
      "",
      "```",
      "POST /wiki/api/v2/pages",
      "```",
      "",
      "```json",
      JSON.stringify(payload, null, 2),
      "```",
      "",
      ...(hasConfluenceWriteToken()
        ? []
        : [
            "> Note: ATLASSIAN_CONFLUENCE_WRITE_TOKEN is not set on this install, so a",
            "> live create would fail at authentication. Dry runs do not need it.",
            "",
          ]),
    ].join("\n");
  }

  let created: ConfluencePage;
  try {
    created = await new ConfluenceClient("write").createPage(payload);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return `Error creating draft: ${message}`;
  }

  const url = draftUrl(created);

  return [
    `Created draft **${payload.title}** (id ${created.id}). It stays ` +
      "unpublished until someone publishes it in Confluence.",
    "",
    `- Space: ${describeSpace(space)}`,
    ...(url ? [`- Link: ${url}`] : []),
    "",
    ...notes,
    await verifyDraft(created.id, payload),
  ].join("\n");
}

const createConfluencePageTool: ToolDefinition = {
  name: "create_confluence_page",
  description:
    "Create an unpublished Confluence draft from markdown (headings, lists, " +
    "tables, code blocks, links), in a space and optionally under a parent " +
    "page. Never guess the space: if the user has not said which space to " +
    "use, ask them. The dry run names the space; show it to the user and get " +
    "their go-ahead before dryRun: false. Only absolute http(s) and " +
    "mailto links are kept; others become plain text and are listed in the " +
    "result. Defaults to a dry run that returns the exact request without " +
    "sending it; pass dryRun: false to create for real. The draft is read back " +
    "to verify it. Requires ATLASSIAN_CONFLUENCE_WRITE_TOKEN for live creation.",
  inputSchema: {
    type: "object",
    properties: {
      spaceId: {
        type: "string",
        description:
          "Numeric id of the space the user named. Ask the user if they have not said.",
        pattern: "^\\d+$",
      },
      title: {
        type: "string",
        description: "Page title. Must be unique within the space.",
        maxLength: 255,
      },
      parentId: {
        type: "string",
        description:
          "Numeric id of the parent page. Omit to create under the space homepage.",
        pattern: "^\\d+$",
      },
      body: {
        type: "string",
        description: "Page body in markdown.",
      },
      dryRun: {
        type: "boolean",
        default: true,
        description:
          "When true (the default), returns the exact request without sending it.",
      },
    },
    required: ["spaceId", "title", "body"],
  },
  handler,
};

export default createConfluencePageTool;
