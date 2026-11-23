import { createGhArchiveSource, type ArchiveSource } from "./github/archive.js";
import {
  buildCodeIndex,
  CODE_INDEX_TTL_MS,
  type CodeIndex,
} from "./code/index.js";

export interface ToolContext {
  now: () => number;
  /** Reads bitwarden/test through gh. Tests replace it with a fake. */
  github: ArchiveSource;
  codeIndex?: CodeIndex;
}

export function createToolContext(now: () => number = Date.now): ToolContext {
  return { now, github: createGhArchiveSource() };
}

/**
 * The code index for the current bitwarden/test main, reused for one TTL window.
 * Throws a CodeSourceError when GitHub cannot be read, so the caller can report
 * the code check as not checked.
 */
export async function loadCodeIndex(ctx: ToolContext): Promise<CodeIndex> {
  const now = ctx.now();
  if (ctx.codeIndex && now - ctx.codeIndex.loadedAt < CODE_INDEX_TTL_MS) {
    return ctx.codeIndex;
  }
  const sha = await ctx.github.resolveBranchSha();
  const index = await buildCodeIndex(ctx.github, sha, now);
  ctx.codeIndex = index;
  return index;
}
