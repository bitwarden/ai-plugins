## Sources of Truth

The following are the sources that drove the creation of this file. They are here **NOT** to encourage Claude Code to perform ad-hoc web fetches. They are included as points of reference for future refinement — and to ensure we stay current as these references change.

1. **Bitwarden GitHub organization** (product lines and repos) — https://github.com/bitwarden
2. **Security Whitepaper** (zero-knowledge invariant; Master Key handling) — https://bitwarden.com/help/bitwarden-security-white-paper/
3. **Security FAQs** (user-facing client-side encryption claims) — https://bitwarden.com/help/security-faqs/
4. **What encryption is used?** (AES-CBC + HMAC-SHA-256; RSA-OAEP) — https://bitwarden.com/help/what-encryption-is-used/
5. **Security Requirements** (VD/EK/AT/SC/TC catalog; EK-1 256-bit UserKey) — https://contributing.bitwarden.com/architecture/security/requirements
6. P01 Servers are zero knowledge — https://contributing.bitwarden.com/architecture/security/principles/servers-are-zero-knowledge
7. P02 A locked vault is secure — https://contributing.bitwarden.com/architecture/security/principles/locked-vault-is-secure
8. P03 Limited security for vaults on semi-compromised devices — https://contributing.bitwarden.com/architecture/security/principles/limited-security-on-semi-compromised
9. P04 No security on fully compromised systems — https://contributing.bitwarden.com/architecture/security/principles/no-security-on-fully-compromised
10. P05 Controlled access to vault data — https://contributing.bitwarden.com/architecture/security/principles/controlled-access
11. P06 Minimized impact of security breaches — https://contributing.bitwarden.com/architecture/security/principles/minimized-impact-of-security-breaches
