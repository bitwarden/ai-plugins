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

/**
 * Resolve role-named parameters onto Jira's (outward, inward) pair.
 *
 * For type "Blocks" the link type's descriptions are outward "blocks" and
 * inward "is blocked by", and the payload reads
 * "outwardIssue <outward> inwardIssue". So the blocker is the outward issue.
 * Verified read-only against a real PM link; see JiraClient.createIssueLink.
 *
 * "Relates" is symmetric (both descriptions are "relates to"), so the ordering
 * of the pair carries no meaning.
 *
 * Exported so the mapping can be tested directly.
 */
export function resolveLinkDirection(input: LinkIssuesInput): {
  typeName: string;
  outwardKey: string;
  inwardKey: string;
} {
  if (input.linkType === "Blocks") {
    return {
      typeName: "Blocks",
      outwardKey: input.blockerKey,
      inwardKey: input.blockedKey,
    };
  }

  return {
    typeName: "Relates",
    outwardKey: input.firstKey,
    inwardKey: input.secondKey,
  };
}

function describeLink(input: LinkIssuesInput): string {
  return input.linkType === "Blocks"
    ? `${input.blockerKey} blocks ${input.blockedKey}`
    : `${input.firstKey} relates to ${input.secondKey}`;
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
          outwardIssue: { key: resolved.outwardKey },
          inwardIssue: { key: resolved.inwardKey },
        },
        null,
        2,
      ),
      "```",
      "",
    ];

    if (!hasJiraWriteToken()) {
      lines.push(
        "> Note: ATLASSIAN_JIRA_WRITE_TOKEN is not set on this install, so a live",
        "> link would fail at authentication. Dry runs do not need it.",
        "",
      );
    }

    return lines.join("\n");
  }

  if (!hasJiraWriteToken()) {
    return (
      "Refusing to link: ATLASSIAN_JIRA_WRITE_TOKEN is not set.\n\n" +
      "This install has read-only credentials. Call with dryRun: true to preview " +
      "the payload."
    );
  }

  try {
    const client = new JiraClient("write");
    await client.createIssueLink(resolved);

    return `Linked: ${describeLink(validated)}. Verify in Jira's Linked Issues panel.`;
  } catch (error) {
    return `Error creating link: ${error instanceof Error ? error.message : String(error)}`;
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
