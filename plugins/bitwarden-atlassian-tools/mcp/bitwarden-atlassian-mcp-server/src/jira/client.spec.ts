import { describe, it, expect, vi, beforeEach } from 'vitest';

/**
 * Tests for JiraClient.downloadAttachment hostname validation and gateway routing.
 *
 * The constructor calls loadJiraConfig() which requires env vars,
 * so we mock the auth module to avoid that dependency.
 */

const mockInstanceGet = vi.fn();

// Mock axios before importing the client
vi.mock('axios', () => {
  const mockAxios: any = {
    create: vi.fn(() => ({
      get: mockInstanceGet,
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
    cloudId: 'test-cloud-id',
    gatewayBaseUrl: 'https://api.atlassian.com/ex/jira/test-cloud-id',
    email: 'user@example.com',
    apiToken: 'test-token',
  }),
  getJiraHeaders: () => ({
    Authorization: 'Basic dGVzdA==',
    Accept: 'application/json',
    'Content-Type': 'application/json',
  }),
}));

import { JiraClient } from './client.js';

describe('JiraClient.downloadAttachment', () => {
  let client: JiraClient;

  beforeEach(() => {
    client = new JiraClient();
    vi.clearAllMocks();
  });

  it('should route *.atlassian.net attachment URL through the API gateway', async () => {
    mockInstanceGet.mockResolvedValueOnce({ data: Buffer.from('file-content') });

    const result = await client.downloadAttachment(
      'https://company.atlassian.net/rest/api/3/attachment/content/12345'
    );
    expect(result).toBeInstanceOf(Buffer);
    expect(mockInstanceGet).toHaveBeenCalledOnce();
    expect(mockInstanceGet).toHaveBeenCalledWith(
      'https://api.atlassian.com/ex/jira/test-cloud-id/rest/api/3/attachment/content/12345',
      expect.objectContaining({ responseType: 'arraybuffer' })
    );
  });

  it('should preserve query parameters when rewriting to gateway URL', async () => {
    mockInstanceGet.mockResolvedValueOnce({ data: Buffer.from('file-content') });

    await client.downloadAttachment(
      'https://company.atlassian.net/rest/api/3/attachment/content/12345?redirect=false'
    );
    expect(mockInstanceGet).toHaveBeenCalledWith(
      'https://api.atlassian.com/ex/jira/test-cloud-id/rest/api/3/attachment/content/12345?redirect=false',
      expect.anything()
    );
  });

  it('should allow any *.atlassian.net subdomain', async () => {
    mockInstanceGet.mockResolvedValueOnce({ data: Buffer.from('file-content') });

    const result = await client.downloadAttachment(
      'https://other-company.atlassian.net/rest/api/3/attachment/content/12345'
    );
    expect(result).toBeInstanceOf(Buffer);
    expect(mockInstanceGet).toHaveBeenCalledOnce();
  });

  it('should reject non-atlassian.net domain', async () => {
    await expect(
      client.downloadAttachment('https://evil.com/rest/api/3/attachment/content/12345')
    ).rejects.toThrow('Attachment URL must be an *.atlassian.net hostname');
  });

  it('should reject sibling domain attack', async () => {
    await expect(
      client.downloadAttachment(
        'https://company.atlassian.net.evil.com/rest/api/3/attachment/content/12345'
      )
    ).rejects.toThrow('Attachment URL must be an *.atlassian.net hostname');
  });

  it('should reject bare atlassian.net without subdomain', async () => {
    await expect(
      client.downloadAttachment(
        'https://atlassian.net/rest/api/3/attachment/content/12345'
      )
    ).rejects.toThrow('Attachment URL must be an *.atlassian.net hostname');
  });

  it('should throw TypeError for invalid URL', async () => {
    await expect(
      client.downloadAttachment('not-a-url')
    ).rejects.toThrow();
  });
});