/**
 * Transition Issue Tool (write, opt-in)
 *
 * Moves an issue to a target status by the status's name. The caller names
 * where the issue should end up, and the tool finds the transition that gets
 * it there, so no workflow knowledge is needed up front. An issue already in
 * the target status is a no-op rather than an error, which keeps the tool safe
 * to call repeatedly from automation.
 *
 * The current status and available transitions are read with the read-only
 * token, so a dry run is accurate on a read-only install. Only the transition
 * itself uses ATLASSIAN_JIRA_WRITE_TOKEN.
 */

import { JiraClient } from "../jira/client.js";
import { hasJiraWriteToken } from "../jira/auth.js";
import {
  validateInput,
  TransitionIssueSchema,
  ToolDefinition,
} from "../utils/validation.js";
import {
  writeTokenDryRunNote,
  writeTokenRefusalMessage,
  isWriteAuthError,
  writeScopeHint,
} from "../utils/write-guard.js";

function sameStatus(a: string, b: string): boolean {
  return a.toLowerCase() === b.toLowerCase();
}

async function readStatus(
  client: JiraClient,
  issueIdOrKey: string,
): Promise<string> {
  const issue = await client.getIssue(issueIdOrKey, ["status"]);
  return issue.fields.status.name;
}

/**
 * Read the status back after a live transition. Uses a fresh read-mode client
 * so this never requires a read scope on the write token.
 */
async function verifyStatus(
  issueIdOrKey: string,
  want: string,
): Promise<string> {
  try {
    const now = await readStatus(new JiraClient("read"), issueIdOrKey);

    return sameStatus(now, want)
      ? `Verified: reading ${issueIdOrKey} back shows status ${now}.`
      : `Could not verify: reading ${issueIdOrKey} back shows status ${now}, not ${want}. ` +
          "A workflow post-function may have moved it on; check the issue's history in Jira.";
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return `Could not verify the transition by reading ${issueIdOrKey} back: ${message}`;
  }
}

async function handler(input: any): Promise<string> {
  const { issueIdOrKey, status, dryRun } = validateInput(
    TransitionIssueSchema,
    input,
  );

  const readClient = new JiraClient("read");
  const current = await readStatus(readClient, issueIdOrKey);

  if (sameStatus(current, status)) {
    return `${issueIdOrKey} is already in ${current}. Nothing to do.`;
  }

  const transitions = await readClient.getTransitions(issueIdOrKey);
  const transition = transitions.find((t) => sameStatus(t.to.name, status));

  if (!transition) {
    const reachable = [...new Set(transitions.map((t) => t.to.name))];

    return [
      `No transition from ${current} to ${status} is available on ${issueIdOrKey}.`,
      "",
      reachable.length > 0
        ? `Statuses reachable from ${current}: ${reachable.join(", ")}.`
        : `No transitions are available from ${current} for this user.`,
    ].join("\n");
  }

  const target = transition.to.name;

  if (dryRun) {
    const lines = [
      `# Dry run: transition ${issueIdOrKey}`,
      "",
      "No request was sent. Re-run with `dryRun: false` to apply this transition.",
      "",
      `Moves **${current}** -> **${target}** via transition "${transition.name}" (id ${transition.id}).`,
      "",
      "## Exact request",
      "",
      "```",
      `POST /rest/api/3/issue/${issueIdOrKey}/transitions`,
      "```",
      "",
      "```json",
      JSON.stringify({ transition: { id: transition.id } }, null, 2),
      "```",
      "",
    ];

    if (!hasJiraWriteToken()) {
      lines.push(...writeTokenDryRunNote("transition"));
    }

    return lines.join("\n");
  }

  if (!hasJiraWriteToken()) {
    return writeTokenRefusalMessage("transition");
  }

  try {
    const client = new JiraClient("write");
    await client.transitionIssue(issueIdOrKey, transition.id);

    const verification = await verifyStatus(issueIdOrKey, target);

    return [
      `Transitioned **${issueIdOrKey}**: ${current} -> ${target}.`,
      verification,
    ].join("\n\n");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);

    return isWriteAuthError(message)
      ? [`Error transitioning issue: ${message}`, "", writeScopeHint()].join(
          "\n",
        )
      : `Error transitioning issue: ${message}`;
  }
}

const transitionIssueTool: ToolDefinition = {
  name: "transition_issue",
  description:
    "Move a Jira issue to a target status by name (e.g. 'In Progress', 'Done'). " +
    "Finds the workflow transition that reaches that status from the current one; " +
    "an issue already in the target status is left alone. Defaults to a dry run " +
    "that reports the transition it would apply. Requires " +
    "ATLASSIAN_JIRA_WRITE_TOKEN for a live transition.",
  inputSchema: {
    type: "object",
    properties: {
      issueIdOrKey: {
        type: "string",
        description: "Jira issue key, e.g. PM-12345.",
        pattern: "^[A-Z][A-Z0-9_]+-\\d+$",
      },
      status: {
        type: "string",
        description:
          "Name of the status to move the issue to, matched case-insensitively.",
      },
      dryRun: {
        type: "boolean",
        default: true,
        description:
          "When true (the default), returns the transition it would apply without sending it.",
      },
    },
    required: ["issueIdOrKey", "status"],
  },
  handler,
};

export default transitionIssueTool;
