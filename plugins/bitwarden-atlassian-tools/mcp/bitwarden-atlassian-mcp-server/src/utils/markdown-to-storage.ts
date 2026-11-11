/**
 * Markdown-to-Confluence storage format converter.
 *
 * Confluence storage format is XHTML with Atlassian-specific macros. This
 * module converts standard markdown into that format so callers can write
 * pages in markdown without hand-authoring XHTML.
 *
 * Uses `marked` (already a dependency for Jira ADF) with a custom renderer
 * that emits Confluence storage format instead of vanilla HTML:
 *
 *  - Fenced code blocks → <ac:structured-macro ac:name="code">
 *  - Tables → <table> with Confluence CSS classes
 *  - Blockquotes → <ac:structured-macro ac:name="info">
 *  - Everything else → standard XHTML (which Confluence accepts as-is)
 */

import { marked, Renderer } from "marked";

/**
 * Escape characters that are special in XML/XHTML.
 */
function escapeXml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/**
 * Create a Renderer subclass that emits Confluence storage format.
 *
 * marked v16 passes structured token objects to each renderer method.
 */
class ConfluenceRenderer extends Renderer {
  // Fenced and indented code blocks → Confluence code macro
  code(token: { text: string; lang?: string }): string {
    const langParam = token.lang
      ? `<ac:parameter ac:name="language">${escapeXml(token.lang)}</ac:parameter>`
      : "";
    return (
      `<ac:structured-macro ac:name="code" ac:schema-version="1">` +
      langParam +
      `<ac:plain-text-body><![CDATA[${token.text}]]></ac:plain-text-body>` +
      `</ac:structured-macro>\n`
    );
  }

  // Tables with Confluence classes
  table(token: {
    header: { text: string; tokens: any[]; align: string | null }[];
    rows: { text: string; tokens: any[]; align: string | null }[][];
  }): string {
    const headerCells = token.header
      .map(
        (cell) =>
          `<th class="confluenceTh">${this.parser.parseInline(cell.tokens)}</th>`,
      )
      .join("");

    const bodyRows = token.rows
      .map((row) => {
        const cells = row
          .map(
            (cell) =>
              `<td class="confluenceTd">${this.parser.parseInline(cell.tokens)}</td>`,
          )
          .join("");
        return `<tr>${cells}</tr>\n`;
      })
      .join("");

    return (
      `<table class="wrapped confluenceTable">\n` +
      `<thead><tr>${headerCells}</tr></thead>\n` +
      `<tbody>\n${bodyRows}</tbody>\n` +
      `</table>\n`
    );
  }

  // Blockquote → Confluence info macro
  blockquote(token: { text: string; tokens: any[] }): string {
    const inner = this.parser.parse(token.tokens);
    return (
      `<ac:structured-macro ac:name="info">` +
      `<ac:rich-text-body>${inner}</ac:rich-text-body>` +
      `</ac:structured-macro>\n`
    );
  }

  // Lists
  list(token: {
    ordered: boolean;
    items: {
      text: string;
      tokens: any[];
      task: boolean;
      checked?: boolean;
    }[];
  }): string {
    const tag = token.ordered ? "ol" : "ul";
    const items = token.items
      .map((item) => `<li>${this.parser.parse(item.tokens)}</li>\n`)
      .join("");
    return `<${tag}>\n${items}</${tag}>\n`;
  }
}

/**
 * Detect whether a string is already in Confluence storage format.
 *
 * A string is considered storage format if it starts with an HTML/XML tag
 * or a Confluence macro. Markdown never starts with `<` unless it's raw HTML,
 * which is an edge case we handle by treating it as storage format (pass-through).
 */
export function isStorageFormat(text: string): boolean {
  const trimmed = text.trimStart();
  return (
    trimmed.startsWith("<") &&
    (trimmed.startsWith("<p") ||
      trimmed.startsWith("<h1") ||
      trimmed.startsWith("<h2") ||
      trimmed.startsWith("<h3") ||
      trimmed.startsWith("<h4") ||
      trimmed.startsWith("<h5") ||
      trimmed.startsWith("<h6") ||
      trimmed.startsWith("<div") ||
      trimmed.startsWith("<table") ||
      trimmed.startsWith("<ul") ||
      trimmed.startsWith("<ol") ||
      trimmed.startsWith("<ac:") ||
      trimmed.startsWith("<ri:") ||
      trimmed.startsWith("<!"))
  );
}

/**
 * Convert markdown to Confluence storage format (XHTML).
 *
 * If the input is already in storage format (starts with an HTML tag),
 * it is returned as-is. Otherwise, markdown is parsed and converted using
 * a custom renderer that emits Confluence-specific XHTML with proper table
 * classes and code block macros.
 */
export function markdownToStorage(markdown: string): string {
  if (isStorageFormat(markdown)) {
    return markdown;
  }

  const renderer = new ConfluenceRenderer();

  const result = marked.parse(markdown, {
    renderer,
    async: false,
  }) as string;

  return result.trim();
}
