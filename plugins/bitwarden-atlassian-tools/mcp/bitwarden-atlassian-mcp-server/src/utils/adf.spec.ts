import { describe, it, expect } from 'vitest';
import { extractPlainText, extractPlainTextTruncated } from './adf.js';

describe('extractPlainText', () => {
  it('should return empty string for null input', () => {
    expect(extractPlainText(null)).toBe('');
  });

  it('should return empty string for undefined input', () => {
    expect(extractPlainText(undefined)).toBe('');
  });

  it('should return empty string for object without content', () => {
    expect(extractPlainText({})).toBe('');
    expect(extractPlainText({ type: 'doc' })).toBe('');
  });

  it('should return empty string for empty content array', () => {
    expect(extractPlainText({ content: [] })).toBe('');
  });

  it('should extract text from simple paragraph', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Hello world' }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('Hello world');
  });

  it('should join multiple text nodes in a paragraph', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Hello ' },
            { type: 'text', text: 'world' },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('Hello world');
  });

  it('should add newlines between paragraphs', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'First paragraph' }],
        },
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Second paragraph' }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('First paragraph\nSecond paragraph');
  });

  it('should handle headings', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'heading',
          content: [{ type: 'text', text: 'My Heading' }],
        },
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Body text' }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('My Heading\nBody text');
  });

  it('should handle codeBlocks', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'codeBlock',
          content: [{ type: 'text', text: 'const x = 1;' }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('const x = 1;');
  });

  it('should handle hardBreak nodes', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Line 1' },
            { type: 'hardBreak' },
            { type: 'text', text: 'Line 2' },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('Line 1\nLine 2');
  });

  // ─── Smartlinks ───

  it('should extract URL from inlineCard', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'See ' },
            { type: 'inlineCard', attrs: { url: 'https://example.com/page' } },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('See https://example.com/page');
  });

  it('should handle inlineCard without attrs', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'inlineCard' }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('');
  });

  it('should extract URL from blockCard with trailing newline', () => {
    const adf = {
      type: 'doc',
      content: [
        { type: 'blockCard', attrs: { url: 'https://example.com/card' } },
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'After card' }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('https://example.com/card\nAfter card');
  });

  it('should extract URL from embedCard with trailing newline', () => {
    const adf = {
      type: 'doc',
      content: [
        { type: 'embedCard', attrs: { url: 'https://example.com/embed' } },
      ],
    };
    expect(extractPlainText(adf)).toBe('https://example.com/embed');
  });

  it('should handle blockCard without attrs', () => {
    const adf = {
      type: 'doc',
      content: [{ type: 'blockCard' }],
    };
    expect(extractPlainText(adf)).toBe('');
  });

  // ─── Link marks ───

  it('should append URL in parens for text with link mark', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            {
              type: 'text',
              text: 'click here',
              marks: [{ type: 'link', attrs: { href: 'https://example.com' } }],
            },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('click here (https://example.com)');
  });

  it('should render plain text when link mark has no href', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            {
              type: 'text',
              text: 'no link',
              marks: [{ type: 'link', attrs: {} }],
            },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('no link');
  });

  it('should ignore non-link marks', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            {
              type: 'text',
              text: 'bold text',
              marks: [{ type: 'strong' }],
            },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('bold text');
  });

  // ─── Mentions ───

  it('should extract mention text from attrs.text', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Assigned to ' },
            { type: 'mention', attrs: { text: '@John Doe', id: '123' } },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('Assigned to @John Doe');
  });

  it('should fall back to attrs.displayName for mention', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'mention', attrs: { displayName: 'Jane Smith' } },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('Jane Smith');
  });

  it('should handle mention without attrs', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'mention' }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('');
  });

  // ─── Emoji ───

  it('should extract emoji shortName', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'emoji', attrs: { shortName: ':thumbsup:' } },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe(':thumbsup:');
  });

  it('should fall back to emoji text', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'emoji', attrs: { text: '👍' } },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('👍');
  });

  it('should handle emoji without attrs', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'emoji' }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('');
  });

  // ─── Status ───

  it('should wrap status text in brackets', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'status', attrs: { text: 'IN PROGRESS', color: 'blue' } },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('[IN PROGRESS]');
  });

  it('should handle status without text', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'status', attrs: {} }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('');
  });

  // ─── Date ───

  it('should format date as YYYY-MM-DD', () => {
    // 2024-06-15 in ms (UTC midnight)
    const ts = Date.UTC(2024, 5, 15).toString();
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'date', attrs: { timestamp: ts } }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('2024-06-15');
  });

  it('should handle date without timestamp', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'date', attrs: {} }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('');
  });

  // ─── Media ───

  it('should extract alt text from mediaInline', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'mediaInline', attrs: { alt: 'screenshot.png', id: '1' } },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('[screenshot.png]');
  });

  it('should show placeholder for media without alt', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'media', attrs: { id: '1', type: 'file' } }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('[attachment]');
  });

  it('should handle mediaSingle wrapping media', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'mediaSingle',
          content: [
            { type: 'media', attrs: { alt: 'diagram.png', id: '1', type: 'file' } },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('[diagram.png]');
  });

  // ─── Rule ───

  it('should render rule as horizontal separator', () => {
    const adf = {
      type: 'doc',
      content: [
        { type: 'rule' },
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'After rule' }],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('---\nAfter rule');
  });

  // ─── Bullet lists ───

  it('should format bullet list items', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'bulletList',
          content: [
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'Alpha' }] },
              ],
            },
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'Beta' }] },
              ],
            },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('- Alpha\n- Beta');
  });

  // ─── Ordered lists ───

  it('should format ordered list items with numbers', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'orderedList',
          content: [
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'First' }] },
              ],
            },
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'Second' }] },
              ],
            },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('1. First\n2. Second');
  });

  it('should respect custom start order', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'orderedList',
          attrs: { order: 5 },
          content: [
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'Five' }] },
              ],
            },
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'Six' }] },
              ],
            },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('5. Five\n6. Six');
  });

  it('should handle nested lists', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'bulletList',
          content: [
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'Parent' }] },
                {
                  type: 'bulletList',
                  content: [
                    {
                      type: 'listItem',
                      content: [
                        { type: 'paragraph', content: [{ type: 'text', text: 'Child' }] },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
    };
    const result = extractPlainText(adf);
    expect(result).toContain('- Parent');
    expect(result).toContain('Child');
  });

  it('should handle multi-paragraph list items', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'bulletList',
          content: [
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'Line A' }] },
                { type: 'paragraph', content: [{ type: 'text', text: 'Line B' }] },
              ],
            },
          ],
        },
      ],
    };
    const result = extractPlainText(adf);
    expect(result).toBe('- Line A\n  Line B');
  });

  // ─── Blockquote ───

  it('should prefix blockquote lines with >', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'blockquote',
          content: [
            { type: 'paragraph', content: [{ type: 'text', text: 'Quoted text' }] },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('> Quoted text');
  });

  it('should prefix multiple paragraphs in blockquote', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'blockquote',
          content: [
            { type: 'paragraph', content: [{ type: 'text', text: 'First' }] },
            { type: 'paragraph', content: [{ type: 'text', text: 'Second' }] },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('> First\n> Second');
  });

  // ─── Expand ───

  it('should render expand with title and content', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'expand',
          attrs: { title: 'Details' },
          content: [
            { type: 'paragraph', content: [{ type: 'text', text: 'Hidden content' }] },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('**Details**\nHidden content');
  });

  it('should render expand without title', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'expand',
          attrs: {},
          content: [
            { type: 'paragraph', content: [{ type: 'text', text: 'Content only' }] },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('Content only');
  });

  it('should render nestedExpand', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'nestedExpand',
          attrs: { title: 'Nested' },
          content: [
            { type: 'paragraph', content: [{ type: 'text', text: 'Inner' }] },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('**Nested**\nInner');
  });

  // ─── Tables ───

  it('should render table with header and data rows', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'table',
          content: [
            {
              type: 'tableRow',
              content: [
                {
                  type: 'tableHeader',
                  content: [
                    { type: 'paragraph', content: [{ type: 'text', text: 'Name' }] },
                  ],
                },
                {
                  type: 'tableHeader',
                  content: [
                    { type: 'paragraph', content: [{ type: 'text', text: 'Value' }] },
                  ],
                },
              ],
            },
            {
              type: 'tableRow',
              content: [
                {
                  type: 'tableCell',
                  content: [
                    { type: 'paragraph', content: [{ type: 'text', text: 'foo' }] },
                  ],
                },
                {
                  type: 'tableCell',
                  content: [
                    { type: 'paragraph', content: [{ type: 'text', text: 'bar' }] },
                  ],
                },
              ],
            },
          ],
        },
      ],
    };
    const result = extractPlainText(adf);
    expect(result).toContain('| Name | Value');
    expect(result).toContain('| foo | bar');
  });

  // ─── Mixed inline nodes ───

  it('should handle mixed inline nodes in one paragraph', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Hello ' },
            { type: 'mention', attrs: { text: '@Alice' } },
            { type: 'text', text: ' ' },
            { type: 'emoji', attrs: { shortName: ':wave:' } },
            { type: 'text', text: ' status: ' },
            { type: 'status', attrs: { text: 'DONE', color: 'green' } },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('Hello @Alice :wave: status: [DONE]');
  });

  // ─── Full integration test ───

  it('should handle a realistic full description', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'heading',
          content: [{ type: 'text', text: 'Bug Report' }],
        },
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Reported by ' },
            { type: 'mention', attrs: { text: '@dev-team' } },
          ],
        },
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'See ' },
            { type: 'inlineCard', attrs: { url: 'https://jira.example.com/PROJ-1' } },
          ],
        },
        {
          type: 'bulletList',
          content: [
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'Step 1' }] },
              ],
            },
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'Step 2' }] },
              ],
            },
          ],
        },
        {
          type: 'blockquote',
          content: [
            { type: 'paragraph', content: [{ type: 'text', text: 'Error message here' }] },
          ],
        },
        { type: 'rule' },
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'End of report' }],
        },
      ],
    };
    const result = extractPlainText(adf);
    expect(result).toContain('Bug Report');
    expect(result).toContain('@dev-team');
    expect(result).toContain('https://jira.example.com/PROJ-1');
    expect(result).toContain('- Step 1');
    expect(result).toContain('- Step 2');
    expect(result).toContain('> Error message here');
    expect(result).toContain('---');
    expect(result).toContain('End of report');
  });

  // ─── Deeply nested content (updated from original) ───

  it('should handle deeply nested content with proper formatting', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'bulletList',
          content: [
            {
              type: 'listItem',
              content: [
                {
                  type: 'paragraph',
                  content: [{ type: 'text', text: 'Item 1' }],
                },
              ],
            },
            {
              type: 'listItem',
              content: [
                {
                  type: 'paragraph',
                  content: [{ type: 'text', text: 'Item 2' }],
                },
              ],
            },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('- Item 1\n- Item 2');
  });

  it('should handle orderedList without attrs', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'orderedList',
          content: [
            {
              type: 'listItem',
              content: [
                { type: 'paragraph', content: [{ type: 'text', text: 'A' }] },
              ],
            },
          ],
        },
      ],
    };
    expect(extractPlainText(adf)).toBe('1. A');
  });

  it('should handle empty bulletList', () => {
    const adf = {
      type: 'doc',
      content: [{ type: 'bulletList' }],
    };
    expect(extractPlainText(adf)).toBe('');
  });

  it('should handle empty orderedList', () => {
    const adf = {
      type: 'doc',
      content: [{ type: 'orderedList' }],
    };
    expect(extractPlainText(adf)).toBe('');
  });
});

describe('extractPlainTextTruncated', () => {
  it('should return empty string for null input', () => {
    expect(extractPlainTextTruncated(null)).toBe('');
  });

  it('should return empty string for undefined input', () => {
    expect(extractPlainTextTruncated(undefined)).toBe('');
  });

  it('should extract text from paragraphs only', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Hello world' }],
        },
      ],
    };
    expect(extractPlainTextTruncated(adf)).toBe('Hello world');
  });

  it('should truncate to default 200 chars with ellipsis', () => {
    const longText = 'A'.repeat(300);
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: longText }],
        },
      ],
    };
    const result = extractPlainTextTruncated(adf);
    expect(result).toHaveLength(203); // 200 + '...'
    expect(result.endsWith('...')).toBe(true);
  });

  it('should not add ellipsis for short text', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Short' }],
        },
      ],
    };
    expect(extractPlainTextTruncated(adf)).toBe('Short');
  });

  it('should respect custom maxLength', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'Hello world this is a test' }],
        },
      ],
    };
    const result = extractPlainTextTruncated(adf, 10);
    expect(result).toBe('Hello worl...');
  });

  it('should extract inlineCard URL in paragraph', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Link:' },
            { type: 'inlineCard', attrs: { url: 'https://example.com' } },
          ],
        },
      ],
    };
    expect(extractPlainTextTruncated(adf)).toBe('Link: https://example.com');
  });

  it('should extract mention text in paragraph', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'By' },
            { type: 'mention', attrs: { text: '@Alice' } },
          ],
        },
      ],
    };
    expect(extractPlainTextTruncated(adf)).toBe('By @Alice');
  });

  it('should handle mixed content types in truncated extraction', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Hello' },
            { type: 'mention', attrs: { text: '@Bob' } },
            { type: 'text', text: 'see' },
            { type: 'inlineCard', attrs: { url: 'https://example.com' } },
          ],
        },
      ],
    };
    expect(extractPlainTextTruncated(adf)).toBe('Hello @Bob see https://example.com');
  });

  it('should truncate mixed content at boundary', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'AAAA' },
            { type: 'mention', attrs: { text: '@Bob' } },
          ],
        },
      ],
    };
    const result = extractPlainTextTruncated(adf, 7);
    expect(result).toBe('AAAA @B...');
  });

  it('should skip inlineCard without attrs in truncated', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Before' },
            { type: 'inlineCard' },
            { type: 'text', text: 'After' },
          ],
        },
      ],
    };
    expect(extractPlainTextTruncated(adf)).toBe('Before After');
  });

  it('should skip mention without text in truncated', () => {
    const adf = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Assigned ' },
            { type: 'mention', attrs: {} },
          ],
        },
      ],
    };
    expect(extractPlainTextTruncated(adf)).toBe('Assigned');
  });
});
