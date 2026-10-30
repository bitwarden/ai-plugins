import { describe, it, expect, vi } from "vitest";
import type { ToolContext } from "../context.js";
import { CodeSourceError, type ArchiveSource } from "../github/archive.js";
import { buildTar } from "../github/tar-fixtures.js";
import findAutomatedCases from "./find-automated-cases.js";

const SHA = "a400f22a3961bde78501a57733843417413bfe89";
const NOW = Date.UTC(2026, 9, 22, 12, 0, 0);

const archive = buildTar([
  {
    name: `bitwarden-test-${SHA.slice(0, 7)}/Bitwarden.Android.Tests/Vault/A.cs`,
    body: [
      '[Description("20213")]',
      '[Ignore("flaky")]',
      "public async Task Re_send()",
    ].join("\n"),
  },
]);

function contextWith(source: ArchiveSource): ToolContext {
  return {
    now: () => NOW,
    github: source,
  };
}

function okSource(): ArchiveSource {
  return {
    resolveBranchSha: vi.fn(async () => SHA),
    openArchive: vi.fn(async function* () {
      yield archive;
    }),
  };
}

describe("find_automated_cases", () => {
  it("reports found with file, line, attribute, platform, and ignore state", async () => {
    const text = await findAutomatedCases.handler(
      { caseIds: [20213] },
      contextWith(okSource()),
    );

    expect(text).toContain(`Source: bitwarden/test, main at ${SHA}`);
    expect(text).toContain("read 2026-10-22T12:00:00.000Z");
    expect(text).toContain("20213: found, 1 match(es)");
    expect(text).toContain(
      "  - Bitwarden.Android.Tests/Vault/A.cs:1 [Description] platform Android, ignored yes, KnownBug no",
    );
  });

  it("reports not found for IDs with no match", async () => {
    const text = await findAutomatedCases.handler(
      { caseIds: [99999999] },
      contextWith(okSource()),
    );

    expect(text).toContain("99999999: not found");
  });

  it("says Code not checked, with the reason, when GitHub cannot be read", async () => {
    const source: ArchiveSource = {
      resolveBranchSha: vi.fn(async () => {
        throw new CodeSourceError("there is no gh login on this machine.");
      }),
      openArchive: vi.fn(),
    };

    const text = await findAutomatedCases.handler(
      { caseIds: [20213, 20214] },
      contextWith(source),
    );

    expect(text).toMatch(/^Code not checked: there is no gh login/);
    expect(text).toContain("20213, 20214");
  });

  it("reuses the index inside its window and reads GitHub again after it", async () => {
    const source = okSource();
    let clock = NOW;
    const ctx: ToolContext = {
      ...contextWith(source),
      now: () => clock,
    };

    await findAutomatedCases.handler({ caseIds: [20213] }, ctx);
    clock += 60_000;
    await findAutomatedCases.handler({ caseIds: [20213] }, ctx);
    expect(source.resolveBranchSha).toHaveBeenCalledTimes(1);

    clock += 15 * 60 * 1000;
    await findAutomatedCases.handler({ caseIds: [20213] }, ctx);
    expect(source.resolveBranchSha).toHaveBeenCalledTimes(2);
  });

  it("rejects an empty ID list", async () => {
    await expect(
      findAutomatedCases.handler({ caseIds: [] }, contextWith(okSource())),
    ).rejects.toThrow("Invalid input");
  });
});
