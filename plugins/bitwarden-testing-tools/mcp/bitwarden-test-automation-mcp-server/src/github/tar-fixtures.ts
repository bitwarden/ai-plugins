// cspell:ignore ustar
/** Builds small tar archives in memory for tests. Not used by the server. */

interface Entry {
  name: string;
  body?: string;
  /** Defaults to "0" (regular file). */
  flag?: string;
  /** Written into the ustar prefix field, with the name after it. */
  prefix?: string;
}

function header(entry: Entry, size: number): Buffer {
  const block = Buffer.alloc(512);
  const put = (text: string, start: number, length: number) =>
    block.write(text.slice(0, length), start, "latin1");
  put(entry.name, 0, 100);
  put("0000644\0", 100, 8);
  put("0000000\0", 108, 8);
  put("0000000\0", 116, 8);
  put(size.toString(8).padStart(11, "0") + "\0", 124, 12);
  put("00000000000\0", 136, 12);
  put("        ", 148, 8);
  put(entry.flag ?? "0", 156, 1);
  if (entry.prefix !== undefined) {
    put("ustar\0", 257, 6);
    put("00", 263, 2);
    put(entry.prefix, 345, 155);
  }
  let sum = 0;
  for (const byte of block) {
    sum += byte;
  }
  put(sum.toString(8).padStart(6, "0") + "\0 ", 148, 8);
  return block;
}

function padded(data: Buffer): Buffer {
  const remainder = data.length % 512;
  return remainder === 0
    ? data
    : Buffer.concat([data, Buffer.alloc(512 - remainder)]);
}

export function buildTar(entries: Entry[]): Buffer {
  const parts: Buffer[] = [];
  for (const entry of entries) {
    const body = Buffer.from(entry.body ?? "", "utf8");
    parts.push(header(entry, body.length));
    if (body.length > 0) {
      parts.push(padded(body));
    }
  }
  parts.push(Buffer.alloc(1024));
  return Buffer.concat(parts);
}

/** A pax extended header record for `path`, as GitHub writes for long names. */
export function paxRecord(key: string, value: string): string {
  const body = ` ${key}=${value}\n`;
  // The length counts its own digits, so iterate until the value is stable.
  let total = body.length;
  for (;;) {
    const next = body.length + String(total).length;
    if (next === total) {
      return `${total}${body}`;
    }
    total = next;
  }
}
