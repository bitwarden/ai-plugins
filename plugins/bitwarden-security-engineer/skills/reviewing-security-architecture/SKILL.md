---
name: reviewing-security-architecture
description: This skill should be used when the user asks to "review the security architecture", "check authentication patterns", "evaluate trust boundaries", "review encryption implementation", "assess authorization design", or needs to evaluate system designs for authentication, authorization, data protection, or cryptographic correctness.
---

## Authentication Architecture

### Token Handling

Review these aspects of token-based authentication:

| Aspect               | Secure Pattern                                                    | Anti-Pattern                                                           |
| -------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **Issuance**         | Short-lived tokens with refresh mechanism                         | Long-lived tokens that never expire                                    |
| **Validation**       | Validate signature, issuer, audience, and expiry on every request | Validate only the signature, or skip validation for "internal" calls   |
| **Storage (server)** | Stateless JWT or server-side session store                        | Token stored in querystring or URL                                     |
| **Storage (client)** | HttpOnly Secure cookies or secure platform storage                | localStorage, sessionStorage, or cookies without HttpOnly/Secure flags |
| **Refresh**          | Refresh token rotation (old refresh token invalidated on use)     | Reusable refresh tokens with no rotation                               |
| **Revocation**       | Token blocklist or short expiry + refresh rotation                | No revocation mechanism for compromised tokens                         |

### Session Management

- Server-side sessions should have absolute timeouts (maximum session duration) and idle timeouts
- Session identifiers must be cryptographically random and sufficiently long (128+ bits of entropy)
- Regenerate session ID after authentication state changes (login, privilege escalation)
- Bind sessions to client properties where possible (IP range, user agent) for anomaly detection

### Credential Storage

- Passwords must be hashed with a modern KDF: Argon2id (preferred), bcrypt, or PBKDF2 with high iteration count
- Never use MD5, SHA-1, or SHA-256 alone for password hashing (too fast, no salt by default)
- Salt must be unique per credential, cryptographically random, at least 128 bits
- Consider pepper (application-level secret added to hash input) for defense in depth

## Authorization Patterns

### Role-Based Access Control (RBAC)

```csharp
// CORRECT — explicit role check at the API layer
[Authorize(Roles = "Admin")]
public async Task<IActionResult> DeleteUser(Guid userId)

// WRONG — checking role in business logic with string comparison
if (currentUser.Role == "admin") // Fragile, case-sensitive, easy to bypass
```

### Object-Level Authorization

```csharp
// WRONG — trusts the userId from the route, no ownership check
public async Task<Cipher> GetCipher(Guid cipherId) {
    return await _cipherRepository.GetByIdAsync(cipherId);
}

// CORRECT — verify the requesting user owns the resource
public async Task<Cipher> GetCipher(Guid cipherId) {
    var cipher = await _cipherRepository.GetByIdAsync(cipherId);
    if (cipher.UserId != _currentContext.UserId)
        throw new NotFoundException();
    return cipher;
}
```

### Authorization Principles

- **Check at every layer.** API controller, service layer, and data access should all enforce authorization. Don't rely on a single checkpoint.
- **Least privilege.** Grant the minimum permissions needed. Default to deny.
- **Fail closed.** If an authorization check fails or throws an exception, deny access. Never fail open.
- **Don't trust client-side authorization.** UI visibility controls are UX, not security. Always enforce server-side.

## Data Protection

### Encryption at Rest

- All sensitive data must be encrypted at rest using AES-256 or equivalent
- Encryption keys must be stored separately from encrypted data (never in the same database)
- Use envelope encryption: data encrypted with a data encryption key (DEK), DEK encrypted with a key encryption key (KEK) in a key management system
- Bitwarden's end-to-end encryption ensures vault data is encrypted before leaving the client

### Encryption in Transit

- TLS 1.2 minimum, TLS 1.3 preferred
- Disable older protocols (SSL 3.0, TLS 1.0, TLS 1.1)
- Use strong cipher suites (ECDHE for key exchange, AES-GCM for encryption)
- Certificate pinning for mobile apps where appropriate
- Internal service-to-service communication should also use TLS

### Data Classification

When reviewing architecture, identify data by classification:

| Classification   | Examples                                      | Required Protection                             |
| ---------------- | --------------------------------------------- | ----------------------------------------------- |
| **Critical**     | Encryption keys, master passwords, vault data | End-to-end encryption, HSM key storage          |
| **Confidential** | PII, email addresses, billing info            | Encryption at rest + in transit, access logging |
| **Internal**     | Organizational settings, feature flags        | Encryption in transit, role-based access        |
| **Public**       | Marketing content, public API docs            | Integrity protection                            |

## Trust Boundaries

A trust boundary exists wherever data crosses between components with different levels of trust. Every crossing must be validated.

### Common Trust Boundaries

```
Client ←→ API Gateway         (user-controlled → server-controlled)
API Gateway ←→ Backend Service (internet-facing → internal)
Backend Service ←→ Database    (application → data store)
Service ←→ External API        (internal → third-party)
Browser ←→ Browser Extension   (page context → extension context)
Main Thread ←→ Web Worker      (different execution contexts)
```

### Validation at Trust Boundaries

At each boundary crossing:

1. **Validate all input** — type, format, range, length. Don't trust upstream validation.
2. **Authenticate the caller** — verify identity before processing requests.
3. **Authorize the action** — verify the caller has permission for this specific operation.
4. **Sanitize output** — encode/escape data appropriate to the destination context.
5. **Log the crossing** — security-relevant boundary crossings should be auditable.

### Zero-Trust Principles

- Don't trust internal network location as a proxy for authentication
- Every service-to-service call should be authenticated and authorized
- Assume the network is compromised — encrypt all internal communication
- Validate data from internal services just as rigorously as external input

## Cryptographic Patterns

### Algorithm Selection

| Use Case              | Recommended                                                     | Deprecated / Avoid                      |
| --------------------- | --------------------------------------------------------------- | --------------------------------------- |
| Symmetric encryption  | AES-256-GCM, ChaCha20-Poly1305                                  | DES, 3DES, AES-ECB, Blowfish            |
| Hashing               | SHA-256, SHA-384, SHA-512, BLAKE2                               | MD5, SHA-1                              |
| Password hashing      | Argon2id, bcrypt, PBKDF2 (high iterations)                      | MD5, SHA-\*, plain bcrypt with low cost |
| Asymmetric encryption | RSA-OAEP (2048+ bits), ECIES                                    | RSA-PKCS1v1.5, RSA < 2048 bits          |
| Digital signatures    | Ed25519, ECDSA P-256, RSA-PSS                                   | RSA-PKCS1v1.5, DSA                      |
| Key exchange          | ECDH P-256, X25519                                              | DH with small primes                    |
| Random generation     | `RandomNumberGenerator` (.NET), `crypto.getRandomValues()` (JS) | `Math.random()`, `System.Random`        |

### Common Crypto Anti-Patterns

```csharp
// WRONG — ECB mode (reveals patterns in plaintext)
var aes = Aes.Create();
aes.Mode = CipherMode.ECB;

// CORRECT — GCM mode (authenticated encryption)
var aesGcm = new AesGcm(key);
```

```csharp
// WRONG — predictable IV
var iv = new byte[16]; // All zeros

// CORRECT — random IV for each encryption operation
var iv = RandomNumberGenerator.GetBytes(16);
```

```typescript
// WRONG — Math.random() for security-sensitive values
const token = Math.random().toString(36);

// CORRECT — cryptographic random
const token = crypto.getRandomValues(new Uint8Array(32));
```

## Architectural Anti-Patterns

### Implicit Trust Between Services

Services communicating over an internal network without authentication. An attacker who gains access to the internal network can impersonate any service.

**Fix:** Service-to-service authentication (mTLS, service tokens, managed identities).

### Single Point of Failure in Security Path

All authentication going through a single service with no fallback or circuit breaking. If that service goes down, either everything is blocked (denial of service) or auth is bypassed (security failure).

**Fix:** Redundancy for critical security services, fail-closed behavior.

### Insecure Defaults Requiring Opt-In Security

Features that are insecure by default and require developers to remember to enable security.

**Fix:** Secure by default. Security should be the default behavior that must be explicitly opted out of with justification.

### Monolithic Auth with No Defense in Depth

A single authorization check at the API gateway with no enforcement in downstream services.

**Fix:** Authorization at every layer. The gateway check is a first line of defense, not the only one.

## Connection to Threat Modeling

Architecture security review directly feeds into the threat modeling process:

- **Trust boundary identification** informs where to draw boundaries in data flow diagrams
- **Architectural weaknesses** become threats in the threat catalog
- **Security properties** (auth, encryption, access control) map to security goals in security definitions
- **Anti-patterns found** become candidates for Bitwarden's engagement model Phase 1 initial security assessment

When conducting architecture review, consider whether the findings warrant engaging the AppSec team (#team-eng-appsec) for a full threat modeling session.
