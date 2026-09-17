/**
 * ADF construction for Jira writes.
 *
 * The counterpart to `adf.ts`, which extracts plain text out of ADF for reads.
 *
 * Acceptance criteria are NOT built here: the PM project exposes
 * `Acceptance criteria` (customfield_10192) as a plain textarea, so Gherkin is
 * sent as a string and needs no ADF at all. That leaves descriptions and
 * comment bodies, both authored as markdown. Both go through marklassian
 * instead of hand-built text nodes, so emphasis, links, inline and fenced
 * code, lists, headings, blockquotes, and tables survive the trip into Jira.
 * Targets outside a scheme allowlist are dropped on the way through, and an
 * entry carrying raw HTML is sent as plain text so none of its characters are
 * lost to markup the converter would discard.
 */

import { markdownToAdf } from "marklassian";
import { marked } from "marked";

/**
 * A single ADF node. Deliberately open: markdown converts into any of ADF's
 * node types (headings, lists, code blocks, tables, media, and the marks that
 * carry emphasis and links), not just the bare-text paragraphs this module
 * used to hand-build. Narrowing it would mean restating marklassian's whole
 * output schema here and keeping it in sync for no gain.
 */
export interface AdfNode {
  type: string;
  [key: string]: unknown;
}

export interface AdfDoc {
  version: 1;
  type: "doc";
  content: AdfNode[];
}

/**
 * Schemes allowed to survive conversion. Markdown can name any scheme in a
 * link or image target, and these bodies are untrusted input: they reach here
 * from a model or a caller, not from a human typing into Jira's own editor.
 * ADF is structured JSON rather than HTML, so a tag cannot be injected, but a
 * target is passed through verbatim and would arrive at Jira intact. Jira
 * sanitizes on render, so this is defense in depth rather than the only thing
 * standing in the way.
 */
const SAFE_URL_SCHEMES = new Set(["http:", "https:", "mailto:"]);

/**
 * Attribute keys marklassian uses to carry a target: `href` on a link mark,
 * `url` on the `media` node an image converts to. A target in either place has
 * to clear the allowlist, since checking only link marks would let an image
 * source through.
 */
const TARGET_ATTRS = ["href", "url"] as const;

interface AdfMark {
  type: string;
  attrs?: { href?: unknown };
}

/**
 * Targets that name no scheme of their own, which Jira resolves against the
 * page they are rendered on.
 *
 * A `//host/path` target is deliberately included. It inherits the page's
 * scheme and so points off-site, but that makes it equivalent to the
 * `https://host/path` the allowlist already admits, and an external link is
 * not what the allowlist exists to stop.
 */
function isSchemeRelativeTarget(target: string): boolean {
  return (
    target.startsWith("/") || target.startsWith("#") || target.startsWith("?")
  );
}

function hasSafeScheme(target: unknown): boolean {
  if (typeof target !== "string") {
    return false;
  }

  try {
    return SAFE_URL_SCHEMES.has(new URL(target).protocol);
  } catch {
    // `new URL` also rejects targets that name a scheme in an encoded form,
    // such as `javascript&colon;alert(1)`, which anything decoding HTML
    // entities on the way into an href would turn back into a real scheme. So
    // a target that fails to parse must positively look scheme-relative to be
    // kept, rather than merely fail to parse.
    return isSchemeRelativeTarget(target);
  }
}

function isUnsafeLinkMark(mark: unknown): boolean {
  if (typeof mark !== "object" || mark === null) {
    return false;
  }

  const { type, attrs } = mark as AdfMark;

  return type === "link" && !hasSafeScheme(attrs?.href);
}

function hasUnsafeTarget(node: AdfNode): boolean {
  const { attrs } = node;

  if (typeof attrs !== "object" || attrs === null) {
    return false;
  }

  const record = attrs as Record<string, unknown>;

  return TARGET_ATTRS.some(
    (key) => record[key] !== undefined && !hasSafeScheme(record[key]),
  );
}

/**
 * Nodes whose position in their parent carries meaning, so that removing one
 * changes what its siblings say.
 *
 * A table cell is the case that matters: drop one and every later cell in the
 * row shifts a column left, so a value ends up under the wrong heading. That
 * is worse than an empty cell, so these are emptied rather than removed.
 */
const POSITIONAL_NODES = new Set(["tableCell", "tableHeader", "listItem"]);

/**
 * Drop every target outside the allowlist, returning null when the node itself
 * cannot survive.
 *
 * An unsafe link mark is stripped from its node so the text it covered stays.
 * A node that carries the target in its own attributes, such as the `media`
 * node an image becomes, has no covered text to keep and so is dropped whole,
 * along with any wrapper left empty behind it. A positional node is kept as an
 * empty container instead, since ADF requires one to hold a block.
 */
function sanitizeNode(node: AdfNode): AdfNode | null {
  if (hasUnsafeTarget(node)) {
    return null;
  }

  const sanitized: AdfNode = { ...node };

  if (Array.isArray(sanitized.marks)) {
    const kept = sanitized.marks.filter((mark) => !isUnsafeLinkMark(mark));

    if (kept.length > 0) {
      sanitized.marks = kept;
    } else {
      delete sanitized.marks;
    }
  }

  if (Array.isArray(sanitized.content)) {
    const original = sanitized.content as AdfNode[];
    const children = original
      .map(sanitizeNode)
      .filter((child): child is AdfNode => child !== null);

    if (original.length > 0 && children.length === 0) {
      if (!POSITIONAL_NODES.has(sanitized.type)) {
        return null;
      }

      sanitized.content = [{ type: "paragraph" }];

      return sanitized;
    }

    sanitized.content = children;
  }

  return sanitized;
}

/**
 * Whether markdown carries a raw-HTML token.
 *
 * marklassian discards raw HTML instead of rendering it, so an entry holding
 * any would reach Jira with those characters missing: `List<String>` arrives
 * as `List`, and a Gherkin Scenario Outline's `<placeholder>` disappears.
 *
 * The question is asked of marked, the lexer marklassian itself parses with,
 * so the answer matches what the converter will actually do. Recognizing the
 * brackets by hand cannot: a stray fence run, a four-space indented block, an
 * unmatched backtick and an autolink all hinge on lexical context, and every
 * approximation of it mistook one for another.
 */
function containsRawHtml(markdown: string): boolean {
  return hasHtmlToken(marked.lexer(markdown));
}

/**
 * Walk anything the lexer returns looking for an `html` token. Tokens nest
 * differently by kind, with children under `tokens`, `items`, `header` and
 * `rows`, so this recurses over every value rather than naming those keys and
 * silently missing a nesting the next marked release introduces.
 */
function hasHtmlToken(value: unknown): boolean {
  if (Array.isArray(value)) {
    return value.some(hasHtmlToken);
  }

  if (value === null || typeof value !== "object") {
    return false;
  }

  if ((value as { type?: unknown }).type === "html") {
    return true;
  }

  return Object.values(value).some(hasHtmlToken);
}

/**
 * A paragraph of unstyled text, carrying single newlines as hard breaks.
 *
 * ADF renders a newline inside a text node as nothing, so line structure would
 * collapse without this: a list sent down this path would run its items
 * together on one line. `hardBreak` is the node ADF provides for a break
 * within a paragraph.
 *
 * An empty paragraph carries no content at all, since ADF has no valid empty
 * text node. Both write schemas reject a blank body before it reaches here.
 */
function plainParagraph(text: string): AdfNode {
  const content: AdfNode[] = [];

  text.split("\n").forEach((line, index) => {
    if (index > 0) {
      content.push({ type: "hardBreak" });
    }

    if (line.length > 0) {
      content.push({ type: "text", text: line });
    }
  });

  return content.length > 0
    ? { type: "paragraph", content }
    : { type: "paragraph" };
}

/**
 * Emit text verbatim, one paragraph per blank-line-separated block.
 *
 * Splitting rather than emitting a single paragraph keeps the author's
 * paragraph breaks; the line breaks within each block are kept by
 * `plainParagraph`.
 */
function plainParagraphs(text: string): AdfNode[] {
  const blocks = text
    .split(/\n\s*\n/)
    .map((block) => block.trim())
    .filter((block) => block.length > 0);

  return blocks.length > 0
    ? blocks.map(plainParagraph)
    : [plainParagraph(text.trim())];
}

/**
 * Convert one markdown string into sanitized ADF block nodes.
 *
 * Markdown carrying no renderable blocks converts to an empty document:
 * `<details>`, `<br>`, an HTML comment, and a bare link reference all do,
 * because raw HTML is discarded rather than rendered. Jira also rejects a
 * comment whose body has no content. Before this module parsed markdown, such
 * text reached Jira verbatim, so it falls back to a single plain-text
 * paragraph and no author's words are ever silently dropped.
 */
function convertMarkdown(text: string): AdfNode[] {
  // Raw HTML would be discarded, taking the author's characters with it, so
  // the entry is sent as plain text instead. It forfeits markdown rendering
  // for that entry, which is the deliberate trade: text is never lost, and
  // the outcome is predictable from the input rather than depending on which
  // constructs happen to survive conversion.
  if (containsRawHtml(text)) {
    return plainParagraphs(text);
  }

  const blocks = markdownToAdf(text)
    .content.map(sanitizeNode)
    .filter((node): node is AdfNode => node !== null);

  return blocks.length > 0 ? blocks : plainParagraphs(text);
}

/**
 * Build an ADF document from discrete paragraphs of markdown.
 *
 * Each entry is converted independently and the resulting block nodes are
 * flattened into one document. Converting per-entry rather than joining the
 * array first keeps a caller's paragraph boundaries intact even when one
 * entry's markdown expands into several blocks, such as an entry that is
 * itself a list.
 *
 * @param paragraphs - Paragraph strings, each markdown. Empty and
 *   whitespace-only entries are dropped, since Jira renders an empty paragraph
 *   as visible dead space.
 * @returns An ADF doc, or undefined when there is nothing to send so the
 *   caller can omit the description field entirely rather than posting an
 *   empty doc.
 */
export function buildDescriptionAdf(
  paragraphs: readonly string[],
): AdfDoc | undefined {
  const content: AdfNode[] = paragraphs
    .map((text) => text.trim())
    .filter((text) => text.length > 0)
    .flatMap(convertMarkdown);

  if (content.length === 0) {
    return undefined;
  }

  return { version: 1, type: "doc", content };
}

/**
 * Build an ADF document from a comment body written as markdown.
 *
 * Blank lines become paragraph breaks as part of markdown parsing, so unlike
 * `buildDescriptionAdf` this takes the body as a single string and does no
 * pre-splitting.
 */
export function buildCommentAdf(text: string): AdfDoc {
  return { version: 1, type: "doc", content: convertMarkdown(text.trim()) };
}
