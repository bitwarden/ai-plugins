/**
 * Text shared by every opt-in write tool's `ATLASSIAN_JIRA_WRITE_TOKEN` gate,
 * kept in one place so the next write tool doesn't re-derive this wording.
 */

/** Appended to a dry-run preview when no write token is configured. */
export function writeTokenDryRunNote(action: string): string[] {
  return [
    "> Note: ATLASSIAN_JIRA_WRITE_TOKEN is not set on this install, so a live",
    `> ${action} would fail at authentication. Dry runs do not need it.`,
    "",
  ];
}

/** Returned in place of a live write when no write token is configured. */
export function writeTokenRefusalMessage(action: string): string {
  return (
    `Refusing to ${action}: ATLASSIAN_JIRA_WRITE_TOKEN is not set.\n\n` +
    "This install has read-only credentials. Set a write-scoped Atlassian API " +
    "token as ATLASSIAN_JIRA_WRITE_TOKEN to enable this, or call this tool " +
    "with dryRun: true to preview the payload."
  );
}
