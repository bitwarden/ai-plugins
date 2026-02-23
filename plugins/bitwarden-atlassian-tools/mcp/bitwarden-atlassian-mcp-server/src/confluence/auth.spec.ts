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

  it('should return config when all Confluence env vars are set', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://company.atlassian.net/wiki';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'confluence-token';

    const config = loadConfluenceConfig();
    expect(config.url).toBe('https://company.atlassian.net/wiki');
    expect(config.email).toBe('user@example.com');
    expect(config.apiToken).toBe('confluence-token');
  });

  it('should fall back to ATLASSIAN_JIRA_URL when Confluence URL not set', () => {
    delete process.env.ATLASSIAN_CONFLUENCE_URL;
    process.env.ATLASSIAN_JIRA_URL = 'https://company.atlassian.net';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'confluence-token';

    const config = loadConfluenceConfig();
    expect(config.url).toBe('https://company.atlassian.net');
  });

  it('should fall back to ATLASSIAN_JIRA_READ_ONLY_TOKEN when Confluence token not set', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://company.atlassian.net/wiki';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    delete process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN;
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = 'jira-token';

    const config = loadConfluenceConfig();
    expect(config.apiToken).toBe('jira-token');
  });

  it('should prefer Confluence URL over Jira URL when both set', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://confluence.example.com';
    process.env.ATLASSIAN_JIRA_URL = 'https://jira.example.com';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    const config = loadConfluenceConfig();
    expect(config.url).toBe('https://confluence.example.com');
  });

  it('should prefer Confluence token over Jira token when both set', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://company.atlassian.net/wiki';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'confluence-token';
    process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN = 'jira-token';

    const config = loadConfluenceConfig();
    expect(config.apiToken).toBe('confluence-token');
  });

  it('should normalize trailing slash from URL', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://company.atlassian.net/wiki/';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    const config = loadConfluenceConfig();
    expect(config.url).toBe('https://company.atlassian.net/wiki');
  });

  it('should throw when URL is missing (both variants)', () => {
    delete process.env.ATLASSIAN_CONFLUENCE_URL;
    delete process.env.ATLASSIAN_JIRA_URL;
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });

  it('should throw when ATLASSIAN_EMAIL is missing', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://company.atlassian.net/wiki';
    delete process.env.ATLASSIAN_EMAIL;
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });

  it('should throw when token is missing (both variants)', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = 'https://company.atlassian.net/wiki';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    delete process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN;
    delete process.env.ATLASSIAN_JIRA_READ_ONLY_TOKEN;

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });

  it('should treat unexpanded ${VAR} template as undefined', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = '${ATLASSIAN_CONFLUENCE_URL}';
    delete process.env.ATLASSIAN_JIRA_URL;
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });

  it('should fall back to Jira URL when Confluence URL is unexpanded template', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = '${ATLASSIAN_CONFLUENCE_URL}';
    process.env.ATLASSIAN_JIRA_URL = 'https://company.atlassian.net';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    const config = loadConfluenceConfig();
    expect(config.url).toBe('https://company.atlassian.net');
  });

  it('should treat empty string as missing', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = '';
    delete process.env.ATLASSIAN_JIRA_URL;
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    expect(() => loadConfluenceConfig()).toThrow(/Missing required Confluence environment variables/);
  });

  it('should fall back to Jira URL when Confluence URL is empty', () => {
    process.env.ATLASSIAN_CONFLUENCE_URL = '';
    process.env.ATLASSIAN_JIRA_URL = 'https://company.atlassian.net';
    process.env.ATLASSIAN_EMAIL = 'user@example.com';
    process.env.ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN = 'token';

    const config = loadConfluenceConfig();
    expect(config.url).toBe('https://company.atlassian.net');
  });
});

describe('getAuthHeader', () => {
  it('should produce correct Basic auth header', () => {
    const config = {
      url: 'https://company.atlassian.net/wiki',
      email: 'user@example.com',
      apiToken: 'my-token',
    };

    const header = getAuthHeader(config);
    const expected = `Basic ${Buffer.from('user@example.com:my-token').toString('base64')}`;
    expect(header).toBe(expected);
  });

  it('should start with "Basic "', () => {
    const config = {
      url: 'https://company.atlassian.net/wiki',
      email: 'a@b.com',
      apiToken: 'tok',
    };

    expect(getAuthHeader(config)).toMatch(/^Basic /);
  });
});

describe('getConfluenceHeaders', () => {
  it('should return correct header shape', () => {
    const config = {
      url: 'https://company.atlassian.net/wiki',
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
      url: 'https://company.atlassian.net/wiki',
      email: 'user@example.com',
      apiToken: 'test-token',
    };

    const headers = getConfluenceHeaders(config);
    expect(headers.Authorization).toBe(getAuthHeader(config));
  });
});
