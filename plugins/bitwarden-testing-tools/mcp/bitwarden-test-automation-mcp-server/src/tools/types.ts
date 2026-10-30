import type { z } from "zod";
import type { ToolContext } from "../context.js";

export interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  handler: (input: unknown, ctx: ToolContext) => Promise<string>;
}

/** "1 case", "2 cases". */
export function caseCount(count: number): string {
  return `${count} ${count === 1 ? "case" : "cases"}`;
}

export function parseInput<T extends z.ZodType>(
  schema: T,
  input: unknown,
): z.output<T> {
  const result = schema.safeParse(input ?? {});
  if (!result.success) {
    const problems = result.error.issues
      .map((issue) => `${issue.path.join(".") || "input"}: ${issue.message}`)
      .join("; ");
    throw new Error(`Invalid input: ${problems}`);
  }
  return result.data;
}
