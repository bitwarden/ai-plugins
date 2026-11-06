// cspell:ignore bytewise somedir ustar
import { describe, it, expect } from "vitest";
import { readTarFiles } from "./tar.js";
import { buildTar, paxRecord } from "./tar-fixtures.js";

/** Splits a buffer into single-byte chunks, to test reads across chunk edges. */
async function* bytewise(buffer: Buffer): AsyncGenerator<Buffer> {
  for (const byte of buffer) {
    yield Buffer.from([byte]);
  }
}

async function collect(
  source: AsyncIterable<Buffer>,
  keep: (path: string) => boolean = () => true,
) {
  const files: Array<{ path: string; text: string }> = [];
  for await (const file of readTarFiles(source, keep)) {
    files.push({ path: file.path, text: file.body.toString("utf8") });
  }
  return files;
}

describe("readTarFiles", () => {
  it("yields regular files with their bodies", async () => {
    const tar = buildTar([
      { name: "repo-abc/a.cs", body: "class A {}" },
      { name: "repo-abc/b.cs", body: "class B {}\n" },
    ]);

    expect(await collect(bytewise(tar))).toEqual([
      { path: "repo-abc/a.cs", text: "class A {}" },
      { path: "repo-abc/b.cs", text: "class B {}\n" },
    ]);
  });

  it("joins the ustar prefix and name", async () => {
    const tar = buildTar([
      { name: "file.cs", prefix: "repo-abc/Some.Tests", body: "x" },
    ]);

    const files = await collect(bytewise(tar));

    expect(files.map((file) => file.path)).toEqual([
      "repo-abc/Some.Tests/file.cs",
    ]);
  });

  it("uses a pax path record for the next entry only", async () => {
    const longPath = `repo-abc/${"Deep/".repeat(30)}Long.cs`;
    const tar = buildTar([
      {
        name: "PaxHeader",
        flag: "x",
        body: paxRecord("path", longPath),
      },
      { name: "truncated-name.cs", body: "one" },
      { name: "short.cs", body: "two" },
    ]);

    const files = await collect(bytewise(tar));

    expect(files.map((file) => file.path)).toEqual([longPath, "short.cs"]);
  });

  it("uses a GNU long-name record", async () => {
    const longPath = `repo-abc/${"Gnu/".repeat(30)}Name.cs`;
    const tar = buildTar([
      { name: "././@LongLink", flag: "L", body: `${longPath}\0` },
      { name: "cut.cs", body: "gnu" },
    ]);

    expect((await collect(bytewise(tar))).map((f) => f.path)).toEqual([
      longPath,
    ]);
  });

  it("skips entries the filter rejects and non-regular entries", async () => {
    const tar = buildTar([
      { name: "repo-abc/keep.cs", body: "keep" },
      { name: "repo-abc/skip.txt", body: "skip" },
      { name: "repo-abc/somedir", flag: "5" },
    ]);

    const files = await collect(bytewise(tar), (path) => path.endsWith(".cs"));

    expect(files.map((file) => file.path)).toEqual(["repo-abc/keep.cs"]);
  });

  it("reads bodies that span many 512-byte blocks", async () => {
    const body = "line\n".repeat(2000);
    const tar = buildTar([{ name: "big.cs", body }]);

    const files = await collect(
      (async function* () {
        for (let offset = 0; offset < tar.length; offset += 777) {
          yield tar.subarray(offset, offset + 777);
        }
      })(),
    );

    expect(files).toEqual([{ path: "big.cs", text: body }]);
  });

  it("throws when the archive ends inside a header", async () => {
    const tar = buildTar([{ name: "a.cs", body: "aaaa" }]);

    await expect(collect(bytewise(tar.subarray(0, 300)))).rejects.toThrow(
      "ended inside a header",
    );
  });

  it("throws when the archive ends inside a file body", async () => {
    const tar = buildTar([{ name: "a.cs", body: "aaaa" }]);

    await expect(collect(bytewise(tar.subarray(0, 514)))).rejects.toThrow(
      "ended inside an entry",
    );
  });

  it("throws when the archive ends inside a skipped entry", async () => {
    const tar = buildTar([
      { name: "skip.txt", body: "x".repeat(2000) },
      { name: "a.cs", body: "a" },
    ]);

    await expect(
      collect(bytewise(tar.subarray(0, 1200)), () => false),
    ).rejects.toThrow("ended inside an entry");
  });
});
