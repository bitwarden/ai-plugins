/**
 * Markdown to Confluence storage format.
 *
 * Confluence pages are written in storage format, an XHTML dialect. Callers
 * (and the model behind them) write markdown far more reliably than XHTML, so
 * the Confluence write tools accept markdown and convert it here.
 *
 * This is a deliberately small converter, written in-repo so the server takes
 * on no new dependency. It covers the markdown a write-up actually uses:
 * ATX headings, paragraphs, bulleted and numbered lists (nested, tight or
 * loose), GFM tables, fenced code blocks, block quotes, horizontal rules, and
 * the inline forms (bold, italic, strikethrough, code, links, images, hard
 * breaks, backslash escapes).
 *
 * Two properties matter more than coverage:
 *
 *  - The output is always well-formed XHTML. All text is escaped, raw HTML in
 *    the markdown is shown literally rather than passed through, and control
 *    characters XML cannot carry are dropped.
 *  - Only absolute `http(s):` and `mailto:` links are kept. A relative link
 *    (a sibling `README.md`, say) means nothing on a Confluence page, and any
 *    other scheme is not worth the risk, so those render as their text and are
 *    reported in `warnings` for the caller to see.
 */

export interface StorageConversion {
  storage: string;
  warnings: string[];
}

type Block =
  { kind: "paragraph"; html: string } | { kind: "html"; html: string };

interface ListMarker {
  indent: number;
  ordered: boolean;
  contentOffset: number;
  rest: string;
}

/** Placeholder delimiters. Both are stripped from the input before parsing. */
const SLOT = "\u0000";
const HARD_BREAK = "\u0001";

const HR = /^ {0,3}([-*_])(?: *\1){2,} *$/;
const FENCE_OPEN = /^( {0,3})(`{3,}|~{3,})\s*([\w+#.-]*)/;
const HEADING = /^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$/;
const BLOCKQUOTE = /^ {0,3}>/;
/** `(url "title")`. The URL may hold one level of balanced parentheses. */
const LINK_TARGET =
  '\\(\\s*<?((?:[^\\s()<>]|\\([^\\s()<>]*\\))+)>?(?:\\s+"[^"]*")?\\s*\\)';
const TABLE_SEPARATOR = /^ *\|? *:?-+:? *(?:\| *:?-+:? *)*\|? *$/;

export function markdownToStorage(markdown: string): StorageConversion {
  const warnings: string[] = [];
  const lines = markdown
    .replace(/\r\n?/g, "\n")
    // Characters XML 1.0 cannot carry, including the two placeholder marks.
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "")
    .replace(/\t/g, "    ")
    .split("\n");

  const storage = renderBlocks(parseBlocks(lines, warnings), false);

  return { storage, warnings: [...new Set(warnings)] };
}

// ── Blocks ─────────────────────────────────────────────────────────────

function isBlank(line: string): boolean {
  return line.trim() === "";
}

function indentOf(line: string): number {
  return line.length - line.trimStart().length;
}

function matchListMarker(line: string): ListMarker | undefined {
  if (HR.test(line)) {
    return undefined;
  }

  const m = line.match(/^( *)([-*+]|\d{1,9}[.)])( +|$)(.*)$/);
  if (!m) {
    return undefined;
  }

  return {
    indent: m[1].length,
    ordered: /\d/.test(m[2]),
    contentOffset: m[1].length + m[2].length + Math.max(m[3].length, 1),
    rest: m[4],
  };
}

function isTableStart(lines: string[], i: number): boolean {
  const next = lines[i + 1];
  return (
    lines[i].includes("|") &&
    next !== undefined &&
    next.includes("|") &&
    next.includes("-") &&
    TABLE_SEPARATOR.test(next)
  );
}

/** Whether `lines[i]` starts a new block, ending the paragraph before it. */
function interruptsParagraph(lines: string[], i: number): boolean {
  const line = lines[i];
  const marker = matchListMarker(line);

  return (
    FENCE_OPEN.test(line) ||
    HEADING.test(line) ||
    HR.test(line) ||
    BLOCKQUOTE.test(line) ||
    isTableStart(lines, i) ||
    // As in CommonMark, only a numbered list starting at 1 interrupts a
    // paragraph, so a wrapped line that happens to begin "2027." does not.
    (marker !== undefined &&
      marker.rest.trim() !== "" &&
      (!marker.ordered || /^ *1[.)]/.test(line)))
  );
}

function parseBlocks(lines: string[], warnings: string[]): Block[] {
  const blocks: Block[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (isBlank(line)) {
      i++;
      continue;
    }

    const fence = line.match(FENCE_OPEN);
    if (fence) {
      const [, fenceIndent, marker, language] = fence;
      const close = new RegExp(`^ {0,3}${marker[0]}{${marker.length},}\\s*$`);
      const code: string[] = [];
      i++;
      while (i < lines.length && !close.test(lines[i])) {
        code.push(
          lines[i].replace(new RegExp(`^ {0,${fenceIndent.length}}`), ""),
        );
        i++;
      }
      i++; // closing fence, or past the end if the fence was never closed
      blocks.push({ kind: "html", html: codeMacro(language, code.join("\n")) });
      continue;
    }

    const heading = line.match(HEADING);
    if (heading) {
      const level = heading[1].length;
      const text = renderInline(heading[2] ?? "", warnings);
      blocks.push({ kind: "html", html: `<h${level}>${text}</h${level}>` });
      i++;
      continue;
    }

    if (HR.test(line)) {
      blocks.push({ kind: "html", html: "<hr />" });
      i++;
      continue;
    }

    if (isTableStart(lines, i)) {
      const { html, next } = parseTable(lines, i, warnings);
      blocks.push({ kind: "html", html });
      i = next;
      continue;
    }

    if (BLOCKQUOTE.test(line)) {
      const quoted: string[] = [];
      while (i < lines.length && BLOCKQUOTE.test(lines[i])) {
        quoted.push(lines[i].replace(/^ {0,3}> ?/, ""));
        i++;
      }
      const inner = renderBlocks(parseBlocks(quoted, warnings), false);
      blocks.push({ kind: "html", html: `<blockquote>${inner}</blockquote>` });
      continue;
    }

    if (matchListMarker(line)) {
      const { html, next } = parseList(lines, i, warnings);
      blocks.push({ kind: "html", html });
      i = next;
      continue;
    }

    const paragraph = [line];
    i++;
    while (
      i < lines.length &&
      !isBlank(lines[i]) &&
      !interruptsParagraph(lines, i)
    ) {
      paragraph.push(lines[i]);
      i++;
    }
    blocks.push({
      kind: "paragraph",
      html: renderInline(joinParagraph(paragraph), warnings),
    });
  }

  return blocks;
}

/**
 * Join a paragraph's lines. A line ending in two spaces or a backslash is a
 * hard break; any other line break is a soft wrap and becomes a space.
 */
function joinParagraph(lines: string[]): string {
  return lines
    .map((line, index) => {
      const isLast = index === lines.length - 1;
      const trimmed = line.trim();
      if (!isLast && / {2,}$/.test(line)) {
        return trimmed + HARD_BREAK;
      }
      if (!isLast && trimmed.endsWith("\\")) {
        return trimmed.slice(0, -1) + HARD_BREAK;
      }
      return isLast ? trimmed : trimmed + " ";
    })
    .join("")
    .replace(new RegExp(`${HARD_BREAK} `, "g"), HARD_BREAK);
}

/** Render blocks. In a tight list item, paragraphs drop their `<p>` wrapper. */
function renderBlocks(blocks: Block[], tight: boolean): string {
  return blocks
    .map((block) =>
      block.kind === "paragraph" && !tight
        ? `<p>${block.html}</p>`
        : block.html,
    )
    .join("\n");
}

function parseList(
  lines: string[],
  start: number,
  warnings: string[],
): { html: string; next: number } {
  const first = matchListMarker(lines[start])!;
  const items: string[][] = [];
  let current: string[] = [];
  let contentOffset = first.contentOffset;
  let pendingBlank = false;
  let loose = false;
  let i = start;

  while (i < lines.length) {
    const line = lines[i];

    if (isBlank(line)) {
      pendingBlank = true;
      i++;
      continue;
    }

    const marker = matchListMarker(line);
    const indent = indentOf(line);

    if (marker && marker.indent < contentOffset) {
      // A marker at this list's level: a sibling item if it is the same kind
      // of list, otherwise the end of this list.
      if (marker.indent < first.indent || marker.ordered !== first.ordered) {
        break;
      }
      if (items.length > 0 || current.length > 0) {
        items.push(current);
        loose ||= pendingBlank;
      }
      current = [marker.rest];
      contentOffset = marker.contentOffset;
    } else if (
      indent >= contentOffset ||
      (indent > first.indent && !pendingBlank)
    ) {
      // Content belonging to the current item, shifted left into its own frame.
      if (pendingBlank) {
        current.push("");
        loose = true;
      }
      current.push(line.slice(Math.min(indent, contentOffset)));
    } else if (!pendingBlank && !interruptsParagraph(lines, i)) {
      // A lazy continuation line of the item's paragraph.
      current.push(line.trim());
    } else {
      break;
    }

    pendingBlank = false;
    i++;
  }
  items.push(current);

  const tag = first.ordered ? "ol" : "ul";
  const body = items
    .map(
      (item) => `<li>${renderBlocks(parseBlocks(item, warnings), !loose)}</li>`,
    )
    .join("");

  return { html: `<${tag}>${body}</${tag}>`, next: i };
}

function splitRow(line: string): string[] {
  let row = line.trim();
  if (row.startsWith("|")) row = row.slice(1);
  if (row.endsWith("|") && !row.endsWith("\\|")) row = row.slice(0, -1);

  const cells: string[] = [];
  let cell = "";
  for (let i = 0; i < row.length; i++) {
    if (row[i] === "\\" && row[i + 1] === "|") {
      cell += "|";
      i++;
    } else if (row[i] === "|") {
      cells.push(cell.trim());
      cell = "";
    } else {
      cell += row[i];
    }
  }
  cells.push(cell.trim());

  return cells;
}

function parseTable(
  lines: string[],
  start: number,
  warnings: string[],
): { html: string; next: number } {
  const header = splitRow(lines[start]);
  const rows: string[][] = [];
  let i = start + 2;

  while (i < lines.length && !isBlank(lines[i]) && lines[i].includes("|")) {
    rows.push(splitRow(lines[i]));
    i++;
  }

  const cells = (row: string[], tag: "th" | "td") =>
    header
      .map(
        (_, index) =>
          `<${tag}>${renderInline(row[index] ?? "", warnings)}</${tag}>`,
      )
      .join("");

  const html =
    "<table><tbody>" +
    `<tr>${cells(header, "th")}</tr>` +
    rows.map((row) => `<tr>${cells(row, "td")}</tr>`).join("") +
    "</tbody></table>";

  return { html, next: i };
}

function codeMacro(language: string, code: string): string {
  // "]]>" would end the CDATA section early; split it across two sections.
  const body = code.replace(/]]>/g, "]]]]><![CDATA[>");
  const languageParam = language
    ? `<ac:parameter ac:name="language">${escapeXml(language)}</ac:parameter>`
    : "";

  return (
    `<ac:structured-macro ac:name="code">${languageParam}` +
    `<ac:plain-text-body><![CDATA[${body}]]></ac:plain-text-body>` +
    "</ac:structured-macro>"
  );
}

// ── Inline ─────────────────────────────────────────────────────────────

function escapeXml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function isKeptUrl(url: string): boolean {
  return /^(https?:\/\/|mailto:)/i.test(url);
}

function renderInline(text: string, warnings: string[]): string {
  const slots: string[] = [];
  let html = formatInline(text, warnings, slots);

  // Slots can nest (a code span inside link text), so restore until stable.
  const slotPattern = new RegExp(`${SLOT}(\\d+)${SLOT}`, "g");
  let previous: string;
  do {
    previous = html;
    html = html.replace(slotPattern, (_, n) => slots[Number(n)]);
  } while (html !== previous);

  return html;
}

/**
 * Format inline markdown, parking finished fragments (code spans, links,
 * escapes) in `slots` so the emphasis pass below cannot reach inside them.
 */
function formatInline(
  text: string,
  warnings: string[],
  slots: string[],
): string {
  const hold = (html: string) => `${SLOT}${slots.push(html) - 1}${SLOT}`;
  // Bare URLs pass `formatLabel: false`: their text is the URL itself, which
  // would otherwise match the autolink pattern again, endlessly.
  const linkOrText = (label: string, url: string, formatLabel = true) => {
    const inner = formatLabel
      ? formatInline(label, warnings, slots)
      : escapeXml(label);
    if (isKeptUrl(url)) {
      return hold(`<a href="${escapeXml(url)}">${inner}</a>`);
    }
    warnings.push(
      `Link "${label}" (${url}) was rendered as plain text: only absolute ` +
        "http(s) and mailto links are kept.",
    );
    return hold(inner);
  };

  let s = text;

  s = s.replace(/(`+)(?!`)([\s\S]*?[^`])\1(?!`)/g, (_, _ticks, code: string) =>
    hold(`<code>${escapeXml(code.replace(/^ ([\s\S]*) $/, "$1"))}</code>`),
  );

  s = s.replace(
    /\\([!"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~])/g,
    (_, char: string) => hold(escapeXml(char)),
  );

  s = s.replace(
    new RegExp(`!\\[([^\\]]*)\\]${LINK_TARGET}`, "g"),
    (_, alt: string, url: string) => {
      if (isKeptUrl(url)) {
        return hold(
          `<ac:image ac:alt="${escapeXml(alt)}"><ri:url ri:value="${escapeXml(url)}" /></ac:image>`,
        );
      }
      warnings.push(
        `Image "${alt}" (${url}) was rendered as its alt text: only absolute ` +
          "http(s) image URLs are kept.",
      );
      return hold(escapeXml(alt));
    },
  );

  s = s.replace(
    new RegExp(`\\[([^\\]]+)\\]${LINK_TARGET}`, "g"),
    (_, label: string, url: string) => linkOrText(label, url),
  );

  // URLs stop at a slot mark, so a code span or link parked right after one
  // is never pulled inside its href.
  s = s.replace(
    /<((?:https?:\/\/|mailto:)[^\s<>\u0000]+)>/gi,
    (_, url: string) => linkOrText(url, url, false),
  );

  s = s.replace(
    /(^|[\s(])(https?:\/\/[^\s<\u0000]*[^\s<\u0000.,:;"')\]])/g,
    (_, lead: string, url: string) => lead + linkOrText(url, url, false),
  );

  s = emphasize(escapeXml(s), hold);

  return s.replace(new RegExp(HARD_BREAK, "g"), "<br />");
}

/**
 * Apply bold, strikethrough, and italic. Each finished span is parked with
 * `hold`, so a later pass cannot match across its closing tag and overlapping
 * markers never produce crossed tags; an unmatched marker stays literal. The
 * text inside a span is emphasized on its own, so `**a *b* c**` still nests.
 */
function emphasize(text: string, hold: (html: string) => string): string {
  const wrap = (open: string, close: string) => (inner: string) =>
    hold(`${open}${emphasize(inner, hold)}${close}`);
  const strong = wrap("<strong>", "</strong>");
  const em = wrap("<em>", "</em>");
  const strike = wrap(
    '<span style="text-decoration: line-through;">',
    "</span>",
  );

  let s = text;
  s = s.replace(/\*\*\*(?=\S)([\s\S]*?\S)\*\*\*/g, (_, inner: string) =>
    hold(`<strong>${em(inner)}</strong>`),
  );
  s = s.replace(/\*\*(?=\S)([\s\S]*?\S)\*\*/g, (_, inner: string) =>
    strong(inner),
  );
  s = s.replace(
    /(^|[^\w])__(?=\S)([\s\S]*?\S)__(?!\w)/g,
    (_, lead: string, inner: string) => lead + strong(inner),
  );
  s = s.replace(/~~(?=\S)([\s\S]*?\S)~~/g, (_, inner: string) => strike(inner));
  s = s.replace(/\*(?![\s*])([^*]*?[^\s*])\*/g, (_, inner: string) =>
    em(inner),
  );
  s = s.replace(
    /(^|[^\w])_(?![\s_])([^_]*?[^\s_])_(?!\w)/g,
    (_, lead: string, inner: string) => lead + em(inner),
  );

  return s;
}
