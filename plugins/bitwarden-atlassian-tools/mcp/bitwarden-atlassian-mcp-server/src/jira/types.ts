/**
 * TypeScript type definitions for JIRA REST API v3
 * Used by the MCP JIRA server for type-safe API interactions
 */

export interface JiraConfig {
  cloudId: string;
  gatewayBaseUrl: string;
  email: string;
  apiToken: string;
}

export interface JiraUser {
  accountId: string;
  displayName: string;
  emailAddress?: string;
  active: boolean;
  timeZone?: string;
  avatarUrls?: {
    '48x48': string;
    '24x24': string;
    '16x16': string;
    '32x32': string;
  };
}

export interface JiraProject {
  id: string;
  key: string;
  name: string;
  description?: string;
  projectTypeKey: string;
  lead?: JiraUser;
  avatarUrls?: Record<string, string>;
}

export interface JiraIssueType {
  id: string;
  name: string;
  description?: string;
  iconUrl?: string;
  subtask: boolean;
}

export interface JiraStatus {
  id: string;
  name: string;
  description?: string;
  statusCategory: {
    id: number;
    key: string;
    name: string;
    colorName: string;
  };
}

export interface JiraPriority {
  id: string;
  name: string;
  iconUrl?: string;
}

export interface JiraComment {
  id: string;
  author: JiraUser;
  body: {
    type: string;
    version: number;
    content: any[];
  };
  created: string;
  updated: string;
}

export interface JiraAttachment {
  id: string;
  filename: string;
  size: number;
  mimeType: string;
  content: string;
  thumbnail?: string;
  created: string;
  author: JiraUser;
}

export interface JiraIssueFields {
  summary: string;
  description?: {
    type: string;
    version: number;
    content: any[];
  };
  issuetype: JiraIssueType;
  project: JiraProject;
  status: JiraStatus;
  priority?: JiraPriority;
  assignee?: JiraUser;
  reporter: JiraUser;
  created: string;
  updated: string;
  duedate?: string;
  resolutiondate?: string;
  labels?: string[];
  components?: Array<{
    id: string;
    name: string;
    description?: string;
  }>;
  fixVersions?: Array<{
    id: string;
    name: string;
    description?: string;
    released: boolean;
  }>;
  comment?: {
    comments: JiraComment[];
    total: number;
  };
  attachment?: JiraAttachment[];
  subtasks?: JiraIssue[];
  parent?: JiraIssue;
  [key: string]: any; // Custom fields
}

export interface JiraIssue {
  id: string;
  key: string;
  self: string;
  fields: JiraIssueFields;
}

export interface JiraSearchResponse {
  expand?: string;
  startAt: number;
  maxResults: number;
  total?: number;
  issues: JiraIssue[];
  nextPageToken?: string;
}

export interface JiraSearchParams {
  jql: string;
  maxResults?: number;
  fields?: string[];
  expand?: string[];
  nextPageToken?: string;
}

export interface JiraCommentsResponse {
  startAt: number;
  maxResults: number;
  total: number;
  comments: JiraComment[];
}

/**
 * Attachment download result with Base64-encoded content
 */
export interface AttachmentDownloadResult {
  filename: string;
  mimeType: string;
  sizeBytes: number;
  contentBase64: string;
  warning?: string;  // For size warnings
}

/**
 * Agile API types for boards, sprints, and sprint issues
 */

export interface JiraBoard {
  id: number;
  self: string;
  name: string;
  type: string;
  location?: {
    projectId: number;
    displayName: string;
    projectName: string;
    projectKey: string;
    projectTypeKey: string;
    name: string;
  };
}

export interface JiraBoardsResponse {
  maxResults: number;
  startAt: number;
  total: number;
  isLast: boolean;
  values: JiraBoard[];
}

export interface JiraSprint {
  id: number;
  self: string;
  state: string;
  name: string;
  startDate?: string;
  endDate?: string;
  completeDate?: string;
  originBoardId: number;
  goal?: string;
}

export interface JiraSprintsResponse {
  maxResults: number;
  startAt: number;
  isLast: boolean;
  values: JiraSprint[];
}

export interface JiraSprintIssuesResponse {
  expand: string;
  startAt: number;
  maxResults: number;
  total: number;
  issues: JiraIssue[];
}
