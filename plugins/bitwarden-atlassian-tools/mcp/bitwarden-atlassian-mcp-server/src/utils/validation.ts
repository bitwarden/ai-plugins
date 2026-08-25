/**
 * Input validation schemas using Zod
 * Ensures type safety and validation for tool parameters
 */

import { z } from "zod";

/**
 * Shape of a tool module's default export.
 * Each tool file exports a ToolDefinition with metadata and a handler function.
 */
export interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: any;
  handler: (input: any) => Promise<any>;
}

/**
 * Schema for get_issue tool parameters
 */
export const GetIssueSchema = z.object({
  issueIdOrKey: z
    .string()
    .regex(
      /^[A-Z][A-Z0-9_]+-\d+$|^\d+$/,
      "Must be a valid Jira issue key (e.g., PROJ-123) or numeric ID",
    ),
  fields: z.array(z.string()).optional(),
  expand: z.array(z.string()).optional(),
});

export type GetIssueInput = z.infer<typeof GetIssueSchema>;

/**
 * Schema for get_issue_comments tool parameters
 */
export const GetIssueCommentsSchema = z.object({
  issueIdOrKey: z
    .string()
    .regex(
      /^[A-Z][A-Z0-9_]+-\d+$|^\d+$/,
      "Must be a valid Jira issue key (e.g., PROJ-123) or numeric ID",
    ),
  startAt: z.number().int().min(0).optional().default(0),
  maxResults: z.number().int().min(1).max(100).optional().default(50),
});

export type GetIssueCommentsInput = z.infer<typeof GetIssueCommentsSchema>;

/**
 * Schema for search_issues tool parameters
 */
export const SearchIssuesSchema = z.object({
  jql: z.string().min(1, "JQL query cannot be empty"),
  maxResults: z.number().int().min(1).max(100).optional().default(50),
  fields: z.array(z.string()).optional(),
  expand: z.array(z.string()).optional(),
  nextPageToken: z.string().optional(),
});

export type SearchIssuesInput = z.infer<typeof SearchIssuesSchema>;

/**
 * Schema for list_projects tool parameters
 */
export const ListProjectsSchema = z.object({
  maxResults: z.number().int().min(1).max(100).optional().default(50),
});

export type ListProjectsInput = z.infer<typeof ListProjectsSchema>;

/**
 * Schema for list_boards tool parameters
 */
export const ListBoardsSchema = z.object({
  projectKeyOrId: z.string().optional(),
  maxResults: z.number().int().min(1).max(100).optional().default(50),
});

export type ListBoardsInput = z.infer<typeof ListBoardsSchema>;

/**
 * Schema for get_sprints tool parameters
 */
export const GetSprintsSchema = z.object({
  boardId: z.number().int().positive(),
  state: z.enum(["active", "future", "closed"]).optional(),
  maxResults: z.number().int().min(1).max(100).optional().default(50),
});

export type GetSprintsInput = z.infer<typeof GetSprintsSchema>;

/**
 * Schema for get_sprint_issues tool parameters
 */
export const GetSprintIssuesSchema = z.object({
  sprintId: z.number().int().positive(),
  fields: z.array(z.string()).optional(),
  maxResults: z.number().int().min(1).max(100).optional().default(50),
});

export type GetSprintIssuesInput = z.infer<typeof GetSprintIssuesSchema>;

// ── Confluence Schemas ───────────────────────────────────────────────

export const GetConfluencePageSchema = z.object({
  pageId: z.string().min(1, "Page ID is required"),
  includeBody: z.boolean().optional().default(true),
  bodyFormat: z
    .enum(["storage", "view", "export_view"])
    .optional()
    .default("storage"),
});

export type GetConfluencePageInput = z.infer<typeof GetConfluencePageSchema>;

export const GetConfluencePageCommentsSchema = z.object({
  pageId: z.string().min(1, "Page ID is required"),
  bodyFormat: z.enum(["storage"]).optional().default("storage"),
  limit: z.number().int().min(1).max(100).optional().default(25),
  includeReplies: z.boolean().optional().default(true),
});

export type GetConfluencePageCommentsInput = z.infer<
  typeof GetConfluencePageCommentsSchema
>;

export const GetChildPagesSchema = z.object({
  pageId: z.string().min(1, "Page ID is required"),
  limit: z.number().int().min(1).max(250).optional().default(25),
});

export type GetChildPagesInput = z.infer<typeof GetChildPagesSchema>;

export const SearchConfluenceSchema = z.object({
  spaceKey: z.string().optional(),
  title: z.string().optional(),
  limit: z.number().int().min(1).max(250).optional().default(25),
  cursor: z.string().optional(),
});

export type SearchConfluenceInput = z.infer<typeof SearchConfluenceSchema>;

export const SearchConfluenceCqlSchema = z.object({
  cql: z.string().min(1, "CQL query is required"),
  limit: z.number().int().min(1).max(100).optional().default(10),
  start: z.number().int().min(0).optional().default(0),
});

export type SearchConfluenceCqlInput = z.infer<
  typeof SearchConfluenceCqlSchema
>;

export const ListSpacesSchema = z.object({
  limit: z.number().int().min(1).max(250).optional().default(25),
  type: z.string().optional(),
});

export type ListSpacesInput = z.infer<typeof ListSpacesSchema>;

// ── Confluence Write Schemas (opt-in, require ATLASSIAN_CONFLUENCE_WRITE_TOKEN) ─

/**
 * A Confluence page id is a numeric string. Unlike the read tools' `min(1)`,
 * the write tools interpolate the id into a REST path, so an unconstrained
 * string would let a caller redirect the request to a different path.
 */
const ConfluencePageId = z
  .string()
  .regex(/^\d+$/, "Must be a numeric Confluence page id (e.g. 2923724969)");

/**
 * A parsed ADF document. Validated only as far as `type: "doc"` with a `content`
 * array; the node tree itself is passed through untouched, since the caller is
 * expected to have edited a body previously fetched with get_confluence_page_adf.
 */
const AdfDocument = z
  .record(z.string(), z.unknown())
  .refine(
    (v) =>
      v.type === "doc" && Array.isArray((v as Record<string, unknown>).content),
    'ADF body must be a document node with type "doc" and a content array',
  );

export const GetConfluencePageAdfSchema = z.object({
  pageId: ConfluencePageId,
});

export type GetConfluencePageAdfInput = z.infer<
  typeof GetConfluencePageAdfSchema
>;

export const ListConfluenceAnchorsSchema = z.object({
  pageId: ConfluencePageId,
});

export type ListConfluenceAnchorsInput = z.infer<
  typeof ListConfluenceAnchorsSchema
>;

export const ReplaceConfluenceTextSchema = z.object({
  pageId: ConfluencePageId,
  oldText: z.string().min(1, "oldText cannot be empty"),
  newText: z.string(),
  message: z.string().optional(),
  /**
   * Defaults to true. A live edit requires an explicit `dryRun: false`, so a
   * forgotten flag previews the change instead of writing it.
   */
  dryRun: z.boolean().optional().default(true),
});

export type ReplaceConfluenceTextInput = z.infer<
  typeof ReplaceConfluenceTextSchema
>;

export const UpdateConfluencePageSchema = z.object({
  pageId: ConfluencePageId,
  adfBody: AdfDocument,
  /**
   * The page version `adfBody` was derived from, as reported by
   * get_confluence_page_adf. This workflow spans two tool calls with model
   * editing in between, so the live page can move underneath the edit; when
   * given, the tool refuses to write if the live version no longer matches,
   * turning a silent lost update into a re-fetch prompt. Omitting it keeps the
   * old last-write-wins behavior.
   */
  expectedVersion: z.number().int().min(1).optional(),
  message: z.string().optional(),
  dryRun: z.boolean().optional().default(true),
});

export type UpdateConfluencePageInput = z.infer<
  typeof UpdateConfluencePageSchema
>;

export const DownloadAttachmentSchema = z.object({
  attachmentUrl: z
    .string()
    .url("Must be a valid URL")
    .refine((url) => {
      try {
        const { pathname } = new URL(url);
        return /\/secure\/attachment\/|\/rest\/api\/.*\/attachment\//.test(
          pathname,
        );
      } catch {
        return false;
      }
    }, "Must be a JIRA attachment URL path")
    .refine((url) => {
      try {
        const { hostname } = new URL(url);
        return (
          hostname.endsWith(".atlassian.net") && hostname !== ".atlassian.net"
        );
      } catch {
        return false;
      }
    }, "Attachment URL must be an *.atlassian.net hostname"),
  maxSizeMB: z.number().int().min(1).max(50).optional().default(10),
});

export type DownloadAttachmentInput = z.infer<typeof DownloadAttachmentSchema>;

export const GetIssueRemoteLinksSchema = z.object({
  issueIdOrKey: z
    .string()
    .regex(
      /^[A-Z][A-Z0-9_]+-\d+$|^\d+$/,
      "Must be a valid Jira issue key (e.g., PROJ-123) or numeric ID",
    ),
});

export type GetIssueRemoteLinksInput = z.infer<
  typeof GetIssueRemoteLinksSchema
>;

// ── Write Schemas (opt-in, require ATLASSIAN_JIRA_WRITE_TOKEN) ────────

const JiraIssueKey = z
  .string()
  .regex(
    /^[A-Z][A-Z0-9_]+-\d+$/,
    "Must be a valid Jira issue key (e.g. PM-123)",
  );

/**
 * `project` is interpolated directly into a createmeta REST path, so unlike
 * `CreateIssueSchema.project` (which only ever lands in a JSON body), an
 * unconstrained string here would let a caller redirect the request to a
 * different path on the same host.
 */
const JiraProjectKey = z
  .string()
  .regex(/^[A-Z][A-Z0-9_]+$/, "Must be a valid Jira project key (e.g. PM)");

/**
 * Field keys owned by named parameters. Passing them inside `fields` would make
 * two sources of truth for the same value, so they are rejected there.
 */
export const RESERVED_FIELD_KEYS = [
  "project",
  "issuetype",
  "summary",
  "description",
  "parent",
  "labels",
] as const;

/**
 * Create parameters carry no project-specific knowledge.
 *
 * Bitwarden files into many projects (PM, SM, QA, VULN, PLT, and more), and they
 * do not agree on issue types, screen fields, or which fields are required. A
 * team-managed project can also scope custom fields to itself. So rather than
 * enumerate any project's shape here:
 *
 *  - `issueType` is a free-form name. Jira resolves it against the project and
 *    rejects it if absent, which is validation we do not need to duplicate.
 *  - everything beyond the common core goes through `fields` untouched, and Jira
 *    is the authority on what is required and what is on the screen.
 *  - `get_create_fields` exists to discover a project's shape when drafting.
 */
export const CreateIssueSchema = z.object({
  project: JiraProjectKey,
  issueType: z
    .string()
    .min(
      1,
      "Issue type name is required (e.g. Story, Task, Platform Initiative)",
    ),
  summary: z
    .string()
    .min(1, "Summary cannot be empty")
    .max(255, "Jira summaries are limited to 255 characters"),
  /** Description body as paragraphs of plain text, converted to ADF. */
  descriptionParagraphs: z.array(z.string().min(1)).optional().default([]),
  /** Parent key, for a child of an epic. */
  parentKey: JiraIssueKey.optional(),
  labels: z.array(z.string().min(1)).optional().default([]),
  /**
   * Arbitrary additional fields, merged into the create payload as-is. Keys are
   * Jira field IDs (e.g. `customfield_10192`) discovered via `get_create_fields`
   * for the target project, not assumed.
   */
  fields: z
    .record(z.string(), z.unknown())
    .optional()
    .default({})
    .refine(
      (value) =>
        !Object.keys(value).some((key) =>
          (RESERVED_FIELD_KEYS as readonly string[]).includes(key),
        ),
      `These keys have named parameters and must not be passed in fields: ${RESERVED_FIELD_KEYS.join(", ")}`,
    ),
  /**
   * Defaults to true. A live create requires an explicit `dryRun: false`, so
   * the failure mode of forgetting the flag is a preview, not a ticket.
   */
  dryRun: z.boolean().optional().default(true),
});

export type CreateIssueInput = z.infer<typeof CreateIssueSchema>;

/**
 * Read the create screen for a project + issue type, so a caller can discover
 * required fields, field IDs, and allowed values instead of hardcoding them.
 */
export const GetCreateFieldsSchema = z.object({
  project: JiraProjectKey,
  issueType: z
    .string()
    .min(1)
    .optional()
    .describe("Issue type name. Omit to list the project's creatable types."),
});

export type GetCreateFieldsInput = z.infer<typeof GetCreateFieldsSchema>;

/**
 * Link parameters are named by role rather than by Jira's inward/outward
 * vocabulary, so the caller cannot invert the direction. The inward/outward
 * mapping is applied once, in the client.
 */
export const LinkIssuesSchema = z.discriminatedUnion("linkType", [
  z.object({
    linkType: z.literal("Blocks"),
    blockerKey: JiraIssueKey,
    blockedKey: JiraIssueKey,
    dryRun: z.boolean().optional().default(true),
  }),
  z.object({
    linkType: z.literal("Relates"),
    firstKey: JiraIssueKey,
    secondKey: JiraIssueKey,
    dryRun: z.boolean().optional().default(true),
  }),
]);

export type LinkIssuesInput = z.infer<typeof LinkIssuesSchema>;

/**
 * Validate input against a Zod schema
 * @param schema - Zod schema to validate against
 * @param input - Input data to validate
 * @returns Validated and typed data
 * @throws {Error} If validation fails
 */
export function validateInput<T>(schema: z.ZodSchema<T>, input: unknown): T {
  try {
    return schema.parse(input);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const messages = error.issues.map(
        (e) => `${e.path.join(".")}: ${e.message}`,
      );
      throw new Error(`Validation failed: ${messages.join(", ")}`);
    }
    throw error;
  }
}
