import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { loadJiraConfig, getAuthHeader, getJiraHeaders } from './auth.js';

describe('loadJiraConfig', () => {
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
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = 'test-token';

    const config = loadJiraConfig();
    expect(config.cloudId).toBe('test-cloud-id-123');
    expect(config.gatewayBaseUrl).toBe('https://api.atlassian.com/ex/jira/test-cloud-id-123');
    expect(config.email).toBe('user@example.com');
    expect(config.apiToken).toBe('test-token');
  });

  it('should construct gateway URL from cloud ID', () => {
    process.env.ATLASSIAN_CLOUD_ID = 'ed2a1282-a287-4f97-a32f-b9136165c8ed';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = 'test-token';

    const config = loadJiraConfig();
    expect(config.gatewayBaseUrl).toBe(
      'https://api.atlassian.com/ex/jira/ed2a1282-a287-4f97-a32f-b9136165c8ed'
    );
  });

  it('should throw when ATLASSIAN_CLOUD_ID is missing', () => {
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = 'test-token';
    delete process.env.ATLASSIAN_CLOUD_ID;

    expect(() => loadJiraConfig()).toThrow(/Missing required JIRA environment variables/);
  });

  it('should throw when ATLASSIAN_EMAIL is missing', () => {
    process.env.ATLASSIAN_CLOUD_ID = 'test-cloud-id';
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = 'test-token';
    delete process.env.ATLASSIAN_EMAIL;

    expect(() => loadJiraConfig()).toThrow(/Missing required JIRA environment variables/);
  });

  it('should throw when ATLASSIAN_JIRA_READ_ONLY_TOKEN is missing', () => {
    process.env.ATLASSIAN_CLOUD_ID = 'test-cloud-id';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    delete process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN;

    expect(() => loadJiraConfig()).toThrow(/Missing required JIRA environment variables/);
  });

  it('should treat unexpanded ${VAR} template as undefined', () => {
    process.env.ATLASSIAN_CLOUD_ID = '${ATLASSIAN_CLOUD_ID}';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = 'test-token';

    expect(() => loadJiraConfig()).toThrow(/Missing required JIRA environment variables/);
  });

  it('should treat empty string as missing', () => {
    process.env.ATLASSIAN_CLOUD_ID = '';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = 'test-token';

    expect(() => loadJiraConfig()).toThrow(/Missing required JIRA environment variables/);
  });
});

describe('getAuthHeader', () => {
  it('should produce correct Basic auth header', () => {
    const config = {
      cloudId: 'test-cloud-id',
      gatewayBaseUrl: 'https://api.atlassian.com/ex/jira/test-cloud-id',
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
      gatewayBaseUrl: 'https://api.atlassian.com/ex/jira/test-cloud-id',
      email: 'a@b.com',
      apiToken: 'tok',
    };

    expect(getAuthHeader(config)).toMatch(/^Basic /);
  });
});

describe('getJiraHeaders', () => {
  it('should return correct header shape', () => {
    const config = {
      cloudId: 'test-cloud-id',
      gatewayBaseUrl: 'https://api.atlassian.com/ex/jira/test-cloud-id',
      email: 'user@example.com',
      apiToken: 'test-token',
    };

    const headers = getJiraHeaders(config);
    expect(headers).toHaveProperty('Authorization');
    expect(headers).toHaveProperty('Accept', 'application/json');
    expect(headers).toHaveProperty('Content-Type', 'application/json');
  });

  it('should match Authorization header with getAuthHeader', () => {
    const config = {
      cloudId: 'test-cloud-id',
      gatewayBaseUrl: 'https://api.atlassian.com/ex/jira/test-cloud-id',
      email: 'user@example.com',
      apiToken: 'test-token',
    };

    const headers = getJiraHeaders(config);
    expect(headers.Authorization).toBe(getAuthHeader(config));
  });
});
