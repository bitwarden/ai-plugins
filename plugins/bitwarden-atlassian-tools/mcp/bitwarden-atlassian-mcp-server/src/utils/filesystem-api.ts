/**
 * Filesystem-based MCP Tool Discovery
 * Implements the Anthropic pattern for progressive disclosure of tools
 * Reduces context consumption by allowing Claude to explore tools on-demand
 */

import { readdir, readFile } from 'fs/promises';
import { join, basename, extname } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: any;
  handler: (input: any) => Promise<any>;
}

export interface ToolFile {
  name: string;
  path: string;
  isDirectory: boolean;
}

/**
 * Discover all tool files in the tools directory
 * Returns a filesystem-like structure that MCP clients can navigate
 */
export async function discoverTools(): Promise<ToolFile[]> {
  const toolsDir = join(__dirname, '..', 'tools');

  try {
    const files = await readdir(toolsDir, { withFileTypes: true });

    return files
      .filter(file => {
        // Include only .js files (compiled output), excluding .d.ts and source maps
        const name = file.name;
        return file.isFile() &&
               name.endsWith('.js') &&
               !name.endsWith('.d.ts') &&
               !name.endsWith('.map') &&
               !name.endsWith('.d.js');
      })
      .map(file => ({
        name: basename(file.name, extname(file.name)),
        path: join('tools', file.name),
        isDirectory: false,
      }));
  } catch (error) {
    console.error('Error discovering tools:', error);
    return [];
  }
}

/**
 * Load a specific tool module dynamically
 * @param toolName - Name of the tool to load (without extension)
 * @returns Tool definition with handler function
 */
export async function loadTool(toolName: string): Promise<ToolDefinition | null> {
  try {
    const toolPath = join(__dirname, '..', 'tools', `${toolName}.js`);
    const toolModule = await import(toolPath);

    if (!toolModule.default) {
      console.error(`Tool ${toolName} does not export a default definition`);
      return null;
    }

    return toolModule.default as ToolDefinition;
  } catch (error) {
    console.error(`Error loading tool ${toolName}:`, error);
    return null;
  }
}

/**
 * Load all available tools
 * Used during server initialization to register tools with MCP
 * @returns Array of tool definitions
 */
export async function loadAllTools(): Promise<ToolDefinition[]> {
  const toolFiles = await discoverTools();
  const tools: ToolDefinition[] = [];

  for (const file of toolFiles) {
    const tool = await loadTool(file.name);
    if (tool) {
      tools.push(tool);
    }
  }

  return tools;
}

/**
 * Format tool information for display
 * Creates human-readable documentation for each tool
 */
export function formatToolInfo(tool: ToolDefinition): string {
  const params = tool.inputSchema.properties;
  const required = tool.inputSchema.required || [];

  let info = `# ${tool.name}\n\n`;
  info += `${tool.description}\n\n`;
  info += `## Parameters\n\n`;

  for (const [paramName, paramSchema] of Object.entries(params as Record<string, any>)) {
    const isRequired = required.includes(paramName);
    const requiredTag = isRequired ? ' (required)' : ' (optional)';
    const description = paramSchema.description || 'No description';

    info += `- **${paramName}**${requiredTag}: ${description}\n`;

    if (paramSchema.type) {
      info += `  - Type: ${paramSchema.type}\n`;
    }

    if (paramSchema.default !== undefined) {
      info += `  - Default: ${paramSchema.default}\n`;
    }

    if (paramSchema.minimum !== undefined || paramSchema.maximum !== undefined) {
      info += `  - Range: ${paramSchema.minimum ?? '∞'} - ${paramSchema.maximum ?? '∞'}\n`;
    }
  }

  return info;
}

/**
 * Get tool list as formatted string for MCP resource
 * Provides an index of all available tools
 */
export async function getToolListResource(): Promise<string> {
  const toolFiles = await discoverTools();

  let content = '# Available JIRA Tools\n\n';
  content += 'This MCP server provides read-only access to JIRA for requirement review and implementation planning.\n\n';
  content += '## Tools\n\n';

  for (const file of toolFiles) {
    content += `- **${file.name}** - Load this tool for detailed information\n`;
  }

  content += '\n## Usage\n\n';
  content += 'To use a tool, reference it by name in your requests. The server will load the tool definition on-demand.\n';

  return content;
}
