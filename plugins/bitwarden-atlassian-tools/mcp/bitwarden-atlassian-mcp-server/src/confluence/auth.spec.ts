import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { loadConfluenceConfig, getAuthHeader, getConfluenceHeaders } from './auth.js';

describe('loadConfluenceConfig', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('should return config when all env vars are set', () => {
    process.env.ATLASSIAN_CLOUD_ID = 'test-cloud-id-123';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'confluence-token';

    const config = loadConfluenceConfig();
    expect(config.cloudId).toBe('test-cloud-id-123');
    expect(config.gatewayBaseUrl).toBe('https://api.atlassian.com/ex/confluence/test-cloud-id-123');
    expect(config.email).toBe('user@example.com');
    expect(config.apiToken).toBe('confluence-token');
  });

  it('should construct gateway URL from cloud ID', () => {
    process.env.ATLASSIAN_CLOUD_ID = 'ed2a1282-a287-4f97-a32f-b9136165c8ed';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    const config = loadConfluenceConfig();
    expect(config.gatewayBaseUrl).toBe(
      'https://api.atlassian.com/ex/confluence/ed2a1282-a287-4f97-a32f-b9136165c8ed'
    );
  });

  it('should throw when ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN is missing even if Jira token is set', () => {
    process.env.ATLASSIAN_CLOUD_ID = 'test-cloud-id';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    delete process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN;
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = 'jira-token';

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });

  it('should use ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN', () => {
    process.env.ATLASSIAN_CLOUD_ID = 'test-cloud-id';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'confluence-token';
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = 'jira-token';

    const config = loadConfluenceConfig();
    expect(config.apiToken).toBe('confluence-token');
  });

  it('should throw when ATLASSIAN_CLOUD_ID is missing', () => {
    delete process.env.ATLASSIAN_CLOUD_ID;
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });

  it('should throw when ATLASSIAN_EMAIL is missing', () => {
    process.env.ATLASSIAN_CLOUD_ID = 'test-cloud-id';
    delete process.env.ATLASSIAN_EMAIL;
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });

  it('should throw when ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN is missing', () => {
    process.env.ATLASSIAN_CLOUD_ID = 'test-cloud-id';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    delete process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN;

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });

  it('should treat unexpanded ${VAR} template as undefined', () => {
    process.env.ATLASSIAN_CLOUD_ID = '${ATLASSIAN_CLOUD_ID}';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });

  it('should treat empty string as missing', () => {
    process.env.ATLASSIAN_CLOUD_ID = '';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });
});

describe('getAuthHeader', () => {
  it('should produce correct Basic auth header', () => {
    const config = {
      cloudId: 'test-cloud-id',
      gatewayBaseUrl: 'https://api.atlassian.com/ex/confluence/test-cloud-id',
      email: 'user@example.com',
      apiToken: 'my-token',
    };

    const header = getAuthHeader(config);
    const expected = `Basic ${Buffer.from('user@example.com:my-token').toString('base64')}`;
    expect(header).toBe(expected);
  });

  it('should start with "Basic "', () => {
    const config = {
      cloudId: 'test-cloud-id',
      gatewayBaseUrl: 'https://api.atlassian.com/ex/confluence/test-cloud-id',
      email: 'a@b.com',
      apiToken: 'tok',
    };

    expect(getAuthHeader(config)).toMatch(/^Basic /);
  });
});

describe('getConfluenceHeaders', () => {
  it('should return correct header shape', () => {
    const config = {
      cloudId: 'test-cloud-id',
      gatewayBaseUrl: 'https://api.atlassian.com/ex/confluence/test-cloud-id',
      email: 'user@example.com',
      apiToken: 'test-token',
    };

    const headers = getConfluenceHeaders(config);
    expect(headers).toHaveProperty('Authorization');
    expect(headers).toHaveProperty('Accept', 'application/json');
    expect(headers).toHaveProperty('Content-Type', 'application/json');
  });

  it('should match Authorization header with getAuthHeader', () => {
    const config = {
      cloudId: 'test-cloud-id',
      gatewayBaseUrl: 'https://api.atlassian.com/ex/confluence/test-cloud-id',
      email: 'user@example.com',
      apiToken: 'test-token',
    };

    const headers = getConfluenceHeaders(config);
    expect(headers.Authorization).toBe(getAuthHeader(config));
  });
});
