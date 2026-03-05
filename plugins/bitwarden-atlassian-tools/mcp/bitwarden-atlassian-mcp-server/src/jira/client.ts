/**
 * JIRA REST API Client
 * Provides typed methods for interacting with JIRA Cloud API v3 and Agile API v1
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { loadJiraConfig, getJiraHeaders } from './auth.js';
import {
  JiraConfig,
  JiraSearchParams,
  JiraSearchResponse,
  JiraIssue,
  JiraCommentsResponse,
  JiraUser,
  JiraProject,
  JiraBoardsResponse,
  JiraSprintsResponse,
  JiraSprintIssuesResponse,
} from './types.js';

export class JiraClient {
  private config: JiraConfig;
  private client: AxiosInstance;
  private readonly API_BASE = '/rest/api/3';
  private readonly AGILE_API_BASE = '/rest/agile/1.0';

  constructor() {
    this.config = loadJiraConfig();
    this.client = axios.create({
      baseURL: this.config.url,
      headers: getJiraHeaders(this.config),
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
   * Handle and format JIRA API errors
   */
  private handleError(error: AxiosError): Error {
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as any;

      switch (status) {
        case 401:
          return new Error('JIRA authentication failed. Check your API token and email.');
        case 403:
          return new Error('JIRA access forbidden. Check your permissions.');
        case 404:
          return new Error(`JIRA resource not found: ${error.config?.url}`);
        case 410:
          return new Error('JIRA API endpoint deprecated (410 Gone). The requested resource has been removed.');
        case 429:
          return new Error('JIRA API rate limit exceeded. Please try again later.');
        default:
          return new Error(
            `JIRA API error (${status}): ${data?.errorMessages?.join(', ') || error.message}`
          );
      }
    }

    if (error.request) {
      return new Error(`JIRA API request failed: ${error.message}. Check your JIRA_URL.`);
    }

    return new Error(`JIRA client error: ${error.message}`);
  }

  /**
   * Search for issues using JQL (JIRA Query Language)
   */
  async searchIssues(params: JiraSearchParams): Promise<JiraSearchResponse> {
    const queryParams: Record<string, any> = {
      jql: params.jql,
      maxResults: Math.min(params.maxResults || 50, 100),
    };

    // New /search/jql endpoint uses nextPageToken instead of startAt
    if (params.nextPageToken) {
      queryParams.nextPageToken = params.nextPageToken;
    }

    if (params.fields && params.fields.length > 0) {
      queryParams.fields = params.fields.join(',');
    } else {
      // New endpoint only returns issue IDs by default; request all fields for backward compat
      queryParams.fields = '*all';
    }

    if (params.expand && params.expand.length > 0) {
      queryParams.expand = params.expand.join(',');
    }

    const response = await this.client.get<JiraSearchResponse>(
      `${this.API_BASE}/search/jql`,
      { params: queryParams }
    );

    return response.data;
  }

  /**
   * Get a single issue by key or ID
   */
  async getIssue(
    issueIdOrKey: string,
    fields?: string[],
    expand?: string[]
  ): Promise<JiraIssue> {
    const queryParams: Record<string, any> = {};

    if (fields && fields.length > 0) {
      queryParams.fields = fields.join(',');
    }

    if (expand && expand.length > 0) {
      queryParams.expand = expand.join(',');
    }

    const response = await this.client.get<JiraIssue>(
      `${this.API_BASE}/issue/${issueIdOrKey}`,
      { params: queryParams }
    );

    return response.data;
  }

  /**
   * Get all comments for an issue
   */
  async getIssueComments(
    issueIdOrKey: string,
    startAt: number = 0,
    maxResults: number = 50
  ): Promise<JiraCommentsResponse> {
    const response = await this.client.get<JiraCommentsResponse>(
      `${this.API_BASE}/issue/${issueIdOrKey}/comment`,
      {
        params: {
          startAt,
          maxResults: Math.min(maxResults, 100),
        },
      }
    );

    return response.data;
  }

  /**
   * Get current authenticated user information
   */
  async getCurrentUser(): Promise<JiraUser> {
    const response = await this.client.get<JiraUser>(
      `${this.API_BASE}/myself`
    );

    return response.data;
  }

  /**
   * Test connection and authentication
   */
  async testConnection(): Promise<boolean> {
    await this.getCurrentUser();
    return true;
  }

  /**
   * Download attachment as binary buffer
   */
  async downloadAttachment(attachmentUrl: string): Promise<Buffer> {
    const configOrigin = new URL(this.config.url).origin;
    const attachmentOrigin = new URL(attachmentUrl).origin;
    if (attachmentOrigin !== configOrigin) {
      throw new Error('Attachment URL does not belong to the configured Jira instance');
    }

    try {
      const response = await axios.get(attachmentUrl, {
        headers: getJiraHeaders(this.config),
        responseType: 'arraybuffer',
        timeout: 60000,
        maxContentLength: 50 * 1024 * 1024,
      });

      return Buffer.from(response.data);
    } catch (error: any) {
      if (error.code === 'ERR_FR_MAX_BODY_LENGTH_EXCEEDED') {
        throw new Error('Attachment exceeds maximum download size (50MB)');
      }
      throw this.handleError(error);
    }
  }

  // ── Agile API Methods ──────────────────────────────────────────────

  /**
   * List boards, optionally filtered by project
   */
  async listBoards(projectKeyOrId?: string, maxResults: number = 50): Promise<JiraBoardsResponse> {
    const queryParams: Record<string, any> = {
      maxResults: Math.min(maxResults, 100),
    };

    if (projectKeyOrId) {
      queryParams.projectKeyOrId = projectKeyOrId;
    }

    const response = await this.client.get<JiraBoardsResponse>(
      `${this.AGILE_API_BASE}/board`,
      { params: queryParams }
    );

    return response.data;
  }

  /**
   * Get sprints for a board, optionally filtered by state
   */
  async getSprints(boardId: number, state?: string, maxResults: number = 50): Promise<JiraSprintsResponse> {
    const queryParams: Record<string, any> = {
      maxResults: Math.min(maxResults, 100),
    };

    if (state) {
      queryParams.state = state;
    }

    const response = await this.client.get<JiraSprintsResponse>(
      `${this.AGILE_API_BASE}/board/${boardId}/sprint`,
      { params: queryParams }
    );

    return response.data;
  }

  /**
   * Get all issues in a sprint
   */
  async getSprintIssues(sprintId: number, fields?: string[], maxResults: number = 50): Promise<JiraSprintIssuesResponse> {
    const queryParams: Record<string, any> = {
      maxResults: Math.min(maxResults, 100),
    };

    if (fields && fields.length > 0) {
      queryParams.fields = fields.join(',');
    }

    const response = await this.client.get<JiraSprintIssuesResponse>(
      `${this.AGILE_API_BASE}/sprint/${sprintId}/issue`,
      { params: queryParams }
    );

    return response.data;
  }

  /**
   * List all accessible projects
   */
  async listProjects(maxResults: number = 50): Promise<JiraProject[]> {
    const response = await this.client.get<JiraProject[]>(
      `${this.API_BASE}/project`,
      {
        params: {
          maxResults: Math.min(maxResults, 100),
        },
      }
    );

    return response.data;
  }
}
