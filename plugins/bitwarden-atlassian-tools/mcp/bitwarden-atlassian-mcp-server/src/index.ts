#!/usr/bin/env node

/**
 * Jira MCP Server
 * Read-only MCP server for Jira integration with Claude Code
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import type { ToolDefinition } from './utils/validation.js';

import getIssue from './tools/get-issue.js';
import getIssueComments from './tools/get-issue-comments.js';
import searchIssues from './tools/search-issues.js';
import listProjects from './tools/list-projects.js';

const tools: ToolDefinition[] = [
  getIssue,
  getIssueComments,
  searchIssues,
  listProjects,
];

async function main() {
  const requiredEnvVars = ['ATLASSIAN_JIRA_URL', 'ATLASSIAN_EMAIL', 'ATLASSIAN_JIRA_READ_ONLY_TOKEN'];
  const missingVars = requiredEnvVars.filter(v => !process.env[v]);

  if (missingVars.length > 0) {
    console.error(`Missing required environment variables: ${missingVars.join(', ')}`);
    process.exit(1);
  }

  const server = new Server(
    { name: 'bitwarden-atlassian-mcp', version: '1.0.0' },
    { capabilities: { tools: {} } },
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: tools.map(t => ({
      name: t.name,
      description: t.description,
      inputSchema: t.inputSchema,
    })),
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    const tool = tools.find(t => t.name === name);

    if (!tool) {
      throw new Error(`Unknown tool: ${name}`);
    }

    try {
      const result = await tool.handler(args || {});
      return { content: [{ type: 'text', text: result }] };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`Tool error (${name}):`, message);
      return { content: [{ type: 'text', text: `Error: ${message}` }], isError: true };
    }
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
