/**
 * Reads the bitwarden/test repository through the GitHub CLI, using the user's
 * existing gh login. Nothing is cloned and nothing is written to disk. The
 * token stays inside gh and is never read or printed by this server.
 */

import { spawn } from "node:child_process";
import type { Readable } from "node:stream";
import { createGunzip } from "node:zlib";

export const CODE_REPO = "bitwarden/test";
export const CODE_BRANCH = "main";

/** Source of the repository snapshot. Tests replace it with a fake. */
export interface ArchiveSource {
  /** Full commit sha at the tip of the branch. */
  resolveBranchSha(): Promise<string>;
  /** Uncompressed tar bytes of the repository at `sha`, streamed. */
  openArchive(sha: string): AsyncIterable<Buffer>;
}

export interface GhProcess {
  stdout: Readable;
  stderr: Readable;
  /** Resolves with the exit code. Rejects when the process cannot start. */
  exit: Promise<number>;
}

export type GhSpawn = (args: string[]) => GhProcess;

/** A failure the skill can report as "not checked", with a plain reason. */
export class CodeSourceError extends Error {}

export function classifyGhFailure(stderr: string): string {
  if (/gh auth login|not logged in|authentication required/i.test(stderr)) {
    return "there is no gh login on this machine. Run `gh auth login`, then retry";
  }
  if (/rate limit|secondary rate|HTTP 403/i.test(stderr)) {
    return "the GitHub API rate limit was reached";
  }
  if (/HTTP 404|Not Found/i.test(stderr)) {
    return `${CODE_REPO} was not found, or this gh login cannot read it`;
  }
  if (
    /could not resolve|dial tcp|timed out|network|connection refused/i.test(
      stderr,
    )
  ) {
    return "GitHub could not be reached";
  }
  return "gh api failed";
}

export const defaultGhSpawn: GhSpawn = (args) => {
  const child = spawn("gh", args, { stdio: ["ignore", "pipe", "pipe"] });
  const exit = new Promise<number>((resolve, reject) => {
    child.on("error", reject);
    child.on("close", (code) => resolve(code ?? 1));
  });
  // A failed spawn rejects before anyone awaits this. Mark it handled here, so
  // Node does not crash, and the rejection still surfaces when it is awaited.
  exit.catch(() => undefined);
  return { stdout: child.stdout, stderr: child.stderr, exit };
};

function describeSpawnError(error: unknown): CodeSourceError {
  const code = (error as { code?: unknown } | null)?.code;
  if (code === "ENOENT") {
    return new CodeSourceError(
      "the GitHub CLI (gh) is not installed or not on PATH",
    );
  }
  return new CodeSourceError("the GitHub CLI (gh) could not be started");
}

async function collectStdout(proc: GhProcess): Promise<string> {
  let text = "";
  proc.stdout.setEncoding("utf8");
  for await (const chunk of proc.stdout) {
    text += chunk;
  }
  return text;
}

function collectStderr(proc: GhProcess): () => string {
  let text = "";
  proc.stderr.setEncoding("utf8");
  proc.stderr.on("data", (chunk: string) => {
    text += chunk;
  });
  return () => text;
}

async function finish(proc: GhProcess, stderr: () => string): Promise<void> {
  let code: number;
  try {
    code = await proc.exit;
  } catch (error) {
    throw describeSpawnError(error);
  }
  if (code !== 0) {
    throw new CodeSourceError(classifyGhFailure(stderr()));
  }
}

export function createGhArchiveSource(
  spawnGh: GhSpawn = defaultGhSpawn,
): ArchiveSource {
  return {
    async resolveBranchSha() {
      const proc = spawnGh([
        "api",
        `repos/${CODE_REPO}/commits/${CODE_BRANCH}`,
        "--jq",
        ".sha",
      ]);
      const stderr = collectStderr(proc);
      const out = (await collectStdout(proc)).trim();
      await finish(proc, stderr);
      if (!/^[0-9a-f]{40}$/.test(out)) {
        throw new CodeSourceError("GitHub returned no commit sha for main");
      }
      return out;
    },

    async *openArchive(sha: string) {
      if (!/^[0-9a-f]{40}$/.test(sha)) {
        throw new CodeSourceError("the commit sha is not valid");
      }
      const proc = spawnGh(["api", `repos/${CODE_REPO}/tarball/${sha}`]);
      const stderr = collectStderr(proc);
      const gunzip = proc.stdout.pipe(createGunzip());
      try {
        for await (const chunk of gunzip) {
          yield chunk as Buffer;
        }
      } catch (error) {
        // A non-zero exit explains a bad gzip stream better than the zlib error.
        await finish(proc, stderr);
        throw error;
      }
      await finish(proc, stderr);
    },
  };
}
