/**
 * ADF (Atlassian Document Format) utilities
 * Shared extraction logic for converting ADF to plain text
 */

/**
 * Extract plain text from JIRA ADF (Atlassian Document Format)
 */
export function extractPlainText(adf: any): string {
  if (!adf || !adf.content) return '';

  let text = '';

  function traverse(node: any) {
    if (node.type === 'text') {
      text += node.text;
    } else if (node.type === 'hardBreak') {
      text += '\n';
    } else if (node.content) {
      for (const child of node.content) {
        traverse(child);
      }
      // Add newline after paragraphs, headings, etc.
      if (['paragraph', 'heading', 'codeBlock'].includes(node.type)) {
        text += '\n';
      }
    }
  }

  for (const node of adf.content) {
    traverse(node);
  }

  return text.trim();
}

/**
 * Extract plain text from ADF with truncation for search results
 */
export function extractPlainTextTruncated(adf: any, maxLength: number = 200): string {
  if (!adf || !adf.content) return '';

  let text = '';
  for (const node of adf.content) {
    if (node.type === 'paragraph' && node.content) {
      for (const contentNode of node.content) {
        if (contentNode.type === 'text') {
          text += contentNode.text + ' ';
        }
      }
    }
  }

  const trimmed = text.trim();
  return trimmed.substring(0, maxLength) + (trimmed.length > maxLength ? '...' : '');
}
