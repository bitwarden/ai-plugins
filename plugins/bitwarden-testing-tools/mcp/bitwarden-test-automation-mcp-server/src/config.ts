/**
 * Startup checks for the test automation server. The server reads GitHub only
 * and makes no Testmo calls, so it has no Testmo settings to load.
 */

/**
 * Returns a refusal message when TLS verification is disabled for this
 * process. With verification off, every Node connection this server makes
 * accepts any certificate, so the server does not start.
 */
export function tlsGuardMessage(env: NodeJS.ProcessEnv): string | undefined {
  if (env.NODE_TLS_REJECT_UNAUTHORIZED === "0") {
    return (
      "Refusing to start: NODE_TLS_REJECT_UNAUTHORIZED is 0, which turns off " +
      "certificate checks for every Node connection this server makes. " +
      "Unset it and restart."
    );
  }
  return undefined;
}
