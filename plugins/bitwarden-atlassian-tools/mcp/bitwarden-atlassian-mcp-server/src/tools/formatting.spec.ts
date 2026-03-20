import { describe, it, expect, vi, beforeEach } from 'vitest';

/**
 * Tests for formatting functions via tool handlers.
 *
 * The format functions are private to each tool file. We test them through
 * the tool handlers by mocking JiraClient with a shared instance so mock
 * return values configured in tests are visible to the handlers.
 */

const mockGetIssue = vi.fn();
const mockGetIssueComments = vi.fn();
const mockSearchIssues = vi.fn();
const mockListProjects = vi.fn();

vi.mock('../jira/client.js', () => {
  return {
    JiraClient: vi.fn().mockImplementation(() => ({
      getIssue: mockGetIssue,
      getIssueComments: mockGetIssueComments,
      searchIssues: mockSearchIssues,
      listProjects: mockListProjects,
    })),
  };
});

import getIssueTool from './get-issue.js';
import getIssueCommentsTool from './get-issue-comments.js';
import searchIssuesTool from './search-issues.js';

beforeEach(() => {
  vi.clearAllMocks();
});

describe('get_issue formatting', () => {
  it('should format basic issue details', async () => {
    const mockIssue = {
      key: 'TEST-1',
      fields: {
        summary: 'Test issue',
        issuetype: { name: 'Bug' },
        status: { name: 'Open', statusCategory: { name: 'To Do' } },
        priority: { name: 'High' },
        project: { name: 'Test Project', key: 'TEST' },
        reporter: { displayName: 'Jane Doe', emailAddress: 'jane@example.com' },
        assignee: { displayName: 'John Smith', emailAddress: 'john@example.com' },
        created: '2026-01-01T00:00:00.000Z',
        updated: '2026-01-02T00:00:00.000Z',
      },
    };

    mockGetIssue.mockResolvedValueOnce(mockIssue);

    const result = await getIssueTool.handler({ issueIdOrKey: 'TEST-1' });

    expect(result).toContain('# TEST-1: Test issue');
    expect(result).toContain('**Type:** Bug');
    expect(result).toContain('**Status:** Open (To Do)');
    expect(result).toContain('**Priority:** High');
    expect(result).toContain('Jane Doe');
    expect(result).toContain('John Smith');
  });

  it('should handle issue with labels', async () => {
    const mockIssue = {
      key: 'TEST-2',
      fields: {
        summary: 'Labeled issue',
        priority: { name: 'Low' },
        labels: ['frontend', 'bug'],
      },
    };

    mockGetIssue.mockResolvedValueOnce(mockIssue);

    const result = await getIssueTool.handler({ issueIdOrKey: 'TEST-2' });

    expect(result).toContain('## Labels');
    expect(result).toContain('frontend');
    expect(result).toContain('bug');
  });

  it('should handle issue with ADF description', async () => {
    const mockIssue = {
      key: 'TEST-3',
      fields: {
        summary: 'Described issue',
        priority: { name: 'Medium' },
        description: {
          type: 'doc',
          content: [
            {
              type: 'paragraph',
              content: [{ type: 'text', text: 'This is the description' }],
            },
          ],
        },
      },
    };

    mockGetIssue.mockResolvedValueOnce(mockIssue);

    const result = await getIssueTool.handler({ issueIdOrKey: 'TEST-3' });

    expect(result).toContain('## Description');
    expect(result).toContain('This is the description');
  });

  it('should render ADF custom fields with display names', async () => {
    const mockIssue = {
      key: 'TEST-10',
      names: {
        customfield_10085: 'Replication Steps',
      },
      fields: {
        summary: 'Bug with custom fields',
        priority: { name: 'High' },
        customfield_10085: {
          type: 'doc',
          content: [
            {
              type: 'paragraph',
              content: [{ type: 'text', text: '1. Open app\n2. Click button\n3. See error' }],
            },
          ],
        },
      },
    };

    mockGetIssue.mockResolvedValueOnce(mockIssue);

    const result = await getIssueTool.handler({ issueIdOrKey: 'TEST-10' });

    expect(result).toContain('## Additional Fields');
    expect(result).toContain('### Replication Steps');
    expect(result).toContain('1. Open app');
  });

  it('should render simple string custom fields', async () => {
    const mockIssue = {
      key: 'TEST-11',
      names: {
        customfield_10086: 'Recommended Solution',
      },
      fields: {
        summary: 'Issue with string custom field',
        priority: { name: 'Medium' },
        customfield_10086: 'Upgrade the dependency to v2',
      },
    };

    mockGetIssue.mockResolvedValueOnce(mockIssue);

    const result = await getIssueTool.handler({ issueIdOrKey: 'TEST-11' });

    expect(result).toContain('### Recommended Solution');
    expect(result).toContain('Upgrade the dependency to v2');
  });

  it('should render select-type custom fields', async () => {
    const mockIssue = {
      key: 'TEST-12',
      names: {
        customfield_10087: 'Severity',
      },
      fields: {
        summary: 'Issue with select field',
        priority: { name: 'Low' },
        customfield_10087: { name: 'Critical' },
      },
    };

    mockGetIssue.mockResolvedValueOnce(mockIssue);

    const result = await getIssueTool.handler({ issueIdOrKey: 'TEST-12' });

    expect(result).toContain('### Severity');
    expect(result).toContain('Critical');
  });

  it('should skip null/empty custom fields', async () => {
    const mockIssue = {
      key: 'TEST-13',
      fields: {
        summary: 'Issue with empty custom fields',
        priority: { name: 'Low' },
        customfield_10085: null,
        customfield_10086: '',
      },
    };

    mockGetIssue.mockResolvedValueOnce(mockIssue);

    const result = await getIssueTool.handler({ issueIdOrKey: 'TEST-13' });

    expect(result).not.toContain('## Additional Fields');
  });

  it('should skip low-value fields like Rank and Development', async () => {
    const mockIssue = {
      key: 'TEST-15',
      names: {
        customfield_10100: 'Rank',
        customfield_10101: 'Development',
        customfield_10102: 'Bug category',
      },
      fields: {
        summary: 'Issue with noisy fields',
        priority: { name: 'Medium' },
        customfield_10100: '1|hzvg5q:uo9tqj6002tqzzw7hey4b',
        customfield_10101: { storyPoints: 5 },
        customfield_10102: { name: 'Broken basic behavior' },
      },
    };

    mockGetIssue.mockResolvedValueOnce(mockIssue);

    const result = await getIssueTool.handler({ issueIdOrKey: 'TEST-15' });

    expect(result).not.toContain('### Rank');
    expect(result).not.toContain('### Development');
    expect(result).toContain('### Bug category');
    expect(result).toContain('Broken basic behavior');
  });

  it('should fall back to raw field key when names not provided', async () => {
    const mockIssue = {
      key: 'TEST-14',
      fields: {
        summary: 'Issue without names map',
        priority: { name: 'Medium' },
        customfield_99999: 'Some value',
      },
    };

    mockGetIssue.mockResolvedValueOnce(mockIssue);

    const result = await getIssueTool.handler({ issueIdOrKey: 'TEST-14' });

    expect(result).toContain('### customfield_99999');
    expect(result).toContain('Some value');
  });

  it('should return error message on client failure', async () => {
    mockGetIssue.mockRejectedValueOnce(new Error('Not found'));

    const result = await getIssueTool.handler({ issueIdOrKey: 'TEST-999' });

    expect(result).toContain('Error retrieving issue');
    expect(result).toContain('Not found');
  });
});

describe('get_issue_comments formatting', () => {
  it('should format comments with pagination info', async () => {
    const mockComments = {
      total: 2,
      startAt: 0,
      comments: [
        {
          author: { displayName: 'Alice' },
          created: '2026-01-01T00:00:00.000Z',
          updated: '2026-01-01T00:00:00.000Z',
          body: {
            type: 'doc',
            content: [
              {
                type: 'paragraph',
                content: [{ type: 'text', text: 'First comment' }],
              },
            ],
          },
        },
        {
          author: { displayName: 'Bob' },
          created: '2026-01-02T00:00:00.000Z',
          updated: '2026-01-02T00:00:00.000Z',
          body: {
            type: 'doc',
            content: [
              {
                type: 'paragraph',
                content: [{ type: 'text', text: 'Second comment' }],
              },
            ],
          },
        },
      ],
    };

    mockGetIssueComments.mockResolvedValueOnce(mockComments);

    const result = await getIssueCommentsTool.handler({ issueIdOrKey: 'TEST-1' });

    expect(result).toContain('Comments for TEST-1');
    expect(result).toContain('Total Comments:** 2');
    expect(result).toContain('Alice');
    expect(result).toContain('First comment');
    expect(result).toContain('Bob');
    expect(result).toContain('Second comment');
  });

  it('should handle empty comments', async () => {
    const mockComments = {
      total: 0,
      startAt: 0,
      comments: [],
    };

    mockGetIssueComments.mockResolvedValueOnce(mockComments);

    const result = await getIssueCommentsTool.handler({ issueIdOrKey: 'TEST-1' });

    expect(result).toContain('No comments found');
  });

  it('should show pagination note when more comments available', async () => {
    const mockComments = {
      total: 10,
      startAt: 0,
      comments: [
        {
          author: { displayName: 'Alice' },
          created: '2026-01-01T00:00:00.000Z',
          updated: '2026-01-01T00:00:00.000Z',
          body: {
            type: 'doc',
            content: [
              {
                type: 'paragraph',
                content: [{ type: 'text', text: 'A comment' }],
              },
            ],
          },
        },
      ],
    };

    mockGetIssueComments.mockResolvedValueOnce(mockComments);

    const result = await getIssueCommentsTool.handler({ issueIdOrKey: 'TEST-1' });

    expect(result).toContain('9 more comments available');
  });
});

describe('search_issues formatting', () => {
  it('should format search results', async () => {
    const mockResults = {
      total: 1,
      issues: [
        {
          key: 'TEST-1',
          fields: {
            summary: 'Found issue',
            status: { name: 'Open' },
            issuetype: { name: 'Task' },
            priority: { name: 'Medium' },
            assignee: { displayName: 'John' },
            reporter: { displayName: 'Jane' },
            labels: ['label1'],
          },
        },
      ],
    };

    mockSearchIssues.mockResolvedValueOnce(mockResults);

    const result = await searchIssuesTool.handler({ jql: 'project = TEST' });

    expect(result).toContain('JIRA Search Results');
    expect(result).toContain('TEST-1');
    expect(result).toContain('Found issue');
    expect(result).toContain('project = TEST');
  });

  it('should return message for empty results', async () => {
    const mockResults = { total: 0, issues: [] };

    mockSearchIssues.mockResolvedValueOnce(mockResults);

    const result = await searchIssuesTool.handler({ jql: 'project = NONE' });

    expect(result).toContain('No issues found');
  });

  it('should show pagination note with nextPageToken', async () => {
    const mockResults = {
      total: 100,
      nextPageToken: 'next-page-token-123',
      issues: [
        {
          key: 'TEST-1',
          fields: {
            summary: 'Issue',
            status: { name: 'Open' },
            issuetype: { name: 'Task' },
            priority: { name: 'Medium' },
            labels: [],
          },
        },
      ],
    };

    mockSearchIssues.mockResolvedValueOnce(mockResults);

    const result = await searchIssuesTool.handler({ jql: 'project = TEST' });

    expect(result).toContain('nextPageToken');
    expect(result).toContain('next-page-token-123');
  });
});
