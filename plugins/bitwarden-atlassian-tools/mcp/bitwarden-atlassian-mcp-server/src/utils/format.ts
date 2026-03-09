/**
 * Shared formatting utilities for Confluence content
 */

/**
 * Convert Confluence storage format (XHTML) to readable markdown text.
 * Handles headings, lists, code blocks, inline formatting, and links.
 */
export function htmlToMarkdown(html: string): string {
  if (!html) return '';

  let text = html;

  // Replace common tags with readable equivalents
  text = text.replace(/<br\s*\/?>/gi, '\n');
  text = text.replace(/<\/p>/gi, '\n\n');
  text = text.replace(/<p[^>]*>/gi, '');
  text = text.replace(/<h([1-6])[^>]*>/gi, (_, level) => '\n' + '#'.repeat(parseInt(level)) + ' ');
  text = text.replace(/<\/h[1-6]>/gi, '\n');
  text = text.replace(/<li[^>]*>/gi, '- ');
  text = text.replace(/<\/li>/gi, '\n');
  text = text.replace(/<ul[^>]*>|<\/ul>/gi, '\n');
  text = text.replace(/<ol[^>]*>|<\/ol>/gi, '\n');
  text = text.replace(/<strong[^>]*>|<\/strong>/gi, '**');
  text = text.replace(/<b[^>]*>|<\/b>/gi, '**');
  text = text.replace(/<em[^>]*>|<\/em>/gi, '_');
  text = text.replace(/<i[^>]*>|<\/i>/gi, '_');
  text = text.replace(/<code[^>]*>|<\/code>/gi, '`');
  text = text.replace(/<pre[^>]*>/gi, '\n```\n');
  text = text.replace(/<\/pre>/gi, '\n```\n');
  text = text.replace(/<a[^>]*href="([^"]*)"[^>]*>([^<]*)<\/a>/gi, '[$2]($1)');

  // Remove remaining HTML tags
  text = text.replace(/<[^>]+>/g, '');

  // Decode HTML entities
  text = text.replace(/&nbsp;/g, ' ');
  text = text.replace(/&lt;/g, '<');
  text = text.replace(/&gt;/g, '>');
  text = text.replace(/&amp;/g, '&');
  text = text.replace(/&quot;/g, '"');
  text = text.replace(/&#39;/g, "'");

  // Clean up excessive newlines
  text = text.replace(/\n{3,}/g, '\n\n');

  return text.trim();
}

/**
 * Resolve a relative Confluence webui link to an absolute URL.
 * Falls back through ATLASSIAN_CONFLUENCE_URL then ATLASSIAN_JIRA_URL env vars.
 */
export function resolveWebuiUrl(webui: string): string {
  if (webui.startsWith('http')) return webui;
  const base = process.env.ATLASSIAN_CONFLUENCE_URL || process.env.ATLASSIAN_JIRA_URL || '';
  return `${base}${webui}`;
}