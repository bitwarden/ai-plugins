# STRIDE Framework

Use STRIDE as a guide for structured threat identification. Some vulnerabilities
won't map cleanly to STRIDE — that's expected.

| Category                   | Question to Ask                                    | Example Threats                                               | Typical Mitigations                                      |
| -------------------------- | -------------------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------- |
| **Spoofing**               | Can an attacker impersonate a user or component?   | Forged auth tokens, session hijacking, credential stuffing    | Strong authentication, token validation, MFA             |
| **Tampering**              | Can an attacker modify data in transit or at rest? | Man-in-the-middle, database manipulation, parameter tampering | Integrity checks, signed payloads, TLS, input validation |
| **Repudiation**            | Can an attacker deny performing an action?         | Missing audit logs, unsigned transactions                     | Audit logging, digital signatures, timestamps            |
| **Information Disclosure** | Can an attacker access data they shouldn't?        | Verbose errors, insecure storage, side-channel leaks          | Encryption, access controls, error sanitization          |
| **Denial of Service**      | Can an attacker degrade or prevent service?        | Resource exhaustion, algorithmic complexity attacks           | Rate limiting, input size bounds, circuit breakers       |
| **Elevation of Privilege** | Can an attacker gain unauthorized access?          | Broken access control, privilege escalation, IDOR             | Authorization checks at every layer, least privilege     |
