import { describe, it, expect } from "vitest";
import { Readable } from "node:stream";
import { gzipSync } from "node:zlib";
import {
  CodeSourceError,
  classifyGhFailure,
  createGhArchiveSource,
  type GhProcess,
  type GhSpawn,
} from "./archive.js";
import { buildTar } from "./tar-fixtures.js";

const SHA = "a400f22a3961bde78501a57733843417413bfe89";

/** A fake gh process: stdout and stderr text, and an exit code or spawn error. */
function fakeGh(options: {
  stdout?: Buffer | string;
  stderr?: string;
  exitCode?: number;
  spawnError?: NodeJS.ErrnoException;
}): { spawn: GhSpawn; calls: string[][] } {
  const calls: string[][] = [];
  const spawn: GhSpawn = (args): GhProcess => {
    calls.push(args);
    const exit = options.spawnError
      ? Promise.reject(options.spawnError)
      : Promise.resolve(options.exitCode ?? 0);
    exit.catch(() => undefined);
    return {
      stdout: Readable.from(
        options.stdout === undefined ? [] : [options.stdout],
      ),
      stderr: Readable.from(
        options.stderr === undefined ? [] : [options.stderr],
      ),
      exit,
    };
  };
  return { spawn, calls };
}

async function collectBytes(source: AsyncIterable<Buffer>): Promise<Buffer> {
  const parts: Buffer[] = [];
  for await (const chunk of source) {
    parts.push(chunk);
  }
  return Buffer.concat(parts);
}

describe("classifyGhFailure", () => {
  it.each([
    [
      "To get started with GitHub CLI, please run: gh auth login",
      /gh auth login/,
    ],
    ["API rate limit exceeded for user", /rate limit/],
    [
      "HTTP 404: Not Found (https://api.github.com/...)",
      /not found, or this gh login/,
    ],
    [
      "dial tcp: lookup api.github.com: no such host; could not resolve",
      /could not be reached/,
    ],
  ])("explains %s", (stderr, reason) => {
    expect(classifyGhFailure(stderr)).toMatch(reason);
  });

  it("falls back to a generic reason without echoing stderr", () => {
    expect(classifyGhFailure("something odd with ghp_secret123")).toBe(
      "gh api failed",
    );
  });
});

describe("createGhArchiveSource", () => {
  it("reads the sha of main through gh", async () => {
    const { spawn, calls } = fakeGh({ stdout: `${SHA}\n` });

    const sha = await createGhArchiveSource(spawn).resolveBranchSha();

    expect(sha).toBe(SHA);
    expect(calls[0]).toEqual([
      "api",
      "repos/bitwarden/test/commits/main",
      "--jq",
      ".sha",
    ]);
  });

  it("rejects a sha that is not 40 hex characters", async () => {
    const { spawn } = fakeGh({ stdout: "not-a-sha\n" });

    await expect(
      createGhArchiveSource(spawn).resolveBranchSha(),
    ).rejects.toThrow("no commit sha");
  });

  it("streams the gunzipped archive for the sha", async () => {
    const tar = buildTar([{ name: "repo/a.cs", body: "class A {}" }]);
    const { spawn, calls } = fakeGh({ stdout: gzipSync(tar) });

    const bytes = await collectBytes(
      createGhArchiveSource(spawn).openArchive(SHA),
    );

    expect(bytes.equals(tar)).toBe(true);
    expect(calls[0]).toEqual(["api", `repos/bitwarden/test/tarball/${SHA}`]);
  });

  it("reports a failed archive request with the classified reason", async () => {
    const { spawn } = fakeGh({
      stderr: "HTTP 404: Not Found",
      exitCode: 1,
    });

    await expect(
      collectBytes(createGhArchiveSource(spawn).openArchive(SHA)),
    ).rejects.toThrow(CodeSourceError);
    await expect(
      collectBytes(createGhArchiveSource(spawn).openArchive(SHA)),
    ).rejects.toThrow("not found, or this gh login cannot read it");
  });

  it("does not crash when the spawn fails before stdout is read", async () => {
    // Mirrors the real spawn: the exit promise rejects while stdout is still
    // being read. An unhandled rejection would fail this test run.
    const enoent = Object.assign(new Error("spawn gh ENOENT"), {
      code: "ENOENT",
    });
    const spawn: GhSpawn = () => {
      const exit = new Promise<number>((_, reject) => {
        setTimeout(() => reject(enoent), 0);
      });
      exit.catch(() => undefined);
      return {
        stdout: new Readable({
          read() {
            setTimeout(() => this.push(null), 5);
          },
        }),
        stderr: Readable.from([]),
        exit,
      };
    };

    await expect(
      createGhArchiveSource(spawn).resolveBranchSha(),
    ).rejects.toThrow("not installed or not on PATH");
  });

  it("says gh is missing when the binary cannot start", async () => {
    const enoent = Object.assign(new Error("spawn gh ENOENT"), {
      code: "ENOENT",
    });
    const { spawn } = fakeGh({ spawnError: enoent });

    await expect(
      createGhArchiveSource(spawn).resolveBranchSha(),
    ).rejects.toThrow("not installed or not on PATH");
  });

  it("refuses a sha that is not a commit id, before calling gh", async () => {
    const { spawn, calls } = fakeGh({});

    await expect(
      collectBytes(createGhArchiveSource(spawn).openArchive("main; rm -rf")),
    ).rejects.toThrow("not valid");
    expect(calls).toHaveLength(0);
  });
});
