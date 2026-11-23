/**
 * Shared formatting utilities for Confluence content
 */

const CODE_MACRO =
  /<ac:structured-macro\b[^>]*\bac:name=["']code["'][^>]*>([\s\S]*?)<\/ac:structured-macro>/gi;
const LANGUAGE_PARAM =
  /<ac:parameter\b[^>]*\bac:name=["']language["'][^>]*>([\s\S]*?)<\/ac:parameter>/i;
const PLAIN_TEXT_BODY =
  /<ac:plain-text-body[^>]*>([\s\S]*?)<\/ac:plain-text-body>/i;
const CDATA = /<!\[CDATA\[([\s\S]*?)\]\]>/;
const ANY_CDATA = /<!\[CDATA\[([\s\S]*?)\]\]>/g;

// Confluence storage is XML, so NUL cannot occur in it. NUL-delimited tokens
// let extracted content sit out the tag-stripping and entity-decoding passes
// below, then come back byte for byte.
const BLOCK_TAG = "H2M_BLOCK";
const blockPlaceholder = (index: number) => `\u0000${BLOCK_TAG}_${index}\u0000`;
const BLOCK_PLACEHOLDER = new RegExp(`\\u0000${BLOCK_TAG}_(\\d+)\\u0000`, "g");

function renderCodeMacro(macro: string): string {
  const body = macro.match(PLAIN_TEXT_BODY)?.[1] ?? "";
  const rawCode = body.match(CDATA)?.[1] ?? body;
  // Storage often wraps the body in a newline. Drop that wrapper but keep the
  // code's own indentation.
  const code = rawCode.replace(/^\r?\n+|\r?\n+$/g, "");
  // The language parameter is untrusted. A backtick or newline would close
  // the fence early and let the rest of the code render as prose.
  const language = (macro.match(LANGUAGE_PARAM)?.[1] ?? "")
    .replace(/[`\r\n]/g, "")
    .trim();
  return `\`\`\`${language}\n${code}\n\`\`\``;
}

/**
 * Convert Confluence storage format (XHTML) to readable markdown text.
 * Handles headings, lists, code blocks, inline formatting, and links.
 */
export function htmlToMarkdown(html: string): string {
  if (!html) return "";

  let text = html;

  const blocks: string[] = [];
  const preserve = (content: string) => {
    const token = blockPlaceholder(blocks.length);
    blocks.push(content);
    return token;
  };

  // Code macros become fenced blocks. Any remaining CDATA is kept as plain
  // text, since the generic tag strip below would otherwise eat the section
  // from `<![CDATA[` through `]]>` and lose its contents.
  text = text.replace(CODE_MACRO, (macro) => preserve(renderCodeMacro(macro)));
  text = text.replace(ANY_CDATA, (_, body: string) => preserve(body));

  // Replace common tags with readable equivalents
  text = text.replace(/<br\s*\/?>/gi, "\n");
  text = text.replace(/<\/p>/gi, "\n\n");
  text = text.replace(/<p[^>]*>/gi, "");
  text = text.replace(
    /<h([1-6])[^>]*>/gi,
    (_, level) => "\n" + "#".repeat(parseInt(level)) + " ",
  );
  text = text.replace(/<\/h[1-6]>/gi, "\n");
  text = text.replace(/<li[^>]*>/gi, "- ");
  text = text.replace(/<\/li>/gi, "\n");
  text = text.replace(/<ul[^>]*>|<\/ul>/gi, "\n");
  text = text.replace(/<ol[^>]*>|<\/ol>/gi, "\n");
  text = text.replace(/<strong[^>]*>|<\/strong>/gi, "**");
  text = text.replace(/<b[^>]*>|<\/b>/gi, "**");
  text = text.replace(/<em[^>]*>|<\/em>/gi, "_");
  text = text.replace(/<i[^>]*>|<\/i>/gi, "_");
  text = text.replace(/<code[^>]*>|<\/code>/gi, "`");
  text = text.replace(/<pre[^>]*>/gi, "\n```\n");
  text = text.replace(/<\/pre>/gi, "\n```\n");
  text = text.replace(/<a[^>]*href="([^"]*)"[^>]*>([^<]*)<\/a>/gi, "[$2]($1)");

  // Remove remaining HTML tags
  text = text.replace(/<[^>]+>/g, "");

  // Decode HTML entities
  text = text.replace(/&nbsp;/g, " ");
  text = text.replace(/&lt;/g, "<");
  text = text.replace(/&gt;/g, ">");
  text = text.replace(/&amp;/g, "&");
  text = text.replace(/&quot;/g, '"');
  text = text.replace(/&#39;/g, "'");

  text = text.replace(/\n{3,}/g, "\n\n");
  text = text.replace(
    BLOCK_PLACEHOLDER,
    (token: string, index: string, offset: number, source: string) => {
      const before = source[offset - 1] ?? "";
      const after = source[offset + token.length] ?? "";
      const block = blocks[Number(index)];
      // Storage can put text directly against a macro. Keep the restored
      // block on its own line so a closing fence does not swallow the
      // following word.
      const lead = before && before !== "\n" ? "\n" : "";
      const trail = after && after !== "\n" ? "\n" : "";
      return `${lead}${block}${trail}`;
    },
  );

  return text.trim();
}
