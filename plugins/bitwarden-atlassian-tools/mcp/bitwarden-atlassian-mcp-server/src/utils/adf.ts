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

  function traverseListItem(node: any, ordered: boolean, index: number) {
    const saved = text;
    text = '';
    if (node.content) {
      for (const child of node.content) {
        traverse(child);
      }
    }
    const itemText = text.trimEnd();
    text = saved;
    const prefix = ordered ? `${index}. ` : '- ';
    const lines = itemText.split('\n');
    const indented = lines
      .map((line: string, i: number) => (i === 0 ? prefix + line : '  ' + line))
      .join('\n');
    text += indented + '\n';
  }

  function traverse(node: any) {
    if (node.type === 'text') {
      const linkMark = node.marks?.find((m: any) => m.type === 'link');
      if (linkMark?.attrs?.href) {
        text += node.text + ' (' + linkMark.attrs.href + ')';
      } else {
        text += node.text;
      }
    } else if (node.type === 'hardBreak') {
      text += '\n';
    } else if (node.type === 'inlineCard') {
      if (node.attrs?.url) {
        text += node.attrs.url;
      }
    } else if (node.type === 'blockCard' || node.type === 'embedCard') {
      if (node.attrs?.url) {
        text += node.attrs.url + '\n';
      }
    } else if (node.type === 'mention') {
      text += node.attrs?.text || node.attrs?.displayName || '';
    } else if (node.type === 'emoji') {
      if (node.attrs?.shortName) {
        text += node.attrs.shortName;
      } else if (node.attrs?.text) {
        text += node.attrs.text;
      }
    } else if (node.type === 'status') {
      if (node.attrs?.text) {
        text += '[' + node.attrs.text + ']';
      }
    } else if (node.type === 'date') {
      if (node.attrs?.timestamp) {
        const ts = Number(node.attrs.timestamp);
        text += new Date(ts).toISOString().slice(0, 10);
      }
    } else if (node.type === 'mediaInline' || node.type === 'media') {
      text += node.attrs?.alt ? '[' + node.attrs.alt + ']' : '[attachment]';
    } else if (node.type === 'rule') {
      text += '---\n';
    } else if (node.type === 'bulletList') {
      if (node.content) {
        for (const child of node.content) {
          traverseListItem(child, false, 0);
        }
      }
    } else if (node.type === 'orderedList') {
      const start = node.attrs?.order ?? 1;
      if (node.content) {
        for (let i = 0; i < node.content.length; i++) {
          traverseListItem(node.content[i], true, start + i);
        }
      }
    } else if (node.type === 'blockquote') {
      const saved = text;
      text = '';
      if (node.content) {
        for (const child of node.content) {
          traverse(child);
        }
      }
      const inner = text;
      text = saved;
      const lines = inner.replace(/\n$/, '').split('\n');
      text += lines.map((line: string) => '> ' + line).join('\n') + '\n';
    } else if (node.type === 'expand' || node.type === 'nestedExpand') {
      if (node.attrs?.title) {
        text += '**' + node.attrs.title + '**\n';
      }
      if (node.content) {
        for (const child of node.content) {
          traverse(child);
        }
      }
    } else if (node.type === 'table') {
      if (node.content) {
        for (const row of node.content) {
          traverse(row);
        }
      }
    } else if (node.type === 'tableRow') {
      if (node.content) {
        for (const cell of node.content) {
          traverse(cell);
        }
        text += '\n';
      }
    } else if (node.type === 'tableHeader' || node.type === 'tableCell') {
      const saved = text;
      text = '';
      if (node.content) {
        for (const child of node.content) {
          traverse(child);
        }
      }
      const cellText = text.trim();
      text = saved;
      text += '| ' + cellText + ' ';
    } else if (node.content) {
      for (const child of node.content) {
        traverse(child);
      }
      // Add newline after paragraphs, headings, etc.
      if (
        ['paragraph', 'heading', 'codeBlock', 'mediaSingle', 'mediaGroup'].includes(node.type)
      ) {
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
        } else if (contentNode.type === 'inlineCard') {
          if (contentNode.attrs?.url) {
            text += contentNode.attrs.url + ' ';
          }
        } else if (contentNode.type === 'mention') {
          if (contentNode.attrs?.text) {
            text += contentNode.attrs.text + ' ';
          }
        }
      }
    }
  }

  const trimmed = text.trim();
  return trimmed.substring(0, maxLength) + (trimmed.length > maxLength ? '...' : '');
}
