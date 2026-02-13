---
name: analyzing-code-security
description: This skill should be used when the user asks to "analyze code for security issues", "check for OWASP vulnerabilities", "review code against CWE Top 25", "find injection vulnerabilities", "do a security code review", or needs manual security analysis against OWASP Top 10, API Top 10, Mobile Top 10, or CWE/SANS frameworks.
---

## Security Review Workflow

Follow these steps when conducting a manual security code review:

1. **Identify the attack surface.** Determine entry points: API endpoints, message handlers, file parsers, user-facing forms. Read route definitions and controller registrations to build a map.
2. **Trace data flows from sources to sinks.** Follow untrusted input (HTTP parameters, headers, request bodies, file uploads, external API responses) through all transformations to dangerous operations (database queries, command execution, HTML rendering, file system access).
3. **Check trust boundary crossings.** At every point where data crosses a trust boundary (client→server, service→service, user input→database), verify that validation, authentication, and authorization are enforced.
4. **Apply framework checklists.** Consult `references/framework-checklists.md` for OWASP Web/API/Mobile Top 10 and CWE Top 25. Check each applicable category against the code under review.
5. **Adopt an adversarial mindset.** Form a hypothesis (e.g., "I can bypass SSO", "I can access another user's vault") and work backwards to determine what conditions would make it exploitable.
6. **Map findings to CWE IDs.** Every finding must include the specific CWE identifier, the code location, and the data flow that makes it exploitable.
7. **Classify by practical exploitability.** Distinguish between practically exploitable vulnerabilities and theoretical risks. Prioritize accordingly but document both.

## Key Vulnerability Categories

The most frequently encountered categories across Bitwarden's stack:

- **Injection** (CWE-89, CWE-78, CWE-77) — Unsanitized input reaching SQL queries, OS commands, or LDAP queries. Always use parameterized queries and avoid string concatenation.
- **Broken Access Control** (CWE-862, CWE-287, CWE-306) — Missing authorization checks, IDOR, privilege escalation. Verify per-object ownership checks and role enforcement at every layer.
- **XSS** (CWE-79) — User input rendered in HTML without encoding. In Angular, avoid `innerHTML` and `bypassSecurityTrust*` with untrusted content.
- **SSRF** (CWE-918) — User-controlled URLs in server-side requests. Validate against host allowlists.
- **Insecure Deserialization** (CWE-502) — Type-handling enabled on untrusted input. Avoid `TypeNameHandling.All` in JSON.NET.
- **Path Traversal** (CWE-22) — User-supplied paths reaching file system operations. Canonicalize and validate against a base directory.
- **Cryptographic Failures** — Weak algorithms, hardcoded keys, predictable IVs. See the `reviewing-security-architecture` skill for approved algorithms.

For complete framework checklists (all OWASP and CWE categories), consult **`references/framework-checklists.md`**.

For CORRECT/WRONG code examples in C#, TypeScript, and SQL, consult **`references/vulnerability-patterns.md`**.

## Adversarial Review Mindset

Adopt an adversarial mindset during security code review — this differs from regular code review which seeks to strengthen code.

**How to think adversarially:**

1. **Create a hypothesis** — e.g., "I can bypass SSO", "I can access another user's vault", "I can escalate from member to admin"
2. **Work backwards** — What conditions would need to be true for the attack to succeed? Can those conditions be fabricated?
3. **Question assumptions** — Is that authorization check always reached? What happens if the middleware fails? What if the token is malformed but not invalid?
4. **Consider failure modes** — What happens when things fail? Do they fail open (insecure) or fail closed (secure)?

## Critical Rules

- **Authentication before authorization.** Always verify the user is who they claim to be before checking what they're allowed to do. Never skip auth checks in "internal" endpoints.
- **Validate at trust boundaries.** Every point where data crosses a trust boundary (client→server, service→service, user input→database) must validate. Never trust client-side validation alone.
- **Map findings to CWE IDs.** Every finding must include a specific CWE identifier with evidence: the code location and the data flow that makes it exploitable.
- **Practical over theoretical.** Distinguish between vulnerabilities that are practically exploitable in this system vs. theoretical risks. Prioritize accordingly but document both.
- **Check the whole chain.** A vulnerability isn't just the sink — trace from the source (user input) through all transformations to the sink (dangerous operation). If the chain is broken by sanitization, it's not exploitable.

## Additional Resources

### Reference Files

For detailed checklists and code examples, consult:

- **`references/framework-checklists.md`** — OWASP Web Top 10, API Top 10, Mobile Top 10 (2024), CWE Top 25 lookup tables
- **`references/vulnerability-patterns.md`** — CORRECT/WRONG code examples for C#/.NET, TypeScript/Angular, and SQL
