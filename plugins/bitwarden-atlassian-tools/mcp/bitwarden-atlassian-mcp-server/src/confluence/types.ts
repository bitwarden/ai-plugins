/**
 * TypeScript type definitions for Confluence REST API v2
 * Used by the MCP server for type-safe Confluence API interactions
 */

export interface ConfluenceConfig {
  url: string;
  email: string;
  apiToken: string;
}

export interface ConfluenceUser {
  accountId: string;
  accountType: string;
  email?: string;
  publicName: string;
  displayName: string;
}

export interface ConfluenceSpace {
  id: string;
  key: string;
  name: string;
  type: string;
  status: string;
  _links?: {
    webui: string;
    self: string;
  };
}

export interface ConfluenceVersion {
  by: ConfluenceUser;
  when: string;
  number: number;
  message?: string;
}

export interface ConfluencePageBody {
  storage?: {
    value: string;
    representation: string;
  };
  view?: {
    value: string;
    representation: string;
  };
  export_view?: {
    value: string;
    representation: string;
  };
}

export interface ConfluencePage {
  id: string;
  type: string;
  status: string;
  title: string;
  spaceId?: string;
  space?: ConfluenceSpace;
  parentId?: string;
  parentType?: string;
  position?: number;
  authorId?: string;
  ownerId?: string;
  lastOwnerId?: string;
  createdAt?: string;
  version?: ConfluenceVersion;
  body?: ConfluencePageBody;
  _links?: {
    webui: string;
    editui: string;
    tinyui: string;
    self: string;
  };
}

export interface ConfluenceSearchResult {
  results: ConfluencePage[];
  _links?: {
    base?: string;
    context?: string;
    next?: string;
  };
}

export interface ConfluenceGetPageParams {
  pageId: string;
  includeBody?: boolean;
  bodyFormat?: 'storage' | 'view' | 'export_view';
}

export interface ConfluenceSearchParams {
  spaceKey?: string;
  title?: string;
  limit?: number;
  cursor?: string;
}

export interface ConfluenceCommentBody {
  storage?: {
    value: string;
    representation: string;
  };
  view?: {
    value: string;
    representation: string;
  };
}

export interface ConfluenceInlineProperties {
  inlineMarkerRef?: string;
  inlineOriginalSelection?: string;
}

export interface ConfluenceComment {
  id: string;
  status: string;
  title?: string;
  pageId?: string;
  parentCommentId?: string;
  version?: ConfluenceVersion;
  body?: ConfluenceCommentBody;
  createdAt?: string;
  properties?: ConfluenceInlineProperties;
  resolutionStatus?: 'open' | 'resolved' | 'reopened';
  _links?: {
    webui: string;
    self: string;
  };
}

export interface ConfluenceCommentsResult {
  results: ConfluenceComment[];
  _links?: {
    base?: string;
    context?: string;
    next?: string;
  };
}

export interface ConfluenceGetCommentsParams {
  pageId: string;
  bodyFormat?: 'storage' | 'view';
  limit?: number;
  cursor?: string;
}

export interface ConfluenceGetCommentRepliesParams {
  commentId: string;
  bodyFormat?: 'storage' | 'view';
  limit?: number;
  cursor?: string;
}

export interface ConfluenceSpacesResult {
  results: ConfluenceSpace[];
  _links?: {
    base?: string;
    context?: string;
    next?: string;
  };
}

export interface ConfluenceChildPagesResult {
  results: ConfluencePage[];
  _links?: {
    base?: string;
    context?: string;
    next?: string;
  };
}

// ── CQL Search Types (v1 API) ───────────────────────────────────────

export interface ConfluenceCqlSearchParams {
  cql: string;
  limit?: number;
  start?: number;
}

export interface ConfluenceCqlSearchResultItem {
  id: string;
  type: string;
  status: string;
  title: string;
  space: { key: string; name: string };
  _links: { webui: string };
}

export interface ConfluenceCqlSearchResult {
  results: ConfluenceCqlSearchResultItem[];
  start: number;
  limit: number;
  size: number;
  totalSize: number;
}
