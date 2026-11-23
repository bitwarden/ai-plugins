import { readTarFiles } from "../github/tar.js";
import type { ArchiveSource } from "../github/archive.js";
import { isScannedPath, scanFile, type CodeHit } from "./scan.js";

/** How long a finished index is reused before the branch is read again. */
export const CODE_INDEX_TTL_MS = 15 * 60 * 1000;

export interface CodeIndex {
  sha: string;
  loadedAt: number;
  filesScanned: number;
  hits: Map<number, CodeHit[]>;
}

/** Drops the archive's top-level folder (owner-repo-sha/) from a stored path. */
function repoPath(archivePath: string): string {
  const slash = archivePath.indexOf("/");
  return slash === -1 ? "" : archivePath.slice(slash + 1);
}

/**
 * Reads the whole branch snapshot once and indexes every Testmo ID it names.
 * Files are scanned as they stream past, so only the hits are kept.
 */
export async function buildCodeIndex(
  source: ArchiveSource,
  sha: string,
  now: number,
): Promise<CodeIndex> {
  const hits = new Map<number, CodeHit[]>();
  let filesScanned = 0;

  const files = readTarFiles(source.openArchive(sha), (archivePath) =>
    isScannedPath(repoPath(archivePath)),
  );
  for await (const file of files) {
    filesScanned += 1;
    const path = repoPath(file.path);
    for (const hit of scanFile(path, file.body.toString("utf8"))) {
      const existing = hits.get(hit.id);
      if (existing) {
        existing.push(hit);
      } else {
        hits.set(hit.id, [hit]);
      }
    }
  }

  return { sha, loadedAt: now, filesScanned, hits };
}
