/**
 * Text shared by every opt-in write tool's write-token gate, kept in one place
 * so the next write tool doesn't re-derive this wording.
 *
 * Each helper defaults to the Jira write token so existing Jira call sites read
 * unchanged; the Confluence write tools pass their own token variable and
 * product name. Defaults reproduce the original Jira wording byte-for-byte.
 */

const JIRA_WRITE_TOKEN = "ATLASSIAN_JIRA_WRITE_TOKEN";

/** Appended to a dry-run preview when no write token is configured. */
export function writeTokenDryRunNote(
  action: string,
  tokenVar: string = JIRA_WRITE_TOKEN,
): string[] {
  return [
    `> Note: ${tokenVar} is not set on this install, so a live`,
    `> ${action} would fail at authentication. Dry runs do not need it.`,
    "",
  ];
}

/** Returned in place of a live write when no write token is configured. */
export function writeTokenRefusalMessage(
  action: string,
  tokenVar: string = JIRA_WRITE_TOKEN,
): string {
  return (
    `Refusing to ${action}: ${tokenVar} is not set.\n\n` +
    "This install has read-only credentials. Set a write-scoped Atlassian API " +
    `token as ${tokenVar} to enable this, or call this tool ` +
    "with dryRun: true to preview the payload."
  );
}

/**
 * True for a client's generic 401 text — the one failure that could mean the
 * write token is present but missing part of the required scope set, rather than
 * a config or content problem. `product` matches the client's error prefix
 * ("JIRA" or "Confluence").
 */
export function isWriteAuthError(
  message: string,
  product: string = "JIRA",
): boolean {
  return message.includes(`${product} authentication failed`);
}

/** Appended when a live write fails with isWriteAuthError. */
export function writeScopeHint(
  tokenVar: string = JIRA_WRITE_TOKEN,
  product: string = "Jira",
): string {
  return (
    `If ${tokenVar} is set, verify it carries the full scope ` +
    `set from the plugin README — ${product} rejects a partial set with this same 401.`
  );
}
