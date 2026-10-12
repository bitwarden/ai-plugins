/**
 * Get Create Fields Tool (read-only)
 *
 * Answers "what does this project need in order to create this kind of item?"
 * from Jira itself, so no project's field IDs, required fields, or option values
 * have to be hardcoded here or remembered in a skill.
 *
 * Bitwarden's projects differ from one another. PM and SM expose an Acceptance
 * criteria field, QA and VULN do not. VULN has no Story type. PLT's only
 * creatable type is "Platform Initiative".
 */

import { JiraClient } from "../jira/client.js";
import {
  validateInput,
  GetCreateFieldsSchema,
  ToolDefinition,
} from "../utils/validation.js";
import type { JiraCreateMetaField } from "../jira/types.js";

// Jira's own createmeta 404 carries no body, so this is the Jira UI's typical
// wording for a permission denial rather than something extracted from the response.
const NO_CREATE_PERMISSION = "You cannot create issues in this project";

function renderIssueTypes(
  project: string,
  issueTypes: Array<{ id: string; name: string; subtask: boolean }>,
): string {
  const lines = [`# Creatable issue types in ${project}`, ""];

  const standard = issueTypes.filter((t) => !t.subtask);
  const subtasks = issueTypes.filter((t) => t.subtask);

  for (const t of standard) {
    lines.push(`- **${t.name}** (id ${t.id})`);
  }
  if (subtasks.length > 0) {
    lines.push("", "Sub-task types:");
    for (const t of subtasks) {
      lines.push(`- **${t.name}** (id ${t.id})`);
    }
  }

  lines.push(
    "",
    "Call again with `issueType` to see that type's fields and requirements.",
  );

  return lines.join("\n");
}

function renderField(field: JiraCreateMetaField): string {
  const flags = [field.required ? "required" : "optional"];
  if (field.hasDefaultValue) {
    flags.push("has default");
  }
  flags.push(`type ${field.schema?.type ?? "unknown"}`);

  let line = `- \`${field.fieldId}\` **${field.name}** (${flags.join(", ")})`;

  if (field.allowedValues && field.allowedValues.length > 0) {
    const values = field.allowedValues
      .map((v) => v.value ?? v.name ?? v.id)
      .filter(Boolean);
    if (values.length > 0) {
      line += `\n  - allowed: ${values.join(", ")}`;
    }
  }

  return line;
}

function renderFields(
  project: string,
  issueTypeName: string,
  issueTypeId: string,
  fields: JiraCreateMetaField[],
): string {
  const required = fields.filter((f) => f.required);
  const optional = fields.filter((f) => !f.required);

  const lines = [
    `# ${project} / ${issueTypeName} create screen`,
    "",
    `Issue type id ${issueTypeId}. ${fields.length} fields on the screen.`,
    "",
    "## Required",
    "",
  ];

  if (required.length === 0) {
    lines.push("(none)");
  } else {
    lines.push(...required.map(renderField));
  }

  lines.push("", "## Optional", "");
  lines.push(...optional.map(renderField));
  lines.push(
    "",
    "Pass any of these to `create_issue` via `fields`, keyed by field id. " +
      "`project`, `issuetype`, `summary`, `description`, `parent`, and `labels` " +
      "have their own parameters.",
  );

  return lines.join("\n");
}

async function handler(input: any): Promise<string> {
  const validated = validateInput(GetCreateFieldsSchema, input);
  const client = new JiraClient();

  let issueTypes;
  try {
    const meta = await client.getCreateMetaIssueTypes(validated.project);
    issueTypes = meta.issueTypes ?? [];
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (message.includes("not found") || message.includes("404")) {
      return (
        `Cannot read the create screen for ${validated.project}.\n\n` +
        `This project may not exist, or the authenticated user may lack create ` +
        `permission in it (Jira's UI describes the latter as "${NO_CREATE_PERMISSION}"). ` +
        `This is expected for projects the authenticated user cannot create in ` +
        `(for example AC and ARCH).`
      );
    }
    return `Error reading create metadata: ${message}`;
  }

  if (issueTypes.length === 0) {
    return `${validated.project} reports no creatable issue types for this user.`;
  }

  if (!validated.issueType) {
    return renderIssueTypes(validated.project, issueTypes);
  }

  const wanted = validated.issueType.toLowerCase();
  const match = issueTypes.find((t) => t.name.toLowerCase() === wanted);

  if (!match) {
    return [
      `${validated.project} has no issue type named "${validated.issueType}".`,
      "",
      "Available:",
      ...issueTypes.map((t) => `- ${t.name}`),
    ].join("\n");
  }

  try {
    const { fields } = await client.getCreateMetaFields(
      validated.project,
      match.id,
    );

    return renderFields(validated.project, match.name, match.id, fields ?? []);
  } catch (error) {
    return `Error reading fields for ${match.name}: ${error instanceof Error ? error.message : String(error)}`;
  }
}

const getCreateFieldsTool: ToolDefinition = {
  name: "get_create_fields",
  description:
    "Discover what a Jira project needs to create a work item: its creatable " +
    "issue types, and for a given type, every field on the create screen with " +
    "its field id, whether it is required, and its allowed values. Read-only. " +
    "Use this before create_issue instead of assuming any project's field " +
    "layout, since Bitwarden's projects differ from one another.",
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
          "Issue type name, e.g. Story or 'Platform Initiative'. Omit to list " +
          "the project's creatable types.",
      },
    },
    required: ["project"],
  },
  handler,
};

export default getCreateFieldsTool;
