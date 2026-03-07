/**
 * Download Attachment Tool
 * Retrieve JIRA attachment content as Base64-encoded data
 */

import { JiraClient } from '../jira/client.js';
import { validateInput, DownloadAttachmentSchema, ToolDefinition } from '../utils/validation.js';
import { AttachmentDownloadResult } from '../jira/types.js';

/**
 * Extract filename from attachment URL
 */
function extractFilename(url: string): string {
  try {
    const urlObj = new URL(url);
    const pathParts = urlObj.pathname.split('/');
    const filename = pathParts[pathParts.length - 1];
    return decodeURIComponent(filename);
  } catch {
    return 'attachment';
  }
}

/**
 * Detect MIME type from filename extension
 */
function guessMimeType(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase();
  const mimeMap: Record<string, string> = {
    'pdf': 'application/pdf',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'txt': 'text/plain',
    'json': 'application/json',
    'xml': 'application/xml',
    'zip': 'application/zip',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  };
  return mimeMap[ext || ''] || 'application/octet-stream';
}

/**
 * Format download result for display
 */
function formatResult(result: AttachmentDownloadResult): string {
  const sizeMB = (result.sizeBytes / (1024 * 1024)).toFixed(2);

  let output = `# Attachment Downloaded Successfully\n\n`;
  output += `**Filename:** ${result.filename}\n`;
  output += `**MIME Type:** ${result.mimeType}\n`;
  output += `**Size:** ${result.sizeBytes.toLocaleString()} bytes (${sizeMB} MB)\n\n`;

  if (result.warning) {
    output += `**Warning:** ${result.warning}\n\n`;
  }

  output += `## Base64-Encoded Content\n\n`;
  output += `\`\`\`\n${result.contentBase64}\n\`\`\`\n\n`;
  output += `**Note:** Content is Base64-encoded for transport. `;
  output += `Decode before use: \`Buffer.from(content, 'base64')\`\n`;

  return output;
}

/**
 * Handler function for download-attachment tool
 */
async function handler(input: any): Promise<string> {
  const validated = validateInput(DownloadAttachmentSchema, input);
  const client = new JiraClient();

  try {
    const filename = extractFilename(validated.attachmentUrl);

    // Download binary content
    const buffer = await client.downloadAttachment(validated.attachmentUrl);
    const sizeBytes = buffer.length;
    const sizeMB = sizeBytes / (1024 * 1024);

    // Check size against user-specified limit
    const maxSizeMB = validated.maxSizeMB ?? 10;
    if (sizeMB > maxSizeMB) {
      return `Error: Attachment size (${sizeMB.toFixed(2)} MB) exceeds specified limit (${maxSizeMB} MB). ` +
             `Use maxSizeMB parameter to increase limit (max: 50 MB).`;
    }

    // Generate warning for large files
    let warning: string | undefined;
    if (sizeMB > 5) {
      warning = `Large file (${sizeMB.toFixed(2)} MB) may cause token limit issues in MCP responses. ` +
                `Consider downloading separately if processing fails.`;
    }

    // Convert to Base64
    const contentBase64 = buffer.toString('base64');
    const mimeType = guessMimeType(filename);

    const result: AttachmentDownloadResult = {
      filename,
      mimeType,
      sizeBytes,
      contentBase64,
      warning,
    };

    return formatResult(result);

  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('403')) {
        return `Error: Access denied to attachment. Check JIRA permissions for this attachment.`;
      }
      if (error.message.includes('404')) {
        return `Error: Attachment not found at URL. Verify the URL is correct and attachment still exists.`;
      }
      if (error.message.includes('timeout')) {
        return `Error: Download timeout. Attachment may be too large or network is slow.`;
      }
    }
    return `Error downloading attachment: ${error instanceof Error ? error.message : String(error)}`;
  }
}

/**
 * Tool definition export
 */
const downloadAttachmentTool: ToolDefinition = {
  name: 'download_attachment',
  description: 'Download a JIRA attachment and return Base64-encoded content. ' +
               'Use the attachment URL from get_issue tool output. ' +
               'Supports files up to 50MB with configurable size limits.',
  inputSchema: {
    type: 'object',
    properties: {
      attachmentUrl: {
        type: 'string',
        description: 'Full attachment URL from get_issue output (attachment.content field). ' +
                     'Example: https://your-domain.atlassian.net/secure/attachment/12345/filename.pdf',
      },
      maxSizeMB: {
        type: 'number',
        description: 'Maximum file size to download in megabytes (default: 10, max: 50). ' +
                     'Prevents downloading unexpectedly large files.',
        default: 10,
      },
    },
    required: ['attachmentUrl'],
  },
  handler,
};

export default downloadAttachmentTool;
