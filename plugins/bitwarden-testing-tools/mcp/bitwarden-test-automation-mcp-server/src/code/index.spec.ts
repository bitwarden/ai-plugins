import { describe, it, expect, vi } from "vitest";
import type { ArchiveSource } from "../github/archive.js";
import { CodeSourceError } from "../github/archive.js";
import { buildTar } from "../github/tar-fixtures.js";
import { buildCodeIndex } from "./index.js";

const SHA = "a400f22a3961bde78501a57733843417413bfe89";

const archive = buildTar([
  {
    name: `repo-${SHA.slice(0, 7)}/Bitwarden.Android.Tests/Vault/ItemTests.cs`,
    body: [
      '[Description("9891533")]',
      "public async Task Shows_menu()",
      "{}",
    ].join("\n"),
  },
  {
    name: `repo-${SHA.slice(0, 7)}/Bitwarden.Web.Tests/Vault/Covers.cs`,
    body: "[Covers(9891533)]\npublic async Task Covers_it()",
  },
  {
    name: `repo-${SHA.slice(0, 7)}/Bitwarden.Web.Tests/ProdSmoke/Smoke.cs`,
    body: '[Description("9891533")]\npublic async Task Smoke()',
  },
  {
    name: `repo-${SHA.slice(0, 7)}/Bitwarden.Core/NotTests.cs`,
    body: '[Description("9891533")]\npublic async Task NotTests()',
  },
]);

function sourceWith(bytes: Buffer): ArchiveSource {
  return {
    resolveBranchSha: vi.fn(async () => SHA),
    openArchive: vi.fn(async function* () {
      yield bytes;
    }),
  };
}

describe("buildCodeIndex", () => {
  it("indexes IDs from the scanned test files only", async () => {
    const index = await buildCodeIndex(sourceWith(archive), SHA, 1000);

    expect(index.sha).toBe(SHA);
    expect(index.loadedAt).toBe(1000);
    expect(index.filesScanned).toBe(2);
    const hits = index.hits.get(9891533) ?? [];
    expect(hits.map((hit) => [hit.path, hit.attribute])).toEqual([
      ["Bitwarden.Android.Tests/Vault/ItemTests.cs", "Description"],
      ["Bitwarden.Web.Tests/Vault/Covers.cs", "Covers"],
    ]);
  });

  it("returns an empty index when the archive has no test files", async () => {
    const empty = buildTar([{ name: "repo-x/README.md", body: "hi" }]);

    const index = await buildCodeIndex(sourceWith(empty), SHA, 0);

    expect(index.filesScanned).toBe(0);
    expect(index.hits.size).toBe(0);
  });

  it("does not hide a failure while the archive streams", async () => {
    const source: ArchiveSource = {
      resolveBranchSha: async () => SHA,
      openArchive: async function* () {
        yield archive.subarray(0, 600);
        throw new CodeSourceError("GitHub could not be reached");
      },
    };

    await expect(buildCodeIndex(source, SHA, 0)).rejects.toThrow(
      "GitHub could not be reached",
    );
  });
});
