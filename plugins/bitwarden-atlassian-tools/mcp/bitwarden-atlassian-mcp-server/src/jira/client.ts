/**
 * JIRA REST API Client
 * Provides typed methods for interacting with JIRA Cloud API v3 and Agile API v1
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import { loadJiraConfig, getJiraHeaders, JiraAccessMode } from "./auth.js";
import type { AdfDoc } from "../utils/adf-build.js";
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
  JiraRemoteLink,
  JiraCreateMetaIssueType,
  JiraCreateMetaField,
} from "./types.js";

export class JiraClient {
  private config: JiraConfig;
  private client: AxiosInstance;
  private readonly API_BASE = "/rest/api/3";
  private readonly AGILE_API_BASE = "/rest/agile/1.0";

  /**
   * @param mode - "read" (default) authenticates with the read-only token that
   *   every install sets. "write" authenticates with the optional write token
   *   and throws if it is absent, so a missing token fails at construction
   *   rather than on a half-completed sequence of creates.
   */
  constructor(mode: JiraAccessMode = "read") {
    this.config = loadJiraConfig(mode);
    this.client = axios.create({
      baseURL: this.config.gatewayBaseUrl,
      headers: getJiraHeaders(this.config),
      timeout: 30000, // 30 second timeout
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        return Promise.reject(this.handleError(error));
      },
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
          return new Error(
            "JIRA authentication failed. Check your API token and email.",
          );
        case 403:
          return new Error("JIRA access forbidden. Check your permissions.");
        case 404:
          return new Error(`JIRA resource not found: ${error.config?.url}`);
        case 410:
          return new Error(
            "JIRA API endpoint deprecated (410 Gone). The requested resource has been removed.",
          );
        case 429:
          return new Error(
            "JIRA API rate limit exceeded. Please try again later.",
          );
        default: {
          // Field-level create/update errors (missing required field, field not on
          // screen) land in `errors` keyed by field id, not in `errorMessages`.
          const fieldErrors = data?.errors
            ? Object.entries(data.errors).map(
                ([field, msg]) => `${field}: ${msg}`,
              )
            : [];
          const detail =
            [...(data?.errorMessages ?? []), ...fieldErrors].join("; ") ||
            error.message;
          return new Error(`JIRA API error (${status}): ${detail}`);
        }
      }
    }

    if (error.request) {
      return new Error(
        `JIRA API request failed: ${error.message}. Check your ATLASSIAN_CLOUD_ID.`,
      );
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
      queryParams.fields = params.fields.join(",");
    } else {
      // New endpoint only returns issue IDs by default; request all fields for backward compat
      queryParams.fields = "*all";
    }

    if (params.expand && params.expand.length > 0) {
      queryParams.expand = params.expand.join(",");
    }

    const response = await this.client.get<JiraSearchResponse>(
      `${this.API_BASE}/search/jql`,
      { params: queryParams },
    );

    return response.data;
  }

  /**
   * Get a single issue by key or ID
   */
  async getIssue(
    issueIdOrKey: string,
    fields?: string[],
    expand?: string[],
  ): Promise<JiraIssue> {
    const queryParams: Record<string, any> = {};

    if (fields && fields.length > 0) {
      queryParams.fields = fields.join(",");
    }

    if (expand && expand.length > 0) {
      queryParams.expand = expand.join(",");
    }

    const response = await this.client.get<JiraIssue>(
      `${this.API_BASE}/issue/${issueIdOrKey}`,
      { params: queryParams },
    );

    return response.data;
  }

  /**
   * Get all comments for an issue
   */
  async getIssueComments(
    issueIdOrKey: string,
    startAt: number = 0,
    maxResults: number = 50,
  ): Promise<JiraCommentsResponse> {
    const response = await this.client.get<JiraCommentsResponse>(
      `${this.API_BASE}/issue/${issueIdOrKey}/comment`,
      {
        params: {
          startAt,
          maxResults: Math.min(maxResults, 100),
        },
      },
    );

    return response.data;
  }

  /**
   * Get current authenticated user information
   */
  async getCurrentUser(): Promise<JiraUser> {
    const response = await this.client.get<JiraUser>(`${this.API_BASE}/myself`);

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
   * Download attachment as binary buffer.
   * Rewrites direct *.atlassian.net URLs to route through the API gateway
   * so that scoped API tokens authenticate correctly.
   */
  async downloadAttachment(attachmentUrl: string): Promise<Buffer> {
    const parsed = new URL(attachmentUrl);
    if (
      !parsed.hostname.endsWith(".atlassian.net") ||
      parsed.hostname === ".atlassian.net"
    ) {
      throw new Error("Attachment URL must be an *.atlassian.net hostname");
    }

    // Route through the API gateway so scoped tokens work
    const gatewayUrl = `${this.config.gatewayBaseUrl}${parsed.pathname}${parsed.search}`;

    try {
      const response = await this.client.get(gatewayUrl, {
        responseType: "arraybuffer",
        timeout: 60000,
        maxContentLength: 50 * 1024 * 1024,
      });

      return Buffer.from(response.data);
    } catch (error: any) {
      if (
        error.code === "ERR_FR_MAX_BODY_LENGTH_EXCEEDED" ||
        error.message?.includes("maxContentLength")
      ) {
        throw new Error("Attachment exceeds maximum download size (50MB)");
      }
      throw error; // already transformed by the response interceptor
    }
  }

  // ── Agile API Methods ──────────────────────────────────────────────

  /**
   * List boards, optionally filtered by project
   */
  async listBoards(
    projectKeyOrId?: string,
    maxResults: number = 50,
  ): Promise<JiraBoardsResponse> {
    const queryParams: Record<string, any> = {
      maxResults: Math.min(maxResults, 100),
    };

    if (projectKeyOrId) {
      queryParams.projectKeyOrId = projectKeyOrId;
    }

    const response = await this.client.get<JiraBoardsResponse>(
      `${this.AGILE_API_BASE}/board`,
      { params: queryParams },
    );

    return response.data;
  }

  /**
   * Get sprints for a board, optionally filtered by state
   */
  async getSprints(
    boardId: number,
    state?: string,
    maxResults: number = 50,
  ): Promise<JiraSprintsResponse> {
    const queryParams: Record<string, any> = {
      maxResults: Math.min(maxResults, 100),
    };

    if (state) {
      queryParams.state = state;
    }

    const response = await this.client.get<JiraSprintsResponse>(
      `${this.AGILE_API_BASE}/board/${boardId}/sprint`,
      { params: queryParams },
    );

    return response.data;
  }

  /**
   * Get all issues in a sprint
   */
  async getSprintIssues(
    sprintId: number,
    fields?: string[],
    maxResults: number = 50,
  ): Promise<JiraSprintIssuesResponse> {
    const queryParams: Record<string, any> = {
      maxResults: Math.min(maxResults, 100),
    };

    if (fields && fields.length > 0) {
      queryParams.fields = fields.join(",");
    }

    const response = await this.client.get<JiraSprintIssuesResponse>(
      `${this.AGILE_API_BASE}/sprint/${sprintId}/issue`,
      { params: queryParams },
    );

    return response.data;
  }

  /**
   * Get remote links for an issue (Confluence pages, PRs, external URLs)
   */
  async getRemoteLinks(issueIdOrKey: string): Promise<JiraRemoteLink[]> {
    const response = await this.client.get<JiraRemoteLink[]>(
      `${this.API_BASE}/issue/${issueIdOrKey}/remotelink`,
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
      },
    );

    return response.data;
  }

  // ── Write Methods (require a client constructed with mode "write") ──

  /**
   * Create a work item.
   *
   * @param fields - A fully-formed Jira `fields` object. Built by the calling
   *   tool so that field-ID knowledge lives in one place.
   * @returns The created item's key and id.
   */
  async createIssue(
    fields: Record<string, unknown>,
  ): Promise<{ id: string; key: string; self: string }> {
    const response = await this.client.post<{
      id: string;
      key: string;
      self: string;
    }>(`${this.API_BASE}/issue`, { fields });

    return response.data;
  }

  /**
   * Add a comment to an issue.
   *
   * @param body - A fully-formed ADF comment body. Built by the calling tool.
   * @returns The created comment's id.
   */
  async addIssueComment(
    issueIdOrKey: string,
    body: AdfDoc,
  ): Promise<{ id: string; created: string }> {
    const response = await this.client.post<{ id: string; created: string }>(
      `${this.API_BASE}/issue/${issueIdOrKey}/comment`,
      { body },
    );

    return response.data;
  }

  /**
   * Link two work items.
   *
   * Jira's payload is (inwardIssue, outwardIssue) and reads
   * "outwardIssue <outward description> inwardIssue". For type "Blocks" the
   * descriptions are outward "blocks" and inward "is blocked by", so the
   * outward issue is the blocker.
   *
   * Verified read-only against the live PM project: the same Blocks link between
   * PM-39203 and PM-38796 is reported from PM-39203 as carrying `inwardIssue:
   * PM-38796`, and from PM-38796 as carrying `outwardIssue: PM-39203`. Each end
   * names the other and labels it with the other end's role, so the canonical
   * pair is outward=PM-39203, inward=PM-38796, i.e. PM-39203 blocks PM-38796.
   *
   * Note this is the opposite of the acli CLI's `--in`/`--out` mapping.
   */
  async createIssueLink(params: {
    typeName: string;
    outwardKey: string;
    inwardKey: string;
  }): Promise<void> {
    await this.client.post(`${this.API_BASE}/issueLink`, {
      type: { name: params.typeName },
      outwardIssue: { key: params.outwardKey },
      inwardIssue: { key: params.inwardKey },
    });
  }

  // ── Create-screen Metadata (read-only, works with either token) ─────

  /**
   * List the issue types a project can create, as this user.
   *
   * Jira answers 404 with "You cannot create issues in this project" when the
   * user has no create permission there, which the calling tool surfaces as an
   * ordinary result rather than a failure.
   */
  async getCreateMetaIssueTypes(
    projectKey: string,
  ): Promise<{ issueTypes: JiraCreateMetaIssueType[] }> {
    const response = await this.client.get<{
      issueTypes: JiraCreateMetaIssueType[];
    }>(`${this.API_BASE}/issue/createmeta/${projectKey}/issuetypes`, {
      params: { maxResults: 60 },
    });

    return response.data;
  }

  /**
   * Read the create screen's field metadata for a project + issue type.
   *
   * This is the authority on which fields exist, which are required, and what
   * their allowed values are. It varies per project: PM and SM expose an
   * Acceptance criteria field, QA and VULN do not, and team-managed projects can
   * scope custom fields to themselves.
   */
  async getCreateMetaFields(
    projectKey: string,
    issueTypeId: string,
  ): Promise<{ fields: JiraCreateMetaField[] }> {
    const response = await this.client.get<{ fields: JiraCreateMetaField[] }>(
      `${this.API_BASE}/issue/createmeta/${projectKey}/issuetypes/${issueTypeId}`,
      { params: { maxResults: 200 } },
    );

    return response.data;
  }
}
