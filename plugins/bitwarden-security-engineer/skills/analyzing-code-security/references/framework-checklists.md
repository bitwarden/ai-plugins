# Security Framework Checklists

Reference tables for OWASP Top 10, API Top 10, Mobile Top 10, and CWE Top 25. Consult these when mapping findings to specific framework categories.

## OWASP Web Top 10

| #   | Category                  | What to Look For                                                                   |
| --- | ------------------------- | ---------------------------------------------------------------------------------- |
| A01 | Broken Access Control     | Missing authorization checks, IDOR, path traversal, CORS misconfiguration          |
| A02 | Cryptographic Failures    | Weak algorithms, hardcoded keys, missing encryption, cleartext transmission        |
| A03 | Injection                 | SQL, NoSQL, OS command, LDAP, XPath injection via unsanitized input                |
| A04 | Insecure Design           | Missing threat model, business logic flaws, insufficient rate limiting             |
| A05 | Security Misconfiguration | Default credentials, unnecessary features enabled, verbose errors, missing headers |
| A06 | Vulnerable Components     | Outdated libraries, unpatched dependencies, known CVEs                             |
| A07 | Auth Failures             | Weak passwords, missing brute-force protection, insecure session management        |
| A08 | Data Integrity Failures   | Insecure deserialization, unsigned updates, untrusted CI/CD pipelines              |
| A09 | Logging Failures          | Missing audit logs, sensitive data in logs, no alerting                            |
| A10 | SSRF                      | User-controlled URLs in server-side requests, metadata endpoint access             |

## OWASP API Top 10

| #     | Category                                        | What to Look For                                                         |
| ----- | ----------------------------------------------- | ------------------------------------------------------------------------ |
| API1  | Broken Object Level Authorization               | Missing per-object auth checks, IDOR via API parameters                  |
| API2  | Broken Authentication                           | Weak token generation, missing token validation, insecure password flows |
| API3  | Broken Object Property Level Auth               | Mass assignment, excessive data in responses                             |
| API4  | Unrestricted Resource Consumption               | Missing rate limits, unbounded queries, large payload acceptance         |
| API5  | Broken Function Level Authorization             | Missing role checks on admin endpoints, privilege escalation             |
| API6  | Unrestricted Access to Sensitive Business Flows | No bot protection on critical flows (registration, purchase)             |
| API7  | SSRF                                            | Server-side requests with user-controlled URLs                           |
| API8  | Security Misconfiguration                       | Missing security headers, CORS wildcard, verbose errors                  |
| API9  | Improper Inventory Management                   | Undocumented endpoints, old API versions still active                    |
| API10 | Unsafe Consumption of APIs                      | Trusting third-party API responses without validation                    |

## OWASP Mobile Top 10 (2024)

| #   | Category                         | What to Look For                                             |
| --- | -------------------------------- | ------------------------------------------------------------ |
| M1  | Improper Credential Usage        | Hardcoded credentials, insecure credential storage on device |
| M2  | Inadequate Supply Chain Security | Unverified third-party SDKs, tampered libraries              |
| M3  | Insecure Auth/Authorization      | Client-side auth bypasses, missing server-side validation    |
| M4  | Insufficient I/O Validation      | Missing input validation, injection via intents/deep links   |
| M5  | Insecure Communication           | Cleartext traffic, certificate pinning bypass, weak TLS      |
| M6  | Inadequate Privacy Controls      | Excessive data collection, missing consent, PII leakage      |
| M7  | Insufficient Binary Protections  | No obfuscation, debuggable builds in production              |
| M8  | Security Misconfiguration        | Excessive permissions, insecure default settings             |
| M9  | Insecure Data Storage            | Sensitive data in plaintext files, shared preferences, logs  |
| M10 | Insufficient Cryptography        | Weak algorithms, improper key management, predictable IVs    |

## CWE Top 25

The most critical software weaknesses. Map findings to these when applicable:

- **CWE-787** Out-of-bounds Write
- **CWE-79** Cross-site Scripting (XSS)
- **CWE-89** SQL Injection
- **CWE-416** Use After Free
- **CWE-78** OS Command Injection
- **CWE-20** Improper Input Validation
- **CWE-125** Out-of-bounds Read
- **CWE-22** Path Traversal
- **CWE-352** Cross-Site Request Forgery (CSRF)
- **CWE-434** Unrestricted File Upload
- **CWE-862** Missing Authorization
- **CWE-476** NULL Pointer Dereference
- **CWE-287** Improper Authentication
- **CWE-190** Integer Overflow
- **CWE-502** Deserialization of Untrusted Data
- **CWE-77** Command Injection
- **CWE-119** Buffer Overflow
- **CWE-798** Hardcoded Credentials
- **CWE-918** Server-Side Request Forgery (SSRF)
- **CWE-306** Missing Authentication for Critical Function
