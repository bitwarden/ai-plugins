/**
 * Confluence REST API Client
 * Provides typed methods for interacting with Confluence Cloud API v2
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { loadConfluenceConfig, getConfluenceHeaders } from './auth.js';
import {
  ConfluenceConfig,
  ConfluencePage,
  ConfluenceSearchResult,
  ConfluenceGetPageParams,
  ConfluenceSearchParams,
  ConfluenceComment,
  ConfluenceCommentsResult,
  ConfluenceGetCommentsParams,
  ConfluenceGetCommentRepliesParams,
  ConfluenceSpacesResult,
  ConfluenceChildPagesResult,
  ConfluenceCqlSearchParams,
  ConfluenceCqlSearchResult,
} from './types.js';

export class ConfluenceClient {
  private config: ConfluenceConfig;
  private client: AxiosInstance;
  private readonly API_BASE = '/wiki/api/v2';
  private readonly API_V1_BASE = '/wiki/rest/api';

  constructor() {
    this.config = loadConfluenceConfig();
    this.client = axios.create({
      baseURL: this.config.gatewayBaseUrl,
      headers: getConfluenceHeaders(this.config),
      timeout: 30000, // 30 second timeout
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        return Promise.reject(this.handleError(error));
      }
    );
  }

  /**
   * Handle and format Confluence API errors
   */
  private handleError(error: AxiosError): Error {
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as any;

      switch (status) {
        case 401:
          return new Error('Confluence authentication failed. Check your API token and email.');
        case 403:
          return new Error('Confluence access forbidden. Check your permissions.');
        case 404:
          return new Error(`Confluence resource not found: ${error.config?.url}`);
        case 429:
          return new Error('Confluence API rate limit exceeded. Please try again later.');
        default:
          return new Error(
            `Confluence API error (${status}): ${data?.message || error.message}`
          );
      }
    }

    if (error.request) {
      return new Error(`Confluence API request failed: ${error.message}. Check your ATLASSIAN_CLOUD_ID.`);
    }

    return new Error(`Confluence client error: ${error.message}`);
  }

  /**
   * Get a single page by ID
   */
  async getPage(params: ConfluenceGetPageParams): Promise<ConfluencePage> {
    const queryParams: Record<string, any> = {};

    if (params.includeBody !== false) {
      const format = params.bodyFormat || 'storage';
      queryParams['body-format'] = format;
    }

    const response = await this.client.get<ConfluencePage>(
      `${this.API_BASE}/pages/${params.pageId}`,
      { params: queryParams }
    );

    return response.data;
  }

  /**
   * Search for pages in Confluence
   */
  async searchPages(params: ConfluenceSearchParams): Promise<ConfluenceSearchResult> {
    const queryParams: Record<string, any> = {
      limit: Math.min(params.limit || 25, 250),
    };

    if (params.spaceKey) {
      queryParams['space-key'] = params.spaceKey;
    }

    if (params.title) {
      queryParams.title = params.title;
    }

    if (params.cursor) {
      queryParams.cursor = params.cursor;
    }

    const response = await this.client.get<ConfluenceSearchResult>(
      `${this.API_BASE}/pages`,
      { params: queryParams }
    );

    return response.data;
  }

  /**
   * Get page by ID with full content (convenience method)
   */
  async getPageWithContent(pageId: string): Promise<ConfluencePage> {
    return this.getPage({
      pageId,
      includeBody: true,
      bodyFormat: 'storage',
    });
  }

  /**
   * Test connection and authentication
   */
  async testConnection(): Promise<boolean> {
    await this.searchPages({ limit: 1 });
    return true;
  }

  /**
   * Get footer comments for a page
   */
  async getPageComments(params: ConfluenceGetCommentsParams): Promise<ConfluenceCommentsResult> {
    const queryParams: Record<string, any> = {
      limit: Math.min(params.limit || 25, 100),
    };

    if (params.bodyFormat) {
      queryParams['body-format'] = params.bodyFormat;
    }

    if (params.cursor) {
      queryParams.cursor = params.cursor;
    }

    const response = await this.client.get<ConfluenceCommentsResult>(
      `${this.API_BASE}/pages/${params.pageId}/footer-comments`,
      { params: queryParams }
    );

    return response.data;
  }

  /**
   * Get replies to a specific comment
   */
  async getCommentReplies(params: ConfluenceGetCommentRepliesParams): Promise<ConfluenceCommentsResult> {
    const queryParams: Record<string, any> = {
      limit: Math.min(params.limit || 25, 100),
    };

    if (params.bodyFormat) {
      queryParams['body-format'] = params.bodyFormat;
    }

    if (params.cursor) {
      queryParams.cursor = params.cursor;
    }

    const response = await this.client.get<ConfluenceCommentsResult>(
      `${this.API_BASE}/footer-comments/${params.commentId}/children`,
      { params: queryParams }
    );

    return response.data;
  }

  /**
   * Get inline comments for a page
   */
  async getPageInlineComments(params: ConfluenceGetCommentsParams): Promise<ConfluenceCommentsResult> {
    const queryParams: Record<string, any> = {
      limit: Math.min(params.limit || 25, 100),
    };

    if (params.bodyFormat) {
      queryParams['body-format'] = params.bodyFormat;
    }

    if (params.cursor) {
      queryParams.cursor = params.cursor;
    }

    const response = await this.client.get<ConfluenceCommentsResult>(
      `${this.API_BASE}/pages/${params.pageId}/inline-comments`,
      { params: queryParams }
    );

    return response.data;
  }

  /**
   * Get replies to an inline comment
   */
  async getInlineCommentReplies(params: ConfluenceGetCommentRepliesParams): Promise<ConfluenceCommentsResult> {
    const queryParams: Record<string, any> = {
      limit: Math.min(params.limit || 25, 100),
    };

    if (params.bodyFormat) {
      queryParams['body-format'] = params.bodyFormat;
    }

    if (params.cursor) {
      queryParams.cursor = params.cursor;
    }

    const response = await this.client.get<ConfluenceCommentsResult>(
      `${this.API_BASE}/inline-comments/${params.commentId}/children`,
      { params: queryParams }
    );

    return response.data;
  }

  // ── New Confluence v2 Methods ──────────────────────────────────────

  /**
   * Get child pages of a given page
   */
  async getChildPages(pageId: string, limit: number = 25): Promise<ConfluenceChildPagesResult> {
    const response = await this.client.get<ConfluenceChildPagesResult>(
      `${this.API_BASE}/pages/${pageId}/children`,
      {
        params: {
          limit: Math.min(limit, 250),
        },
      }
    );

    return response.data;
  }

  /**
   * List accessible Confluence spaces
   */
  async listSpaces(limit: number = 25, type?: string): Promise<ConfluenceSpacesResult> {
    const queryParams: Record<string, any> = {
      limit: Math.min(limit, 250),
    };

    if (type) {
      queryParams.type = type;
    }

    const response = await this.client.get<ConfluenceSpacesResult>(
      `${this.API_BASE}/spaces`,
      { params: queryParams }
    );

    return response.data;
  }

  // ── CQL Search (v1 API) ──────────────────────────────────────────

  /**
   * Search Confluence content using CQL (Confluence Query Language)
   * Uses v1 API which supports CQL, unlike v2 which only supports title/space filtering
   */
  async searchCql(params: ConfluenceCqlSearchParams): Promise<ConfluenceCqlSearchResult> {
    const queryParams: Record<string, any> = {
      cql: params.cql,
      limit: Math.min(params.limit || 10, 100),
      start: params.start || 0,
    };

    const response = await this.client.get<ConfluenceCqlSearchResult>(
      `${this.API_V1_BASE}/content/search`,
      { params: queryParams }
    );

    return response.data;
  }
}
