import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

/**
 * Tests for JiraClient.downloadAttachment origin validation.
 *
 * The constructor calls loadJiraConfig() which requires env vars,
 * so we mock the auth module to avoid that dependency.
 */

// Mock axios before importing the client
vi.mock('axios', () => {
  const mockAxios: any = {
    create: vi.fn(() => ({
      get: vi.fn(),
      interceptors: {
        response: { use: vi.fn() },
      },
    })),
    get: vi.fn(),
  };
  return { default: mockAxios };
});

vi.mock('./auth.js', () => ({
  loadJiraConfig: () => ({
    url: 'https://company.atlassian.net',
    email: 'user@example.com',
    apiToken: 'test-token',
  }),
  getJiraHeaders: () => ({
    Authorization: 'Basic dGVzdA==',
    Accept: 'application/json',
    'Content-Type': 'application/json',
  }),
}));

import axios from 'axios';
import { JiraClient } from './client.js';

describe('JiraClient.downloadAttachment', () => {
  let client: JiraClient;

  beforeEach(() => {
    client = new JiraClient();
    vi.clearAllMocks();
  });

  it('should allow same-origin attachment URL', async () => {
    const mockGet = vi.mocked(axios.get);
    mockGet.mockResolvedValueOnce({ data: Buffer.from('file-content') });

    const result = await client.downloadAttachment(
      'https://company.atlassian.net/rest/api/3/attachment/content/12345'
    );
    expect(result).toBeInstanceOf(Buffer);
    expect(mockGet).toHaveBeenCalledOnce();
  });

  it('should reject different origin URL', async () => {
    await expect(
      client.downloadAttachment('https://evil.com/rest/api/3/attachment/content/12345')
    ).rejects.toThrow('Attachment URL does not belong to the configured Jira instance');
  });

  it('should reject sibling domain attack', async () => {
    await expect(
      client.downloadAttachment(
        'https://company.atlassian.net.evil.com/rest/api/3/attachment/content/12345'
      )
    ).rejects.toThrow('Attachment URL does not belong to the configured Jira instance');
  });

  it('should reject URL with different port', async () => {
    await expect(
      client.downloadAttachment(
        'https://company.atlassian.net:8443/rest/api/3/attachment/content/12345'
      )
    ).rejects.toThrow('Attachment URL does not belong to the configured Jira instance');
  });

  it('should throw TypeError for invalid URL', async () => {
    await expect(
      client.downloadAttachment('not-a-url')
    ).rejects.toThrow();
  });
});
