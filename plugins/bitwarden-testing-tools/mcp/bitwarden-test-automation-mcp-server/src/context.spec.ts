import { describe, it, expect, vi } from "vitest";
import {
  createToolContext,
  loadCodeIndex,
  type ToolContext,
} from "./context.js";
import { CodeSourceError, type ArchiveSource } from "./github/archive.js";

describe("createToolContext", () => {
  it("uses the clock it is given", () => {
    expect(createToolContext(() => 42).now()).toBe(42);
  });
});

describe("loadCodeIndex", () => {
  it("does not cache a failed GitHub read, so the next call tries again", async () => {
    const source: ArchiveSource = {
      resolveBranchSha: vi.fn(async () => {
        throw new CodeSourceError("there is no gh login on this machine.");
      }),
      openArchive: vi.fn(),
    };
    const ctx: ToolContext = { now: () => 0, github: source };

    await expect(loadCodeIndex(ctx)).rejects.toThrow(CodeSourceError);
    await expect(loadCodeIndex(ctx)).rejects.toThrow(CodeSourceError);
    expect(source.resolveBranchSha).toHaveBeenCalledTimes(2);
    expect(ctx.codeIndex).toBeUndefined();
  });
});
