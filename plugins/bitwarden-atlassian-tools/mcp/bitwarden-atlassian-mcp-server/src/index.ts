#!/usr/bin/env node

/**
 * Atlassian MCP Server
 * MCP server for Jira and Confluence integration with Claude Code.
 * Confluence is read-only; Jira read is always on, and Jira write is opt-in
 * per install via ATLASSIAN_JIRA_WRITE_TOKEN.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import type { ToolDefinition } from "./utils/validation.js";

// Jira tools
import getIssue from "./tools/get-issue.js";
import getIssueComments from "./tools/get-issue-comments.js";
import getIssueRemoteLinks from "./tools/get-issue-remote-links.js";
import searchIssues from "./tools/search-issues.js";
import listProjects from "./tools/list-projects.js";
import listBoards from "./tools/list-boards.js";
import getSprints from "./tools/get-sprints.js";
import getSprintIssues from "./tools/get-sprint-issues.js";

// Confluence tools
import getConfluencePage from "./tools/get-confluence-page.js";
import getConfluencePageComments from "./tools/get-confluence-page-comments.js";
import getChildPages from "./tools/get-child-pages.js";
import searchConfluence from "./tools/search-confluence.js";
import searchConfluenceCql from "./tools/search-confluence-cql.js";
import listSpaces from "./tools/list-spaces.js";

// Cross-domain tools
import downloadAttachment from "./tools/download-attachment.js";

// Jira write tools
//
// These are registered unconditionally so that their dry-run path, which sends
// no request and needs no write credential, is available on a read-only install.
// Live execution is gated inside each handler on ATLASSIAN_JIRA_WRITE_TOKEN, so
// an install without that token behaves exactly as it does today.
//
// The alternative is gating registration itself on hasJiraWriteToken(), which
// hides the tools entirely from read-only installs. That is arguably the better
// production choice; it is not used here because it would also hide the dry-run
// preview, which should stay available so anyone can evaluate the write tools
// before minting a token.
// get_create_fields is read-only and useful on its own: it answers what a given
// project requires, which is what keeps the write tools free of any hardcoded
// per-project field knowledge.
import getCreateFields from "./tools/get-create-fields.js";
import createIssue from "./tools/create-issue.js";
import linkIssues from "./tools/link-issues.js";

const tools: ToolDefinition[] = [
  getIssue,
  getIssueComments,
  getIssueRemoteLinks,
  searchIssues,
  listProjects,
  listBoards,
  getSprints,
  getSprintIssues,
  getConfluencePage,
  getConfluencePageComments,
  getChildPages,
  searchConfluence,
  searchConfluenceCql,
  listSpaces,
  downloadAttachment,
  getCreateFields,
  createIssue,
  linkIssues,
];

async function main() {
  const requiredEnvVars = [
    "ATLASSIAN_CLOUD_ID",
    "ATLASSIAN_EMAIL",
    "ATLASSIAN_JIRA_READ_ONLY_TOKEN",
    "ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN",
  ];
  const missingVars = requiredEnvVars.filter((v) => !process.env[v]);

  if (missingVars.length > 0) {
    console.error(
      `Missing required environment variables: ${missingVars.join(", ")}`,
    );
    process.exit(1);
  }

  const server = new Server(
    { name: "bitwarden-atlassian-mcp", version: "2.0.0" },
    { capabilities: { tools: {} } },
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: tools.map((t) => ({
      name: t.name,
      description: t.description,
      inputSchema: t.inputSchema,
    })),
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    const tool = tools.find((t) => t.name === name);

    if (!tool) {
      throw new Error(`Unknown tool: ${name}`);
    }

    try {
      const result = await tool.handler(args || {});
      return { content: [{ type: "text", text: result }] };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`Tool error (${name}):`, message);
      return {
        content: [{ type: "text", text: `Error: ${message}` }],
        isError: true,
      };
    }
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
