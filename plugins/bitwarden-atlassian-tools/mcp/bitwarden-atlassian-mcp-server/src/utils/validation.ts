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
