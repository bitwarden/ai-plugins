#!/usr/bin/env node

/**
 * Test automation MCP server. Read-only: it reads bitwarden/test on GitHub
 * through the user's gh login and never calls Testmo. Testmo case IDs come in
 * as tool arguments.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { tlsGuardMessage } from "./config.js";
import { createToolContext } from "./context.js";
import type { ToolDefinition } from "./tools/types.js";
import findAutomatedCases from "./tools/find-automated-cases.js";

const tools: ToolDefinition[] = [findAutomatedCases];

async function main() {
  const refusal = tlsGuardMessage(process.env);
  if (refusal) {
    console.error(refusal);
    process.exit(1);
  }

  const ctx = createToolContext();

  const server = new Server(
    { name: "bitwarden-test-automation-mcp", version: "1.0.0" },
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
      const result = await tool.handler(args || {}, ctx);
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
  console.error(
    "Fatal error:",
    error instanceof Error ? error.message : String(error),
  );
  process.exit(1);
});
