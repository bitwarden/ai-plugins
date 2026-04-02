# Security Review Rubric

The rubric grounds specialized analysis agents during security review.

## Bitwarden Security Invariants

Invoke `Skill(bitwarden-security-context)` for the full security principles (P01–P06), vocabulary, and data classification standards. The invariants below are the non-negotiable rules derived from that context — any violation is automatically 🔴 CRITICAL severity.

### Core Invariants

1. **Zero-knowledge invariant**: Encryption and decryption happen client-side only. The server MUST never have access to plaintext vault data.
2. **Vault Data protection**: Passwords, usernames, secure notes, credit cards, identities, and attachments must always be encrypted before leaving the client.
3. **Key material**: The UserKey MUST NOT be exported. It must be protected at rest and in transit. (EK)
4. **Data Exporting**: Any operation that causes vault data to leave Bitwarden unprotected requires explicit, informed user consent.
5. **Secure Channel requirement**: All communication containing vault data must use at minimum a Secure Channel (confidentiality + integrity). A Trusted Channel (adds receiver identity verification) is required where authenticity of the receiving party must be guaranteed. (SC/TC)

### Bitwarden-Specific Code Patterns

- **Controlled Access (P05)**: Vault data access must remain restricted to explicit user actions or authorized contexts (e.g., autofill). Check for any new code path that grants access to vault data outside of explicit user control.
- **Data Leaking (Definitions)**: Any unintentional departure of vault data from the Bitwarden secure environment is a leak. Check that vault data values, encryption keys, and metadata are not written to logs, error messages, telemetry, or any unprotected output channel.

## Severity × Confidence Threshold Matrix

|                 | HIGH Confidence | MEDIUM Confidence | LOW Confidence |
| --------------- | --------------- | ----------------- | -------------- |
| **🔴 CRITICAL** | 🚨 Blocker      | ⚠️ Improvement    | 📝 Note        |
| **🟠 HIGH**     | 🚨 Blocker      | ⚠️ Improvement    | ❌ Dismiss     |
| **🟡 MEDIUM**   | ⚠️ Improvement  | 📝 Note           | ❌ Dismiss     |
| **🔵 LOW**      | 📝 Note         | 📝 Note           | ❌ Dismiss     |
| **⚪ INFO**     | 📝 Note         | ❌ Dismiss        | ❌ Dismiss     |

### Severity Definitions

| Severity    | Meaning                                                                                | Examples                                                     |
| ----------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 🔴 CRITICAL | Immediate exploitation risk; vault data exposure or zero-knowledge invariant violation | SQLi, RCE, auth bypass, plaintext vault data reaching server |
| 🟠 HIGH     | Serious vulnerability, exploit path exists                                             | XSS, IDOR, hardcoded secrets, privilege escalation           |
| 🟡 MEDIUM   | Exploitable with conditions or through chaining                                        | CSRF, open redirect, weak crypto, defense-in-depth failure   |
| 🔵 LOW      | Best practice violation, low direct risk                                               | Verbose errors, missing headers, hardening opportunity       |
| ⚪ INFO     | Observation worth noting, not a vulnerability                                          | Outdated dependency (no CVE), advisory note                  |

### Confidence Definitions

- **HIGH**: Evidence directly supports the finding; not a pre-existing issue
- **MEDIUM**: Likely real but may have mitigating context not visible in the diff
- **LOW**: Speculative; probable false positive

---

## OWASP Top 10 2025 Checklist

### A01:2025 — Broken Access Control

- Missing authorization checks on new endpoints or functions
- Insecure Direct Object References (IDOR) — user-controlled IDs without ownership verification
- Privilege escalation paths — lower-privilege user accessing higher-privilege resources
- CORS misconfiguration allowing unauthorized origins
- Force-browsing to restricted pages or API routes

### A02:2025 — Security Misconfiguration

- Debug mode or verbose error messages in production paths
- Default credentials or tokens committed or hardcoded
- Unnecessary features or endpoints enabled
- Missing security headers (CSP, HSTS, X-Frame-Options)

### A03:2025 — Software Supply Chain Failures

- Direct or transitive dependencies with known CVEs
- Unpinned or overly permissive version ranges (`^`, `~`, `*`)
- Unverified package integrity — no checksum or signature validation
- Malicious or typosquatted package names
- Build pipeline steps that pull unverified external content

### A04:2025 — Cryptographic Failures

- Sensitive data transmitted without TLS/HTTPS
- Weak or deprecated algorithms (MD5, SHA1, DES, RC4, ECB mode)
- Hardcoded or predictable encryption keys
- Missing encryption for sensitive data at rest
- Insufficient key length or entropy

### A05:2025 — Injection

- SQL injection — user input concatenated into queries without parameterization
- Command injection — user input passed to shell execution
- XSS — user input rendered to HTML without escaping
- LDAP, XPath, NoSQL injection patterns
- Template injection in server-side rendering

### A06:2025 — Insecure Design

- Missing rate limiting on sensitive operations
- Business logic flaws — sequence bypass, negative values, quantity manipulation
- Insufficient input validation at system boundaries
- Insecure defaults requiring opt-in to secure configuration

### A07:2025 — Authentication Failures

- Weak session token generation (insufficient entropy)
- Session fixation — reusing session ID across privilege levels
- Missing session expiration or invalidation on logout
- Brute-force protections absent on authentication endpoints
- Insecure credential storage (plaintext, reversible encoding)

### A08:2025 — Software or Data Integrity Failures

- Deserialization of untrusted data without integrity checks
- Missing signature verification on updates or plugins
- Insecure CI/CD pipeline steps with unvalidated inputs
- Unverified external content loaded and executed

### A09:2025 — Security Logging and Alerting Failures

- Missing audit logs for sensitive operations (auth events, data access, admin actions)
- PII or secrets logged in plaintext
- No alerting on repeated security failures or anomalous patterns
- Log injection — user input written to logs without sanitization

### A10:2025 — Mishandling of Exceptional Conditions

- Unhandled exceptions exposing stack traces or internal state in responses
- Silent error swallowing that hides security-relevant failures
- Exception-based control flow that can be triggered to bypass logic
- Resource leaks (file handles, connections, memory) from unhandled errors
- Inconsistent error handling that creates exploitable behavioral differences
