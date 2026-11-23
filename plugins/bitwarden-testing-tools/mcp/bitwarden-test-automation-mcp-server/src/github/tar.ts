// cspell:ignore ustar
/**
 * Streaming reader for uncompressed tar archives. It yields the regular files
 * that `keep` accepts and skips the rest, so an archive never has to fit in
 * memory. Handles the ustar name prefix and the pax and GNU long-name records
 * that GitHub archives use.
 */

const BLOCK = 512;

export interface TarFile {
  /** Path as stored in the archive, including the archive's top-level folder. */
  path: string;
  body: Buffer;
}

/** Reads exact byte counts from a stream of chunks, keeping only what is pending. */
class ChunkReader {
  private readonly iterator: AsyncIterator<Buffer>;
  private chunks: Buffer[] = [];
  private size = 0;
  private ended = false;

  constructor(source: AsyncIterable<Buffer>) {
    this.iterator = source[Symbol.asyncIterator]();
  }

  private async fill(): Promise<boolean> {
    if (this.ended) {
      return false;
    }
    const next = await this.iterator.next();
    if (next.done) {
      this.ended = true;
      return false;
    }
    this.chunks.push(next.value);
    this.size += next.value.length;
    return true;
  }

  /** Returns n bytes, or fewer only when the archive ends first. */
  async read(n: number): Promise<Buffer> {
    while (this.size < n && (await this.fill())) {
      // Keep pulling until enough bytes are buffered or the stream ends.
    }
    const take = Math.min(n, this.size);
    const out = Buffer.allocUnsafe(take);
    let offset = 0;
    while (offset < take) {
      const head = this.chunks[0];
      const need = take - offset;
      if (head.length <= need) {
        head.copy(out, offset);
        offset += head.length;
        this.chunks.shift();
      } else {
        head.copy(out, offset, 0, need);
        this.chunks[0] = head.subarray(need);
        offset += need;
      }
    }
    this.size -= take;
    return out;
  }

  /** Discards n bytes without copying them. */
  async skip(n: number): Promise<void> {
    let remaining = n;
    while (remaining > 0) {
      if (this.size === 0 && !(await this.fill())) {
        throw new Error("The archive ended inside an entry.");
      }
      const head = this.chunks[0];
      if (head.length <= remaining) {
        remaining -= head.length;
        this.size -= head.length;
        this.chunks.shift();
      } else {
        this.chunks[0] = head.subarray(remaining);
        this.size -= remaining;
        remaining = 0;
      }
    }
  }
}

function field(block: Buffer, start: number, length: number): string {
  const slice = block.subarray(start, start + length);
  const nul = slice.indexOf(0);
  return slice.subarray(0, nul === -1 ? length : nul).toString("utf8");
}

function octalField(block: Buffer, start: number, length: number): number {
  if (block[start] & 0x80) {
    throw new Error("Unsupported tar size encoding (base-256).");
  }
  const text = field(block, start, length).trim();
  return text === "" ? 0 : parseInt(text, 8);
}

/** Reads the path from a pax extended header ("<len> path=<value>\n" records). */
function paxPath(data: Buffer): string | undefined {
  let path: string | undefined;
  let pos = 0;
  while (pos < data.length) {
    const space = data.indexOf(0x20, pos);
    if (space === -1) {
      break;
    }
    const length = parseInt(data.subarray(pos, space).toString("ascii"), 10);
    if (!(length > 0)) {
      break;
    }
    // Drop the length digits, the separating space, and the trailing newline.
    const record = data.subarray(space + 1, pos + length - 1).toString("utf8");
    const equals = record.indexOf("=");
    if (equals > 0 && record.slice(0, equals) === "path") {
      path = record.slice(equals + 1);
    }
    pos += length;
  }
  return path;
}

/**
 * Yields each regular file in the archive whose stored path passes `keep`.
 * Stops at the first all-zero header block, which ends a tar archive.
 */
export async function* readTarFiles(
  source: AsyncIterable<Buffer>,
  keep: (path: string) => boolean,
): AsyncGenerator<TarFile> {
  const reader = new ChunkReader(source);
  let pendingPath: string | undefined;

  for (;;) {
    const header = await reader.read(BLOCK);
    if (header.length === 0) {
      return;
    }
    if (header.length < BLOCK) {
      throw new Error("The archive ended inside a header.");
    }
    if (header.every((byte) => byte === 0)) {
      return;
    }

    const size = octalField(header, 124, 12);
    const padding = (BLOCK - (size % BLOCK)) % BLOCK;
    const flag = header[156] === 0 ? "0" : String.fromCharCode(header[156]);

    if (flag === "x") {
      pendingPath = paxPath(await reader.read(size)) ?? pendingPath;
      await reader.skip(padding);
      continue;
    }
    if (flag === "L") {
      const data = await reader.read(size);
      pendingPath = data.toString("utf8").replace(/\0[\s\S]*$/, "");
      await reader.skip(padding);
      continue;
    }
    if (flag === "g") {
      await reader.skip(size + padding);
      continue;
    }

    const magic = field(header, 257, 6);
    const prefix = magic.startsWith("ustar") ? field(header, 345, 155) : "";
    const name = field(header, 0, 100);
    const path = pendingPath ?? (prefix === "" ? name : `${prefix}/${name}`);
    pendingPath = undefined;

    if (flag === "0" && keep(path)) {
      const body = await reader.read(size);
      if (body.length < size) {
        throw new Error("The archive ended inside an entry.");
      }
      await reader.skip(padding);
      yield { path, body };
    } else {
      await reader.skip(size + padding);
    }
  }
}
