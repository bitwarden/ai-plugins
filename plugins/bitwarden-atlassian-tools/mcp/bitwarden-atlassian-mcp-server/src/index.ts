#!/usr/bin/env node

/**
 * JIRA MCP Server
 * Custom read-only MCP server for JIRA integration with Claude Code
 * Implements filesystem-based progressive disclosure for efficient context usage
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { loadAllTools, formatToolInfo, getToolListResource } from './utils/filesystem-api.js';

/**
 * Initialize and start the MCP server
 */
async function main() {
  console.error('Starting JIRA MCP Server...');

  // Validate environment variables
  const requiredEnvVars = ['JIRA_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN'];
  const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

  if (missingVars.length > 0) {
    console.error(`Error: Missing required environment variables: ${missingVars.join(', ')}`);
    console.error('Please set these variables before starting the server.');
    process.exit(1);
  }

  // Load all tools
  console.error('Loading tools...');
  const tools = await loadAllTools();
  console.error(`Loaded ${tools.length} tools:`, tools.map(t => t.name).join(', '));

  // Create MCP server
  const server = new Server(
    {
      name: 'jira-mcp-server',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
        resources: {},
      },
    }
  );

  // Register tool list handler
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: tools.map(tool => ({
        name: tool.name,
        description: tool.description,
        inputSchema: tool.inputSchema,
      })),
    };
  });

  // Register tool execution handler
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const toolName = request.params.name;
    const tool = tools.find(t => t.name === toolName);

    if (!tool) {
      throw new Error(`Unknown tool: ${toolName}`);
    }

    try {
      console.error(`Executing tool: ${toolName}`);
      const result = await tool.handler(request.params.arguments || {});

      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error(`Tool execution error (${toolName}):`, errorMessage);

      return {
        content: [
          {
            type: 'text',
            text: `Error executing ${toolName}: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  });

  // Register resource list handler (for filesystem-like navigation)
  server.setRequestHandler(ListResourcesRequestSchema, async () => {
    return {
      resources: [
        {
          uri: 'jira://tools',
          name: 'Available JIRA Tools',
          description: 'List of all available JIRA integration tools',
          mimeType: 'text/markdown',
        },
      ],
    };
  });

  // Register resource read handler
  server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
    const uri = request.params.uri;

    if (uri === 'jira://tools') {
      const content = await getToolListResource();
      return {
        contents: [
          {
            uri,
            mimeType: 'text/markdown',
            text: content,
          },
        ],
      };
    }

    throw new Error(`Unknown resource: ${uri}`);
  });

  // Start the server with stdio transport
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('JIRA MCP Server running on stdio');
  console.error(`Connected to JIRA: ${process.env.JIRA_URL}`);
}

// Error handling
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
