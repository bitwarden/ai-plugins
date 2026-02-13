# Architectural Anti-Patterns

Common security architecture anti-patterns and their fixes.

## Implicit Trust Between Services

Services communicating over an internal network without authentication. An
attacker who gains access to the internal network can impersonate any service.

**Fix:** Service-to-service authentication (mTLS, service tokens, managed
identities).

## Single Point of Failure in Security Path

All authentication going through a single service with no fallback or circuit
breaking. If that service goes down, either everything is blocked (denial of
service) or auth is bypassed (security failure).

**Fix:** Redundancy for critical security services, fail-closed behavior.

## Insecure Defaults Requiring Opt-In Security

Features that are insecure by default and require developers to remember to
enable security.

**Fix:** Secure by default. Security should be the default behavior that must
be explicitly opted out of with justification.

## Monolithic Auth with No Defense in Depth

A single authorization check at the API gateway with no enforcement in
downstream services.

**Fix:** Authorization at every layer. The gateway check is a first line of
defense, not the only one.
