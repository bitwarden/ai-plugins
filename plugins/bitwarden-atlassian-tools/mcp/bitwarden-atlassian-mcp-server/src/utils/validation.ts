/**
 * Input validation schemas using Zod
 * Ensures type safety and validation for tool parameters
 */

import { z } from 'zod';

/**
 * Schema for search_issues tool parameters
 */
export const SearchIssuesSchema = z.object({
  jql: z.string().min(1, 'JQL query cannot be empty'),
  startAt: z.number().int().min(0).optional().default(0),
  maxResults: z.number().int().min(1).max(100).optional().default(50),
  fields: z.array(z.string()).optional(),
  expand: z.array(z.string()).optional(),
});

export type SearchIssuesInput = z.infer<typeof SearchIssuesSchema>;

/**
 * Schema for get_issue tool parameters
 */
export const GetIssueSchema = z.object({
  issueIdOrKey: z.string().min(1, 'Issue ID or key is required'),
  fields: z.array(z.string()).optional(),
  expand: z.array(z.string()).optional(),
});

export type GetIssueInput = z.infer<typeof GetIssueSchema>;

/**
 * Schema for get_issue_comments tool parameters
 */
export const GetIssueCommentsSchema = z.object({
  issueIdOrKey: z.string().min(1, 'Issue ID or key is required'),
  startAt: z.number().int().min(0).optional().default(0),
  maxResults: z.number().int().min(1).max(100).optional().default(50),
});

export type GetIssueCommentsInput = z.infer<typeof GetIssueCommentsSchema>;

/**
 * Schema for get_confluence_page tool parameters
 */
export const GetConfluencePageSchema = z.object({
  pageId: z.string().min(1, 'Page ID is required'),
  includeBody: z.boolean().optional().default(true),
  bodyFormat: z.enum(['storage', 'view', 'export_view']).optional().default('storage'),
});

export type GetConfluencePageInput = z.infer<typeof GetConfluencePageSchema>;

/**
 * Schema for search_confluence tool parameters
 */
export const SearchConfluenceSchema = z.object({
  spaceKey: z.string().optional(),
  title: z.string().optional(),
  limit: z.number().int().min(1).max(250).optional().default(25),
  cursor: z.string().optional(),
});

export type SearchConfluenceInput = z.infer<typeof SearchConfluenceSchema>;

/**
 * Schema for get_confluence_page_comments tool parameters
 */
export const GetConfluencePageCommentsSchema = z.object({
  pageId: z.string().min(1, 'Page ID is required'),
  bodyFormat: z.enum(['storage', 'view']).optional().default('storage'),
  limit: z.number().int().min(1).max(100).optional().default(25),
  includeReplies: z.boolean().optional().default(true),
});

export type GetConfluencePageCommentsInput = z.infer<typeof GetConfluencePageCommentsSchema>;

/**
 * Schema for download_attachment tool parameters
 */
export const DownloadAttachmentSchema = z.object({
  attachmentUrl: z.string()
    .url('Must be a valid URL')
    .regex(/\/secure\/attachment\/|\/rest\/api\/.*\/attachment\//,
           'Must be a JIRA attachment URL'),
  maxSizeMB: z.number()
    .int()
    .min(1)
    .max(50)
    .optional()
    .default(10),
});

export type DownloadAttachmentInput = z.infer<typeof DownloadAttachmentSchema>;

// ── New Agile & Confluence Tool Schemas ──────────────────────────────

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
  boardId: z.number().int().min(1, 'Board ID is required'),
  state: z.enum(['active', 'closed', 'future']).optional(),
  maxResults: z.number().int().min(1).max(100).optional().default(50),
});

export type GetSprintsInput = z.infer<typeof GetSprintsSchema>;

/**
 * Schema for get_sprint_issues tool parameters
 */
export const GetSprintIssuesSchema = z.object({
  sprintId: z.number().int().min(1, 'Sprint ID is required'),
  fields: z.array(z.string()).optional(),
  maxResults: z.number().int().min(1).max(100).optional().default(50),
});

export type GetSprintIssuesInput = z.infer<typeof GetSprintIssuesSchema>;

/**
 * Schema for list_projects tool parameters
 */
export const ListProjectsSchema = z.object({
  maxResults: z.number().int().min(1).max(100).optional().default(50),
});

export type ListProjectsInput = z.infer<typeof ListProjectsSchema>;

/**
 * Schema for get_child_pages tool parameters
 */
export const GetChildPagesSchema = z.object({
  pageId: z.string().min(1, 'Page ID is required'),
  limit: z.number().int().min(1).max(250).optional().default(25),
});

export type GetChildPagesInput = z.infer<typeof GetChildPagesSchema>;

/**
 * Schema for list_spaces tool parameters
 */
export const ListSpacesSchema = z.object({
  limit: z.number().int().min(1).max(250).optional().default(25),
  type: z.string().optional(),
});

export type ListSpacesInput = z.infer<typeof ListSpacesSchema>;

/**
 * Schema for search_confluence_cql tool parameters
 */
export const SearchConfluenceCqlSchema = z.object({
  cql: z.string().min(1, 'CQL query is required'),
  limit: z.number().int().min(1).max(100).optional().default(10),
  start: z.number().int().min(0).optional().default(0),
});

export type SearchConfluenceCqlInput = z.infer<typeof SearchConfluenceCqlSchema>;

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
      const messages = error.errors.map(e => `${e.path.join('.')}: ${e.message}`);
      throw new Error(`Validation failed: ${messages.join(', ')}`);
    }
    throw error;
  }
}
