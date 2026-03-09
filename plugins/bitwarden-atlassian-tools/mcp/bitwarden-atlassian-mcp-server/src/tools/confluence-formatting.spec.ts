import { describe, it, expect, vi, beforeEach } from 'vitest';

/**
 * Tests for Confluence tool handler formatting.
 *
 * Format functions are private to each tool file. We test through
 * tool handlers by mocking ConfluenceClient.
 */

const mockGetPage = vi.fn();
const mockSearchPages = vi.fn();
const mockGetPageComments = vi.fn();
const mockGetPageInlineComments = vi.fn();
const mockGetCommentReplies = vi.fn();
const mockGetInlineCommentReplies = vi.fn();
const mockGetChildPages = vi.fn();
const mockListSpaces = vi.fn();
const mockSearchCql = vi.fn();

vi.mock('../confluence/client.js', () => {
  return {
    ConfluenceClient: vi.fn().mockImplementation(() => ({
      getPage: mockGetPage,
      searchPages: mockSearchPages,
      getPageWithContent: vi.fn(),
      testConnection: vi.fn(),
      getPageComments: mockGetPageComments,
      getCommentReplies: mockGetCommentReplies,
      getPageInlineComments: mockGetPageInlineComments,
      getInlineCommentReplies: mockGetInlineCommentReplies,
      getChildPages: mockGetChildPages,
      listSpaces: mockListSpaces,
      searchCql: mockSearchCql,
    })),
  };
});

import getConfluencePageTool from './get-confluence-page.js';
import getConfluencePageCommentsTool from './get-confluence-page-comments.js';
import getChildPagesTool from './get-child-pages.js';
import listSpacesTool from './list-spaces.js';
import searchConfluenceTool from './search-confluence.js';
import searchConfluenceCqlTool from './search-confluence-cql.js';

beforeEach(() => {
  vi.clearAllMocks();
  delete process.env.ATLASSIAN_CONFLUENCE_URL;
  delete process.env.ATLASSIAN_JIRA_URL;
});

// ── get_confluence_page ─────────────────────────────────────────────

describe('get_confluence_page formatting', () => {
  it('should format basic page details', async () => {
    mockGetPage.mockResolvedValueOnce({
      title: 'Test Page',
      id: '12345',
      status: 'current',
    });

    const result = await getConfluencePageTool.handler({ pageId: '12345' });
    expect(result).toContain('# Test Page');
    expect(result).toContain('**Page ID:** 12345');
    expect(result).toContain('**Status:** current');
  });

  it('should include space info when present', async () => {
    mockGetPage.mockResolvedValueOnce({
      title: 'Page',
      id: '1',
      status: 'current',
      space: { name: 'Engineering', key: 'EN' },
    });

    const result = await getConfluencePageTool.handler({ pageId: '1' });
    expect(result).toContain('**Space:** Engineering (EN)');
  });

  it('should include version and modified by when present', async () => {
    mockGetPage.mockResolvedValueOnce({
      title: 'Page',
      id: '1',
      status: 'current',
      version: {
        number: 5,
        when: '2026-01-15T10:00:00.000Z',
        by: { displayName: 'Jane Doe' },
      },
    });

    const result = await getConfluencePageTool.handler({ pageId: '1' });
    expect(result).toContain('**Version:** 5');
    expect(result).toContain('**Modified By:** Jane Doe');
  });

  it('should use absolute webui URL as-is', async () => {
    mockGetPage.mockResolvedValueOnce({
      title: 'Page',
      id: '1',
      status: 'current',
      _links: { webui: 'https://company.atlassian.net/wiki/spaces/EN/pages/1' },
    });

    const result = await getConfluencePageTool.handler({ pageId: '1' });
    expect(result).toContain('**URL:** https://company.atlassian.net/wiki/spaces/EN/pages/1');
  });

  it('should prepend ATLASSIAN_CONFLUENCE_URL for relative webui URL', async () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://company.atlassian.net';
    mockGetPage.mockResolvedValueOnce({
      title: 'Page',
      id: '1',
      status: 'current',
      _links: { webui: '/wiki/spaces/EN/pages/1' },
    });

    const result = await getConfluencePageTool.handler({ pageId: '1' });
    expect(result).toContain('**URL:** https://company.atlassian.net/wiki/spaces/EN/pages/1');
  });

  it('should fall back to ATLASSIAN_JIRA_URL for relative webui URL', async () => {
    process.env.ATLASSIAN_JIRA_URL = 'https://jira.example.com';
    mockGetPage.mockResolvedValueOnce({
      title: 'Page',
      id: '1',
      status: 'current',
      _links: { webui: '/wiki/spaces/EN/pages/1' },
    });

    const result = await getConfluencePageTool.handler({ pageId: '1' });
    expect(result).toContain('**URL:** https://jira.example.com/wiki/spaces/EN/pages/1');
  });

  it('should render body from storage format', async () => {
    mockGetPage.mockResolvedValueOnce({
      title: 'Page',
      id: '1',
      status: 'current',
      body: { storage: { value: '<p>Hello world</p>' } },
    });

    const result = await getConfluencePageTool.handler({ pageId: '1' });
    expect(result).toContain('## Content');
    expect(result).toContain('Hello world');
  });

  it('should fall back to view format when storage absent', async () => {
    mockGetPage.mockResolvedValueOnce({
      title: 'Page',
      id: '1',
      status: 'current',
      body: { view: { value: '<p>View content</p>' } },
    });

    const result = await getConfluencePageTool.handler({ pageId: '1' });
    expect(result).toContain('## Content');
    expect(result).toContain('View content');
  });

  it('should show no content message when body is empty', async () => {
    mockGetPage.mockResolvedValueOnce({
      title: 'Page',
      id: '1',
      status: 'current',
    });

    const result = await getConfluencePageTool.handler({ pageId: '1' });
    expect(result).toContain('_No content available_');
  });

  it('should return error message on failure', async () => {
    mockGetPage.mockRejectedValueOnce(new Error('Connection refused'));

    const result = await getConfluencePageTool.handler({ pageId: '1' });
    expect(result).toContain('Error retrieving Confluence page');
    expect(result).toContain('Connection refused');
  });

  it('should convert HTML storage content to readable text', async () => {
    const html =
      '<h1>Title</h1><p><strong>Bold</strong> and <em>italic</em> and <code>code</code></p><ul><li>Item 1</li><li>Item 2</li></ul><p>A &amp; B &lt; C</p><br/><br/><br/><br/>';
    mockGetPage.mockResolvedValueOnce({
      title: 'Page',
      id: '1',
      status: 'current',
      body: { storage: { value: html } },
    });

    const result = await getConfluencePageTool.handler({ pageId: '1' });
    expect(result).toContain('# Title');
    expect(result).toContain('**Bold**');
    expect(result).toContain('_italic_');
    expect(result).toContain('`code`');
    expect(result).toContain('- Item 1');
    expect(result).toContain('A & B < C');
    // Should not have 3+ consecutive newlines
    expect(result).not.toMatch(/\n{4,}/);
  });
});

// ── get_confluence_page_comments ────────────────────────────────────

describe('get_confluence_page_comments formatting', () => {
  it('should show footer comments section with count', async () => {
    mockGetPageComments.mockResolvedValueOnce({
      results: [
        {
          id: 'c1',
          version: { by: { displayName: 'Alice' }, when: '2026-01-01T00:00:00.000Z' },
          createdAt: '2026-01-01T00:00:00.000Z',
          body: { storage: { value: '<p>Footer comment</p>' } },
        },
      ],
    });
    mockGetPageInlineComments.mockResolvedValueOnce({ results: [] });
    mockGetCommentReplies.mockResolvedValueOnce({ results: [] });

    const result = await getConfluencePageCommentsTool.handler({ pageId: '100' });
    expect(result).toContain('## Footer Comments (1)');
    expect(result).toContain('Footer comment');
  });

  it('should show inline comments section with count', async () => {
    mockGetPageComments.mockResolvedValueOnce({ results: [] });
    mockGetPageInlineComments.mockResolvedValueOnce({
      results: [
        {
          id: 'ic1',
          version: { by: { displayName: 'Bob' }, when: '2026-02-01T00:00:00.000Z' },
          createdAt: '2026-02-01T00:00:00.000Z',
          body: { storage: { value: '<p>Inline note</p>' } },
        },
      ],
    });
    mockGetInlineCommentReplies.mockResolvedValueOnce({ results: [] });

    const result = await getConfluencePageCommentsTool.handler({ pageId: '100' });
    expect(result).toContain('## Inline Comments (1)');
    expect(result).toContain('Inline note');
  });

  it('should show comment author and date from createdAt', async () => {
    mockGetPageComments.mockResolvedValueOnce({
      results: [
        {
          id: 'c1',
          version: { by: { displayName: 'Alice' } },
          createdAt: '2026-03-01T12:00:00.000Z',
          body: { storage: { value: '<p>Comment</p>' } },
        },
      ],
    });
    mockGetPageInlineComments.mockResolvedValueOnce({ results: [] });
    mockGetCommentReplies.mockResolvedValueOnce({ results: [] });

    const result = await getConfluencePageCommentsTool.handler({ pageId: '100' });
    expect(result).toContain('**Alice**');
  });

  it('should fall back to version.when for date', async () => {
    mockGetPageComments.mockResolvedValueOnce({
      results: [
        {
          id: 'c1',
          version: { by: { displayName: 'Alice' }, when: '2026-03-01T12:00:00.000Z' },
          body: { storage: { value: '<p>Comment</p>' } },
        },
      ],
    });
    mockGetPageInlineComments.mockResolvedValueOnce({ results: [] });
    mockGetCommentReplies.mockResolvedValueOnce({ results: [] });

    const result = await getConfluencePageCommentsTool.handler({ pageId: '100' });
    expect(result).toContain('**Alice**');
    // The date should be formatted (not "Unknown date")
    expect(result).not.toContain('Unknown date');
  });

  it('should show Unknown author when version is absent', async () => {
    mockGetPageComments.mockResolvedValueOnce({
      results: [
        {
          id: 'c1',
          createdAt: '2026-01-01T00:00:00.000Z',
          body: { storage: { value: '<p>Comment</p>' } },
        },
      ],
    });
    mockGetPageInlineComments.mockResolvedValueOnce({ results: [] });

    const result = await getConfluencePageCommentsTool.handler({
      pageId: '100',
      includeReplies: false,
    });
    expect(result).toContain('**Unknown**');
  });

  it('should show resolution status badge', async () => {
    mockGetPageComments.mockResolvedValueOnce({ results: [] });
    mockGetPageInlineComments.mockResolvedValueOnce({
      results: [
        {
          id: 'ic1',
          version: { by: { displayName: 'Bob' }, when: '2026-01-01T00:00:00.000Z' },
          createdAt: '2026-01-01T00:00:00.000Z',
          resolutionStatus: 'open',
          body: { storage: { value: '<p>Todo</p>' } },
        },
      ],
    });
    mockGetInlineCommentReplies.mockResolvedValueOnce({ results: [] });

    const result = await getConfluencePageCommentsTool.handler({ pageId: '100' });
    expect(result).toContain('[OPEN]');
  });

  it('should show inlineOriginalSelection as blockquote', async () => {
    mockGetPageComments.mockResolvedValueOnce({ results: [] });
    mockGetPageInlineComments.mockResolvedValueOnce({
      results: [
        {
          id: 'ic1',
          version: { by: { displayName: 'Bob' }, when: '2026-01-01T00:00:00.000Z' },
          createdAt: '2026-01-01T00:00:00.000Z',
          properties: { inlineOriginalSelection: 'selected text here' },
          body: { storage: { value: '<p>My comment</p>' } },
        },
      ],
    });
    mockGetInlineCommentReplies.mockResolvedValueOnce({ results: [] });

    const result = await getConfluencePageCommentsTool.handler({ pageId: '100' });
    expect(result).toContain('> "selected text here"');
  });

  it('should use view body format as fallback', async () => {
    mockGetPageComments.mockResolvedValueOnce({
      results: [
        {
          id: 'c1',
          version: { by: { displayName: 'Alice' }, when: '2026-01-01T00:00:00.000Z' },
          createdAt: '2026-01-01T00:00:00.000Z',
          body: { view: { value: '<p>View body</p>' } },
        },
      ],
    });
    mockGetPageInlineComments.mockResolvedValueOnce({ results: [] });
    mockGetCommentReplies.mockResolvedValueOnce({ results: [] });

    const result = await getConfluencePageCommentsTool.handler({ pageId: '100' });
    expect(result).toContain('View body');
  });

  it('should return no comments message when both empty', async () => {
    mockGetPageComments.mockResolvedValueOnce({ results: [] });
    mockGetPageInlineComments.mockResolvedValueOnce({ results: [] });

    const result = await getConfluencePageCommentsTool.handler({ pageId: '100' });
    expect(result).toContain('No comments found for page 100');
  });

  it('should fetch replies when includeReplies is true', async () => {
    mockGetPageComments.mockResolvedValueOnce({
      results: [
        {
          id: 'c1',
          version: { by: { displayName: 'Alice' }, when: '2026-01-01T00:00:00.000Z' },
          createdAt: '2026-01-01T00:00:00.000Z',
          body: { storage: { value: '<p>Parent</p>' } },
        },
      ],
    });
    mockGetPageInlineComments.mockResolvedValueOnce({ results: [] });
    mockGetCommentReplies.mockResolvedValueOnce({
      results: [
        {
          id: 'r1',
          version: { by: { displayName: 'Charlie' }, when: '2026-01-02T00:00:00.000Z' },
          createdAt: '2026-01-02T00:00:00.000Z',
          body: { storage: { value: '<p>Reply text</p>' } },
        },
      ],
    });

    const result = await getConfluencePageCommentsTool.handler({
      pageId: '100',
      includeReplies: true,
    });
    expect(result).toContain('Reply text');
    expect(mockGetCommentReplies).toHaveBeenCalled();
  });

  it('should silently swallow reply errors', async () => {
    mockGetPageComments.mockResolvedValueOnce({
      results: [
        {
          id: 'c1',
          version: { by: { displayName: 'Alice' }, when: '2026-01-01T00:00:00.000Z' },
          createdAt: '2026-01-01T00:00:00.000Z',
          body: { storage: { value: '<p>Parent</p>' } },
        },
      ],
    });
    mockGetPageInlineComments.mockResolvedValueOnce({ results: [] });
    mockGetCommentReplies.mockRejectedValueOnce(new Error('Reply fetch failed'));

    const result = await getConfluencePageCommentsTool.handler({
      pageId: '100',
      includeReplies: true,
    });
    // Should not contain error, should still show parent comment
    expect(result).toContain('Parent');
    expect(result).not.toContain('Reply fetch failed');
  });

  it('should not fetch replies when includeReplies is false', async () => {
    mockGetPageComments.mockResolvedValueOnce({
      results: [
        {
          id: 'c1',
          version: { by: { displayName: 'Alice' }, when: '2026-01-01T00:00:00.000Z' },
          createdAt: '2026-01-01T00:00:00.000Z',
          body: { storage: { value: '<p>Comment</p>' } },
        },
      ],
    });
    mockGetPageInlineComments.mockResolvedValueOnce({ results: [] });

    await getConfluencePageCommentsTool.handler({
      pageId: '100',
      includeReplies: false,
    });
    expect(mockGetCommentReplies).not.toHaveBeenCalled();
    expect(mockGetInlineCommentReplies).not.toHaveBeenCalled();
  });

  it('should return error on failure', async () => {
    mockGetPageComments.mockRejectedValueOnce(new Error('Server error'));

    const result = await getConfluencePageCommentsTool.handler({ pageId: '100' });
    expect(result).toContain('Error retrieving Confluence page comments');
    expect(result).toContain('Server error');
  });
});

// ── get_child_pages ─────────────────────────────────────────────────

describe('get_child_pages formatting', () => {
  it('should format child page with title, ID, status', async () => {
    mockGetChildPages.mockResolvedValueOnce({
      results: [{ title: 'Child Page', id: '200', status: 'current' }],
    });

    const result = await getChildPagesTool.handler({ pageId: '100' });
    expect(result).toContain('**Child Page** (ID: 200)');
    expect(result).toContain('- Status: current');
  });

  it('should include version info', async () => {
    mockGetChildPages.mockResolvedValueOnce({
      results: [
        {
          title: 'Child',
          id: '200',
          status: 'current',
          version: { when: '2026-01-15T10:00:00.000Z', by: { displayName: 'Jane' } },
        },
      ],
    });

    const result = await getChildPagesTool.handler({ pageId: '100' });
    expect(result).toContain('- Modified By: Jane');
  });

  it('should construct URL with ATLASSIAN_CONFLUENCE_URL for relative links', async () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://company.atlassian.net';
    mockGetChildPages.mockResolvedValueOnce({
      results: [
        {
          title: 'Child',
          id: '200',
          status: 'current',
          _links: { webui: '/wiki/spaces/EN/pages/200' },
        },
      ],
    });

    const result = await getChildPagesTool.handler({ pageId: '100' });
    expect(result).toContain('- URL: https://company.atlassian.net/wiki/spaces/EN/pages/200');
  });

  it('should show empty results message', async () => {
    mockGetChildPages.mockResolvedValueOnce({ results: [] });

    const result = await getChildPagesTool.handler({ pageId: '100' });
    expect(result).toContain('No child pages found');
  });

  it('should show found count in header', async () => {
    mockGetChildPages.mockResolvedValueOnce({
      results: [
        { title: 'A', id: '1', status: 'current' },
        { title: 'B', id: '2', status: 'current' },
      ],
    });

    const result = await getChildPagesTool.handler({ pageId: '100' });
    expect(result).toContain('**Found:** 2 page(s)');
  });

  it('should return error on failure', async () => {
    mockGetChildPages.mockRejectedValueOnce(new Error('Not found'));

    const result = await getChildPagesTool.handler({ pageId: '100' });
    expect(result).toContain('Error getting child pages');
    expect(result).toContain('Not found');
  });
});

// ── list_spaces ─────────────────────────────────────────────────────

describe('list_spaces formatting', () => {
  it('should format space with name, key, ID, type, status', async () => {
    mockListSpaces.mockResolvedValueOnce({
      results: [{ name: 'Engineering', key: 'EN', id: 's1', type: 'global', status: 'current' }],
    });

    const result = await listSpacesTool.handler({});
    expect(result).toContain('**Engineering** (EN)');
    expect(result).toContain('- ID: s1');
    expect(result).toContain('- Type: global');
    expect(result).toContain('- Status: current');
  });

  it('should construct URL for relative links', async () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://company.atlassian.net';
    mockListSpaces.mockResolvedValueOnce({
      results: [
        {
          name: 'EN',
          key: 'EN',
          id: 's1',
          type: 'global',
          status: 'current',
          _links: { webui: '/wiki/spaces/EN' },
        },
      ],
    });

    const result = await listSpacesTool.handler({});
    expect(result).toContain('- URL: https://company.atlassian.net/wiki/spaces/EN');
  });

  it('should show empty results message', async () => {
    mockListSpaces.mockResolvedValueOnce({ results: [] });

    const result = await listSpacesTool.handler({});
    expect(result).toContain('No accessible spaces found');
  });

  it('should show found count', async () => {
    mockListSpaces.mockResolvedValueOnce({
      results: [
        { name: 'A', key: 'A', id: '1', type: 'global', status: 'current' },
        { name: 'B', key: 'B', id: '2', type: 'personal', status: 'current' },
      ],
    });

    const result = await listSpacesTool.handler({});
    expect(result).toContain('**Found:** 2 space(s)');
  });

  it('should have Confluence Spaces header', async () => {
    mockListSpaces.mockResolvedValueOnce({ results: [] });

    const result = await listSpacesTool.handler({});
    expect(result).toContain('# Confluence Spaces');
  });

  it('should return error on failure', async () => {
    mockListSpaces.mockRejectedValueOnce(new Error('Timeout'));

    const result = await listSpacesTool.handler({});
    expect(result).toContain('Error listing spaces');
    expect(result).toContain('Timeout');
  });
});

// ── search_confluence ───────────────────────────────────────────────

describe('search_confluence formatting', () => {
  it('should return error when no search params provided', async () => {
    const result = await searchConfluenceTool.handler({});
    expect(result).toContain('At least one search parameter');
  });

  it('should display spaceKey', async () => {
    mockSearchPages.mockResolvedValueOnce({ results: [] });

    const result = await searchConfluenceTool.handler({ spaceKey: 'EN' });
    expect(result).toContain('**Space:** EN');
  });

  it('should display title filter', async () => {
    mockSearchPages.mockResolvedValueOnce({ results: [] });

    const result = await searchConfluenceTool.handler({ title: 'Architecture' });
    expect(result).toContain('**Title Filter:** "Architecture"');
  });

  it('should format page entry with details', async () => {
    mockSearchPages.mockResolvedValueOnce({
      results: [
        {
          title: 'API Guide',
          id: '500',
          type: 'page',
          status: 'current',
          space: { name: 'Engineering', key: 'EN' },
          version: { when: '2026-01-01T00:00:00.000Z', by: { displayName: 'Alice' } },
        },
      ],
    });

    const result = await searchConfluenceTool.handler({ spaceKey: 'EN' });
    expect(result).toContain('## API Guide');
    expect(result).toContain('**Page ID:** 500');
    expect(result).toContain('**Type:** page');
    expect(result).toContain('**Status:** current');
    expect(result).toContain('**Space:** Engineering (EN)');
  });

  it('should construct URL for pages', async () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://company.atlassian.net';
    mockSearchPages.mockResolvedValueOnce({
      results: [
        {
          title: 'Page',
          id: '1',
          type: 'page',
          status: 'current',
          _links: { webui: '/wiki/spaces/EN/pages/1' },
        },
      ],
    });

    const result = await searchConfluenceTool.handler({ spaceKey: 'EN' });
    expect(result).toContain('**URL:** https://company.atlassian.net/wiki/spaces/EN/pages/1');
  });

  it('should show empty results message', async () => {
    mockSearchPages.mockResolvedValueOnce({ results: [] });

    const result = await searchConfluenceTool.handler({ spaceKey: 'EMPTY' });
    expect(result).toContain('No pages found matching your criteria');
  });

  it('should show pagination note when _links.next present', async () => {
    mockSearchPages.mockResolvedValueOnce({
      results: [{ title: 'P', id: '1', type: 'page', status: 'current' }],
      _links: { next: '/wiki/api/v2/pages?cursor=abc' },
    });

    const result = await searchConfluenceTool.handler({ spaceKey: 'EN' });
    expect(result).toContain('More results available');
  });

  it('should return error on failure', async () => {
    mockSearchPages.mockRejectedValueOnce(new Error('Bad request'));

    const result = await searchConfluenceTool.handler({ spaceKey: 'EN' });
    expect(result).toContain('Error searching Confluence');
    expect(result).toContain('Bad request');
  });
});

// ── search_confluence_cql ───────────────────────────────────────────

describe('search_confluence_cql formatting', () => {
  it('should show CQL query in output', async () => {
    mockSearchCql.mockResolvedValueOnce({ results: [], size: 0, totalSize: 0 });

    const result = await searchConfluenceCqlTool.handler({ cql: 'space = "EN"' });
    expect(result).toContain('`space = "EN"`');
  });

  it('should display limit', async () => {
    mockSearchCql.mockResolvedValueOnce({ results: [], size: 0, totalSize: 0 });

    const result = await searchConfluenceCqlTool.handler({ cql: 'type = page', limit: 50 });
    expect(result).toContain('**Limit:** 50');
  });

  it('should display start when greater than 0', async () => {
    mockSearchCql.mockResolvedValueOnce({ results: [], size: 0, totalSize: 0 });

    const result = await searchConfluenceCqlTool.handler({ cql: 'type = page', start: 10 });
    expect(result).toContain('**Start:** 10');
  });

  it('should omit start when 0', async () => {
    mockSearchCql.mockResolvedValueOnce({ results: [], size: 0, totalSize: 0 });

    const result = await searchConfluenceCqlTool.handler({ cql: 'type = page', start: 0 });
    expect(result).not.toContain('**Start:**');
  });

  it('should format result item', async () => {
    mockSearchCql.mockResolvedValueOnce({
      results: [
        {
          title: 'Found Page',
          id: '999',
          type: 'page',
          status: 'current',
          space: { name: 'Eng', key: 'EN' },
        },
      ],
      size: 1,
      totalSize: 1,
    });

    const result = await searchConfluenceCqlTool.handler({ cql: 'text ~ "test"' });
    expect(result).toContain('## Found Page');
    expect(result).toContain('**Content ID:** 999');
    expect(result).toContain('**Type:** page');
    expect(result).toContain('**Status:** current');
    expect(result).toContain('**Space:** Eng (EN)');
  });

  it('should show size and totalSize from v1 API', async () => {
    mockSearchCql.mockResolvedValueOnce({
      results: [{ title: 'P', id: '1', type: 'page', status: 'current' }],
      size: 1,
      totalSize: 50,
    });

    const result = await searchConfluenceCqlTool.handler({ cql: 'space = "EN"' });
    expect(result).toContain('**Found:** 1 of 50 total result(s)');
  });

  it('should show empty results message', async () => {
    mockSearchCql.mockResolvedValueOnce({ results: [], size: 0, totalSize: 0 });

    const result = await searchConfluenceCqlTool.handler({ cql: 'space = "NONEXISTENT"' });
    expect(result).toContain('No content found matching your CQL query');
  });

  it('should show pagination when size < totalSize', async () => {
    mockSearchCql.mockResolvedValueOnce({
      results: [{ title: 'P', id: '1', type: 'page', status: 'current' }],
      size: 10,
      totalSize: 50,
    });

    const result = await searchConfluenceCqlTool.handler({ cql: 'type = page', start: 0 });
    expect(result).toContain('Showing 10 of 50 total results');
    expect(result).toContain('next start: 10');
  });

  it('should return error on failure', async () => {
    mockSearchCql.mockRejectedValueOnce(new Error('Invalid CQL'));

    const result = await searchConfluenceCqlTool.handler({ cql: 'bad query' });
    expect(result).toContain('Error searching Confluence with CQL');
    expect(result).toContain('Invalid CQL');
  });
});
