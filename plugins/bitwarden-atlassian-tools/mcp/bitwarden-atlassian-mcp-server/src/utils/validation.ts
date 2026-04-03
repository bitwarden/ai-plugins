/**
 * Input validation schemas using Zod
 * Ensures type safety and validation for tool parameters
 */

import { z } from 'zod';

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
  issueIdOrKey: z.string().regex(
    /^[A-Z][A-Z0-9_]+-\d+$|^\d+$/,
    'Must be a valid Jira issue key (e.g., PROJ-123) or numeric ID'
  ),
  fields: z.array(z.string()).optional(),
  expand: z.array(z.string()).optional(),
});

export type GetIssueInput = z.infer<typeof GetIssueSchema>;

/**
 * Schema for get_issue_comments tool parameters
 */
export const GetIssueCommentsSchema = z.object({
  issueIdOrKey: z.string().regex(
    /^[A-Z][A-Z0-9_]+-\d+$|^\d+$/,
    'Must be a valid Jira issue key (e.g., PROJ-123) or numeric ID'
  ),
  startAt: z.number().int().min(0).optional().default(0),
  maxResults: z.number().int().min(1).max(100).optional().default(50),
});

export type GetIssueCommentsInput = z.infer<typeof GetIssueCommentsSchema>;

/**
 * Schema for search_issues tool parameters
 */
export const SearchIssuesSchema = z.object({
  jql: z.string().min(1, 'JQL query cannot be empty'),
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

// ── Confluence Schemas ───────────────────────────────────────────────

export const GetConfluencePageSchema = z.object({
  pageId: z.string().min(1, 'Page ID is required'),
  includeBody: z.boolean().optional().default(true),
  bodyFormat: z.enum(['storage', 'view', 'export_view']).optional().default('storage'),
});

export type GetConfluencePageInput = z.infer<typeof GetConfluencePageSchema>;

export const GetConfluencePageCommentsSchema = z.object({
  pageId: z.string().min(1, 'Page ID is required'),
  bodyFormat: z.enum(['storage', 'view']).optional().default('storage'),
  limit: z.number().int().min(1).max(100).optional().default(25),
  includeReplies: z.boolean().optional().default(true),
});

export type GetConfluencePageCommentsInput = z.infer<typeof GetConfluencePageCommentsSchema>;

export const GetChildPagesSchema = z.object({
  pageId: z.string().min(1, 'Page ID is required'),
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
  cql: z.string().min(1, 'CQL query is required'),
  limit: z.number().int().min(1).max(100).optional().default(10),
  start: z.number().int().min(0).optional().default(0),
});

export type SearchConfluenceCqlInput = z.infer<typeof SearchConfluenceCqlSchema>;

export const ListSpacesSchema = z.object({
  limit: z.number().int().min(1).max(250).optional().default(25),
  type: z.string().optional(),
});

export type ListSpacesInput = z.infer<typeof ListSpacesSchema>;

export const DownloadAttachmentSchema = z.object({
  attachmentUrl: z.string()
    .url('Must be a valid URL')
    .refine((url) => {
      try {
        const { pathname } = new URL(url);
        return /\/secure\/attachment\/|\/rest\/api\/.*\/attachment\//.test(pathname);
      } catch {
        return false;
      }
    }, 'Must be a JIRA attachment URL path')
    .refine((url) => {
      try {
        const { hostname } = new URL(url);
        return hostname.endsWith('.atlassian.net') && hostname !== '.atlassian.net';
      } catch {
        return false;
      }
    }, 'Attachment URL must be an *.atlassian.net hostname'),
  maxSizeMB: z.number()
    .int()
    .min(1)
    .max(50)
    .optional()
    .default(10),
});

export type DownloadAttachmentInput = z.infer<typeof DownloadAttachmentSchema>;

export const GetIssueRemoteLinksSchema = z.object({
  issueIdOrKey: z.string().regex(
    /^[A-Z][A-Z0-9_]+-\d+$|^\d+$/,
    'Must be a valid Jira issue key (e.g., PROJ-123) or numeric ID'
  ),
});

export type GetIssueRemoteLinksInput = z.infer<typeof GetIssueRemoteLinksSchema>;

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
