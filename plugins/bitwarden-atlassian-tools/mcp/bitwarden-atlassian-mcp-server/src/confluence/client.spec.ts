import { describe, it, expect, vi, beforeEach } from 'vitest';

/**
 * Tests for ConfluenceClient error handling.
 *
 * We extract the error interceptor registered during construction
 * and exercise handleError indirectly.
 */

const mockAxiosInstance: any = {
  get: vi.fn(),
  interceptors: {
    response: { use: vi.fn() },
  },
};

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance),
  },
}));

vi.mock('./auth.js', () => ({
  loadConfluenceConfig: () => ({
    url: 'https://company.atlassian.net',
    email: 'user@example.com',
    apiToken: 'test-token',
  }),
  getConfluenceHeaders: () => ({
    Authorization: 'Basic dGVzdA==',
    Accept: 'application/json',
    'Content-Type': 'application/json',
  }),
}));

import { ConfluenceClient } from './client.js';

describe('ConfluenceClient error handling', () => {
  let handleError: (error: any) => any;

  beforeEach(() => {
    vi.clearAllMocks();
    new ConfluenceClient();
    // Extract the rejection handler registered on interceptors.response.use
    const calls = mockAxiosInstance.interceptors.response.use.mock.calls;
    const errorHandler = calls[calls.length - 1][1];
    // handleError returns Promise.reject(err), so we unwrap
    handleError = async (error: any) => {
      try {
        await errorHandler(error);
      } catch (e) {
        return e;
      }
    };
  });

  it('should map 401 to authentication failed', async () => {
    const err = await handleError({ response: { status: 401, data: {} }, config: {} });
    expect(err.message).toContain('authentication failed');
  });

  it('should map 403 to access forbidden', async () => {
    const err = await handleError({ response: { status: 403, data: {} }, config: {} });
    expect(err.message).toContain('access forbidden');
  });

  it('should map 404 to resource not found with URL', async () => {
    const err = await handleError({
      response: { status: 404, data: {} },
      config: { url: '/wiki/api/v2/pages/123' },
    });
    expect(err.message).toContain('resource not found');
    expect(err.message).toContain('/wiki/api/v2/pages/123');
  });

  it('should map 429 to rate limit', async () => {
    const err = await handleError({ response: { status: 429, data: {} }, config: {} });
    expect(err.message).toContain('rate limit');
  });

  it('should map 500 with data.message', async () => {
    const err = await handleError({
      response: { status: 500, data: { message: 'Internal failure' } },
      config: {},
      message: 'Request failed',
    });
    expect(err.message).toContain('API error (500)');
    expect(err.message).toContain('Internal failure');
  });

  it('should map 500 without data.message to error.message', async () => {
    const err = await handleError({
      response: { status: 500, data: {} },
      config: {},
      message: 'Request failed with status 500',
    });
    expect(err.message).toContain('API error (500)');
    expect(err.message).toContain('Request failed with status 500');
  });

  it('should handle no response with request present', async () => {
    const err = await handleError({
      request: {},
      message: 'Network Error',
      config: {},
    });
    expect(err.message).toContain('request failed');
    expect(err.message).toContain('ATLASSIAN_CONFLUENCE_URL');
  });

  it('should handle no response and no request', async () => {
    const err = await handleError({
      message: 'Something went wrong',
      config: {},
    });
    expect(err.message).toContain('client error');
  });
});
