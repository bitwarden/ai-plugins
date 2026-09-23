/**
 * ADF construction for Jira writes.
 *
 * The counterpart to `adf.ts`, which extracts plain text out of ADF for reads.
 *
 * This is deliberately small. Acceptance criteria are NOT built here: the PM
 * project exposes `Acceptance criteria` (customfield_10192) as a plain textarea,
 * so Gherkin is sent as a string and needs no ADF at all. That leaves the
 * description, which is prose paragraphs.
 */

export interface AdfTextNode {
  type: "text";
  text: string;
}

export interface AdfParagraph {
  type: "paragraph";
  content: AdfTextNode[];
}

export interface AdfDoc {
  version: 1;
  type: "doc";
  content: AdfParagraph[];
}

/**
 * Build an ADF document from discrete paragraphs of plain text.
 *
 * @param paragraphs - Paragraph strings. Empty and whitespace-only entries are
 *   dropped, since Jira renders an empty paragraph as visible dead space.
 * @returns An ADF doc, or undefined when there is nothing to send so the caller
 *   can omit the description field entirely rather than posting an empty doc.
 */
export function buildDescriptionAdf(
  paragraphs: readonly string[],
): AdfDoc | undefined {
  const content: AdfParagraph[] = paragraphs
    .map((text) => text.trim())
    .filter((text) => text.length > 0)
    .map((text) => ({
      type: "paragraph" as const,
      content: [{ type: "text" as const, text }],
    }));

  if (content.length === 0) {
    return undefined;
  }

  return { version: 1, type: "doc", content };
}

/**
 * Build an ADF document from a single block of plain text, splitting on blank
 * lines so a caller can write a multi-paragraph comment as one string.
 */
export function buildCommentAdf(text: string): AdfDoc {
  const paragraphs = text.split(/\n\s*\n/);
  const doc = buildDescriptionAdf(paragraphs);

  // Comment bodies are validated non-empty by the schema before reaching here,
  // so splitting can only ever yield at least one non-blank paragraph.
  return doc as AdfDoc;
}
