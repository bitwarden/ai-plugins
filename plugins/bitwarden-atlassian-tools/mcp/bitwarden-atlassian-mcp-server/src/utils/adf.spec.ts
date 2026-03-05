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

  it('should handle deeply nested content', () => {
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
    expect(extractPlainText(adf)).toContain('Item 1');
    expect(extractPlainText(adf)).toContain('Item 2');
  });

  it('should skip nodes without text or content', () => {
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
    expect(extractPlainText(adf)).toBe('After rule');
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
});
