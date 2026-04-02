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

- **Controlled Access (P05)**: Vault data access must remain restricted to explicit user actions or authorized contexts (e.g., autofill, user-joined organizations). Check for any new code path that grants access to vault data outside of explicit user control — including paths that could allow one organization member to access another member's vault data, or that expand collection/group access beyond what the user explicitly authorized.
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

## Vulnerability Checklists

For OWASP Web Top 10, API Top 10, Mobile Top 10, and CWE Top 25 reference tables, read `../../analyzing-code-security/references/framework-checklists.md`.
