---
name: analyzing-code-security
description: This skill should be used when the user asks to "analyze code for security issues", "check for OWASP vulnerabilities", "review code against CWE Top 25", "find injection vulnerabilities", "do a security code review", or needs manual security analysis against OWASP Top 10, API Top 10, Mobile Top 10, or CWE/SANS frameworks.
---

## Frameworks Reference

### OWASP Web Top 10

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

### OWASP API Top 10

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

### OWASP Mobile Top 10 (2024)

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

### CWE Top 25

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

## Language-Specific Vulnerability Patterns

### C# / .NET

```csharp
// WRONG — SQL injection via string concatenation
var query = $"SELECT * FROM Users WHERE Id = '{userId}'";
var result = connection.Execute(query);

// CORRECT — parameterized query
var query = "SELECT * FROM Users WHERE Id = @UserId";
var result = connection.Execute(query, new { UserId = userId });
```

```csharp
// WRONG — insecure deserialization with type handling
JsonConvert.DeserializeObject<object>(input, new JsonSerializerSettings {
    TypeNameHandling = TypeNameHandling.All
});

// CORRECT — no type name handling on untrusted input
JsonConvert.DeserializeObject<ExpectedType>(input);
```

```csharp
// WRONG — path traversal via user input
var filePath = Path.Combine(baseDir, userInput);
var content = File.ReadAllText(filePath);

// CORRECT — canonicalize and validate
var filePath = Path.GetFullPath(Path.Combine(baseDir, userInput));
if (!filePath.StartsWith(Path.GetFullPath(baseDir)))
    throw new UnauthorizedAccessException();
var content = File.ReadAllText(filePath);
```

```csharp
// WRONG — SSRF via user-controlled URL
var response = await httpClient.GetAsync(userProvidedUrl);

// CORRECT — validate against allowlist
var uri = new Uri(userProvidedUrl);
if (!AllowedHosts.Contains(uri.Host))
    throw new ArgumentException("Host not allowed");
var response = await httpClient.GetAsync(uri);
```

```csharp
// WRONG — XXE via default XML settings
var doc = new XmlDocument();
doc.LoadXml(userInput);

// CORRECT — disable DTD and external entities
var doc = new XmlDocument();
doc.XmlResolver = null;
doc.LoadXml(userInput);
```

### TypeScript / Angular

```typescript
// WRONG — XSS via innerHTML
element.innerHTML = userInput;

// CORRECT — use framework text binding
// In Angular templates: {{ userInput }} (auto-escaped)
// Or use DomSanitizer with explicit trust only for known-safe content
```

```typescript
// WRONG — bypassing Angular security without justification
this.sanitizer.bypassSecurityTrustHtml(userInput);

// CORRECT — only bypass for content you fully control
const trustedContent = this.generateSafeHtml(); // no user input
this.sanitizer.bypassSecurityTrustHtml(trustedContent);
```

```typescript
// WRONG — open redirect
window.location.href = params.get("redirect");

// CORRECT — validate redirect target
const redirect = params.get("redirect");
const url = new URL(redirect, window.location.origin);
if (url.origin !== window.location.origin) {
  throw new Error("Invalid redirect");
}
window.location.href = url.toString();
```

```typescript
// WRONG — insecure postMessage (no origin check)
window.addEventListener("message", (event) => {
  processData(event.data);
});

// CORRECT — validate origin
window.addEventListener("message", (event) => {
  if (event.origin !== "https://expected-origin.com") return;
  processData(event.data);
});
```

### SQL

```sql
-- WRONG — dynamic SQL with concatenation
EXECUTE('SELECT * FROM Users WHERE Name = ''' + @Name + '''');

-- CORRECT — parameterized dynamic SQL
EXECUTE sp_executesql N'SELECT * FROM Users WHERE Name = @Name', N'@Name NVARCHAR(100)', @Name = @Name;
```

## Adversarial Review Mindset

Bitwarden encourages adopting an adversarial mindset during security code review — this is different from regular code review which seeks to strengthen code.

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

## Further Reading

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [OWASP Mobile Top 10 2024](https://owasp.org/www-project-mobile-top-10/)
- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html)
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
