/**
 * Create Issue Tool (write, opt-in)
 *
 * Creates a single Jira work item in any project. Three properties are deliberate:
 *
 *  - `dryRun` defaults to true. Forgetting the flag yields a payload preview,
 *    not a live ticket. Dry runs need no write token at all.
 *  - No project's shape is encoded here. `issueType` is a name Jira resolves,
 *    and anything beyond the common core rides in `fields` keyed by field id.
 *    Use `get_create_fields` to discover those ids for the target project.
 *  - Jira is the validator. Required-field and screen-membership errors come
 *    back from the API verbatim rather than being second-guessed locally.
 */

import { JiraClient } from "../jira/client.js";
import { hasJiraWriteToken } from "../jira/auth.js";
import {
  validateInput,
  CreateIssueSchema,
  CreateIssueInput,
  ToolDefinition,
} from "../utils/validation.js";
import { buildDescriptionAdf } from "../utils/adf-build.js";
import {
  writeTokenDryRunNote,
  writeTokenRefusalMessage,
  isWriteAuthError,
  writeScopeHint,
} from "../utils/write-guard.js";

/**
 * Assemble the Jira `fields` object for a create call.
 *
 * Exported for testing: the payload shape is the whole contract, so it is worth
 * asserting directly rather than only through a mocked HTTP call.
 */
export function buildCreateFields(
  input: CreateIssueInput,
): Record<string, unknown> {
  // Passthrough first, so a named parameter wins on collision. The schema already
  // rejects reserved keys, so this ordering is a redundant safeguard.
  const fields: Record<string, unknown> = { ...input.fields };

  fields.project = { key: input.project };
  fields.issuetype = { name: input.issueType };
  fields.summary = input.summary;

  const description = buildDescriptionAdf(input.descriptionParagraphs);
  if (description) {
    fields.description = description;
  }

  if (input.parentKey) {
    fields.parent = { key: input.parentKey };
  }

  if (input.labels.length > 0) {
    fields.labels = input.labels;
  }

  return fields;
}

function renderDryRun(
  input: CreateIssueInput,
  fields: Record<string, unknown>,
): string {
  const extraKeys = Object.keys(input.fields);

  const lines: string[] = [
    `# Dry run: create ${input.issueType} in ${input.project}`,
    "",
    "No request was sent. Re-run with `dryRun: false` to create this item.",
    "",
    "## Summary of what would be created",
    "",
    `- **Project:** ${input.project}`,
    `- **Type:** ${input.issueType}`,
    `- **Summary:** ${input.summary}`,
    `- **Parent:** ${input.parentKey ?? "(none)"}`,
    `- **Labels:** ${input.labels.length > 0 ? input.labels.join(", ") : "(none)"}`,
    `- **Description paragraphs:** ${input.descriptionParagraphs.length}`,
    `- **Additional fields:** ${extraKeys.length > 0 ? extraKeys.join(", ") : "(none)"}`,
    "",
    "## Exact request",
    "",
    "```",
    "POST /rest/api/3/issue",
    "```",
    "",
    "```json",
    JSON.stringify({ fields }, null, 2),
    "```",
    "",
  ];

  if (extraKeys.length === 0) {
    lines.push(
      "> No additional fields were supplied. If this project requires any, or has " +
        "a field this item should populate (an acceptance-criteria field, for " +
        "example), check `get_create_fields` for " +
        `${input.project} / ${input.issueType} first.`,
      "",
    );
  }

  if (!hasJiraWriteToken()) {
    lines.push(...writeTokenDryRunNote("create"));
  }

  return lines.join("\n");
}

async function handler(input: any): Promise<string> {
  const validated = validateInput(CreateIssueSchema, input);
  const fields = buildCreateFields(validated);

  if (validated.dryRun) {
    return renderDryRun(validated, fields);
  }

  if (!hasJiraWriteToken()) {
    return writeTokenRefusalMessage("create");
  }

  try {
    const client = new JiraClient("write");
    const created = await client.createIssue(fields);

    return [
      `Created **${created.key}** (${validated.issueType} in ${validated.project}).`,
      "",
      `- Summary: ${validated.summary}`,
      `- Parent: ${validated.parentKey ?? "(none)"}`,
      `- Id: ${created.id}`,
    ].join("\n");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);

    if (isWriteAuthError(message)) {
      return [`Error creating issue: ${message}`, "", writeScopeHint()].join(
        "\n",
      );
    }

    return [
      `Error creating issue: ${message}`,
      "",
      "If this names a required or unavailable field, read the create screen " +
        `with get_create_fields for ${validated.project} / ${validated.issueType} ` +
        "and retry with the corrected `fields`.",
    ].join("\n");
  }
}

const createIssueTool: ToolDefinition = {
  name: "create_issue",
  description:
    "Create a single Jira work item in any project. Defaults to a dry run that " +
    "returns the exact payload without sending it; pass dryRun: false to create " +
    "for real. Projects differ in their issue types and required fields, so call " +
    "get_create_fields first and pass anything project-specific through `fields`. " +
    "Requires ATLASSIAN_JIRA_WRITE_TOKEN for live creation.",
  inputSchema: {
    type: "object",
    properties: {
      project: {
        type: "string",
        description: "Project key, e.g. PM, SM, QA, VULN, PLT.",
      },
      issueType: {
        type: "string",
        description:
          "Issue type name as it exists in that project, e.g. Story, Task, " +
          "Security, 'Platform Initiative'. Jira resolves and validates it.",
      },
      summary: {
        type: "string",
        description:
          "Ticket title: imperative verb, outcome, and area. Not a decomposition label.",
        maxLength: 255,
      },
      descriptionParagraphs: {
        type: "array",
        items: { type: "string" },
        description: "Description body as paragraphs of plain text.",
      },
      parentKey: {
        type: "string",
        description: "Parent key, e.g. an epic to file this item under.",
        pattern: "^[A-Z][A-Z0-9_]+-\\d+$",
      },
      labels: {
        type: "array",
        items: { type: "string" },
        description: "Labels to apply.",
      },
      fields: {
        type: "object",
        description:
          "Additional fields keyed by Jira field id (e.g. customfield_10192), " +
          "merged into the payload as-is. Discover ids and allowed values with " +
          "get_create_fields. Do not pass project, issuetype, summary, " +
          "description, parent, or labels here; they have their own parameters.",
        additionalProperties: true,
      },
      dryRun: {
        type: "boolean",
        default: true,
        description:
          "When true (the default), returns the exact payload without sending it.",
      },
    },
    required: ["project", "issueType", "summary"],
  },
  handler,
};

export default createIssueTool;
