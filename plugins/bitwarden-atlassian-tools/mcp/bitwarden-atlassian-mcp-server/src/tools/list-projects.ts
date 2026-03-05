/**
 * List Projects Tool
 * List accessible JIRA projects
 */

import { JiraClient } from '../jira/client.js';
import { validateInput, ListProjectsSchema, ToolDefinition } from '../utils/validation.js';
import { JiraProject } from '../jira/types.js';

/**
 * Format project list for display
 */
function formatProjects(projects: JiraProject[]): string {
  let output = `# JIRA Projects\n\n`;
  output += `**Found:** ${projects.length} project(s)\n\n`;

  if (projects.length === 0) {
    output += `No accessible projects found.\n`;
    return output;
  }

  output += `---\n\n`;

  for (const project of projects) {
    output += `**${project.name}** (${project.key})\n`;
    output += `- ID: ${project.id}\n`;
    output += `- Type: ${project.projectTypeKey}\n`;
    if (project.description) {
      output += `- Description: ${project.description.substring(0, 200)}${project.description.length > 200 ? '...' : ''}\n`;
    }
    if (project.lead) {
      output += `- Lead: ${project.lead.displayName}\n`;
    }
    output += `\n`;
  }

  return output;
}

/**
 * Handler function for list-projects tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(ListProjectsSchema, input);
  const client = new JiraClient();

  try {
    const maxResults = validated.maxResults ?? 50;
    const projects = await client.listProjects(maxResults);

    return formatProjects(projects);
  } catch (error) {
    return `Error listing projects: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const listProjectsTool: ToolDefinition = {
  name: 'list_projects',
  description: 'List accessible JIRA projects. Returns project names, keys, types, descriptions, and leads. Use project keys with search_issues.',
  inputSchema: {
    type: 'object',
    properties: {
      maxResults: {
        type: 'number',
        description: 'Maximum number of projects to return (default: 50, max: 100)',
        default: 50,
        minimum: 1,
        maximum: 100,
      },
    },
  },
  handler,
};

export default listProjectsTool;
