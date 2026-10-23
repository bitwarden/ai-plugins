/**
 * Link Issues Tool (write, opt-in)
 *
 * Parameters are named by role (`blockerKey` / `blockedKey`) rather than by
 * Jira's inward/outward vocabulary. The direction mapping is applied once, here,
 * so a caller cannot invert it. That removes the failure mode the acli path has
 * to document and guard with an eval case.
 */

import { JiraClient } from "../jira/client.js";
import { hasJiraWriteToken } from "../jira/auth.js";
import {
  validateInput,
  LinkIssuesSchema,
  LinkIssuesInput,
  ToolDefinition,
} from "../utils/validation.js";
import {
  writeTokenDryRunNote,
  writeTokenRefusalMessage,
  isWriteAuthError,
  writeScopeHint,
} from "../utils/write-guard.js";

/**
 * Resolve role-named parameters onto Jira's (inward, outward) pair.
 *
 * For type "Blocks" the create payload reads "inwardIssue blocks
 * outwardIssue", so the blocker is the inward issue and the blocked item the
 * outward issue. See JiraClient.createIssueLink for the live evidence.
 *
 * "Relates" is symmetric (both descriptions are "relates to"), so the ordering
 * of the pair carries no meaning.
 *
 * Exported so the mapping can be tested directly.
 */
export function resolveLinkDirection(input: LinkIssuesInput): {
  typeName: string;
  inwardKey: string;
  outwardKey: string;
} {
  if (input.linkType === "Blocks") {
    return {
      typeName: "Blocks",
      inwardKey: input.blockerKey,
      outwardKey: input.blockedKey,
    };
  }

  return {
    typeName: "Relates",
    inwardKey: input.firstKey,
    outwardKey: input.secondKey,
  };
}

function describeLink(input: LinkIssuesInput): string {
  return input.linkType === "Blocks"
    ? `${input.blockerKey} blocks ${input.blockedKey}`
    : `${input.firstKey} relates to ${input.secondKey}`;
}

/**
 * Read the link back from one end and confirm it landed in the direction the
 * caller asked for. The check is by role, independent of the create mapping,
 * so a wrong mapping cannot pass its own check.
 *
 * On issue X's record, an entry carrying `outwardIssue: Y` reads "X <outward
 * description> Y" and one carrying `inwardIssue: Y` reads "X <inward
 * description> Y". So for Blocks the blocker's record should carry
 * `outwardIssue: blocked` ("blocks"). If it carries `inwardIssue: blocked`
 * instead ("is blocked by"), the link exists but is inverted, and that is
 * reported as such. Relates is symmetric, so either side is accepted.
 *
 * Uses a fresh read-mode client rather than the write client the create call
 * used, so this never requires a read scope on the write token.
 */
async function verifyLink(input: LinkIssuesInput): Promise<string> {
  const [readKey, otherKey] =
    input.linkType === "Blocks"
      ? [input.blockerKey, input.blockedKey]
      : [input.firstKey, input.secondKey];

  try {
    const readClient = new JiraClient("read");
    const issue = await readClient.getIssue(readKey, ["issuelinks"]);
    const links = (issue.fields.issuelinks ?? []).filter(
      (link) => link.type.name === input.linkType,
    );

    if (input.linkType === "Blocks") {
      if (links.some((link) => link.outwardIssue?.key === otherKey)) {
        return `Verified: reading ${readKey} back shows it blocks ${otherKey}.`;
      }

      const inverted = links.find((link) => link.inwardIssue?.key === otherKey);
      if (inverted) {
        return (
          `**Created inverted:** reading ${readKey} back shows link ${inverted.id} ` +
          `as ${otherKey} blocks ${readKey}, the opposite of what was requested. ` +
          `Delete link ${inverted.id} in Jira and recreate it.`
        );
      }
    } else if (
      links.some(
        (link) =>
          link.outwardIssue?.key === otherKey ||
          link.inwardIssue?.key === otherKey,
      )
    ) {
      return `Verified: reading ${readKey} back shows it relates to ${otherKey}.`;
    }

    return (
      `Could not verify: reading ${readKey} back does not show a ` +
      `${input.linkType} link to ${otherKey}. Check Jira's Linked Issues panel.`
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return `Could not verify the link by reading ${readKey} back: ${message}`;
  }
}

async function handler(input: any): Promise<string> {
  const validated = validateInput(LinkIssuesSchema, input);
  const resolved = resolveLinkDirection(validated);

  if (validated.dryRun) {
    const lines = [
      `# Dry run: link ${validated.linkType}`,
      "",
      "No request was sent. Re-run with `dryRun: false` to create this link.",
      "",
      `Reads as: **${describeLink(validated)}**`,
      "",
      "## Exact request",
      "",
      "```",
      "POST /rest/api/3/issueLink",
      "```",
      "",
      "```json",
      JSON.stringify(
        {
          type: { name: resolved.typeName },
          inwardIssue: { key: resolved.inwardKey },
          outwardIssue: { key: resolved.outwardKey },
        },
        null,
        2,
      ),
      "```",
      "",
    ];

    if (!hasJiraWriteToken()) {
      lines.push(...writeTokenDryRunNote("link"));
    }

    return lines.join("\n");
  }

  if (!hasJiraWriteToken()) {
    return writeTokenRefusalMessage("link");
  }

  try {
    const client = new JiraClient("write");
    await client.createIssueLink(resolved);

    const verification = await verifyLink(validated);

    return [`Linked: ${describeLink(validated)}.`, verification].join("\n\n");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);

    return isWriteAuthError(message)
      ? [`Error creating link: ${message}`, "", writeScopeHint()].join("\n")
      : `Error creating link: ${message}`;
  }
}

const linkIssuesTool: ToolDefinition = {
  name: "link_issues",
  description:
    "Link two Jira work items. For a dependency use linkType 'Blocks' with " +
    "blockerKey (the item that must land first) and blockedKey (the item waiting " +
    "on it); the inward/outward mapping is handled internally so direction cannot " +
    "be inverted. Defaults to a dry run. Requires ATLASSIAN_JIRA_WRITE_TOKEN for " +
    "live linking.",
  inputSchema: {
    type: "object",
    properties: {
      linkType: {
        type: "string",
        enum: ["Blocks", "Relates"],
        description:
          "'Blocks' for a hard dependency, 'Relates' for soft or ordering-only.",
      },
      blockerKey: {
        type: "string",
        description:
          "Blocks only: the item that must land first (e.g. PM-12345).",
        pattern: "^[A-Z][A-Z0-9_]+-\\d+$",
      },
      blockedKey: {
        type: "string",
        description: "Blocks only: the item waiting on the blocker.",
        pattern: "^[A-Z][A-Z0-9_]+-\\d+$",
      },
      firstKey: {
        type: "string",
        description: "Relates only: one side of the symmetric relationship.",
        pattern: "^[A-Z][A-Z0-9_]+-\\d+$",
      },
      secondKey: {
        type: "string",
        description: "Relates only: the other side.",
        pattern: "^[A-Z][A-Z0-9_]+-\\d+$",
      },
      dryRun: {
        type: "boolean",
        default: true,
        description:
          "When true (the default), returns the exact payload without sending it.",
      },
    },
    required: ["linkType"],
  },
  handler,
};

export default linkIssuesTool;
