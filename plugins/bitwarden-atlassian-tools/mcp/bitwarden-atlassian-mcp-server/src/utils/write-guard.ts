/**
 * Text shared by every opt-in write tool's write-token gate, kept in one place
 * so the next write tool doesn't re-derive this wording.
 *
 * Supports both Jira and Confluence write tools via the `product` parameter.
 */

export type WriteProduct = "jira" | "confluence";

const TOKEN_VAR: Record<WriteProduct, string> = {
  jira: "ATLASSIAN_JIRA_WRITE_TOKEN",
  confluence: "ATLASSIAN_CONFLUENCE_WRITE_TOKEN",
};

const AUTH_FAIL_TEXT: Record<WriteProduct, string> = {
  jira: "JIRA authentication failed",
  confluence: "Confluence authentication failed",
};

const PRODUCT_LABEL: Record<WriteProduct, string> = {
  jira: "Jira",
  confluence: "Confluence",
};

/** Appended to a dry-run preview when no write token is configured. */
export function writeTokenDryRunNote(
  action: string,
  product: WriteProduct = "jira",
): string[] {
  return [
    `> Note: ${TOKEN_VAR[product]} is not set on this install, so a live`,
    `> ${action} would fail at authentication. Dry runs do not need it.`,
    "",
  ];
}

/** Returned in place of a live write when no write token is configured. */
export function writeTokenRefusalMessage(
  action: string,
  product: WriteProduct = "jira",
): string {
  return (
    `Refusing to ${action}: ${TOKEN_VAR[product]} is not set.\n\n` +
    "This install has read-only credentials. Set a write-scoped Atlassian API " +
    `token as ${TOKEN_VAR[product]} to enable this, or call this tool ` +
    "with dryRun: true to preview the payload."
  );
}

/**
 * True for a client's generic 401 text — the one failure that could mean
 * the write token is present but missing part of the required scope set,
 * rather than a config or field problem.
 */
export function isWriteAuthError(
  message: string,
  product: WriteProduct = "jira",
): boolean {
  return message.includes(AUTH_FAIL_TEXT[product]);
}

/** Appended when a live write fails with isWriteAuthError. */
export function writeScopeHint(product: WriteProduct = "jira"): string {
  return (
    `If ${TOKEN_VAR[product]} is set, verify it carries the full scope ` +
    `set from the plugin README — ${PRODUCT_LABEL[product]} rejects a partial set with this same 401.`
  );
}
