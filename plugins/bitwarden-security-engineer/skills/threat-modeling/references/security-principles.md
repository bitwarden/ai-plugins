# Bitwarden Security Principles (P01-P06)

These six principles form the foundation for all threat modeling at Bitwarden.
Reference them when writing security goals and evaluating threats.

Sourced from [Security Principles](https://contributing.bitwarden.com/architecture/security/principles/).

## Principles

| Principle | Name                                         | Core Guarantee                                                                                                                                                                                                                                       |
| --------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P01**   | Servers are Zero Knowledge                   | Bitwarden infrastructure cannot access unencrypted user data. The server must not enable weakening of user-chosen protections, masquerade server data as user-encrypted content, or access encrypted data outside the client context.                |
| **P02**   | A Locked Vault is Secure                     | Highly sensitive vault data cannot be accessed in plaintext once the vault is locked, even if the device is compromised after locking. Platform limitations (e.g., JS memory) are mitigated through buffer clearing and available security features. |
| **P03**   | Limited Security on Semi-Compromised Devices | For unlocked vaults on devices with userspace malware (but intact OS/kernel), clients maximize kernel/OS-level protections and balance security with usability through controls like biometrics.                                                     |
| **P04**   | No Security on Fully Compromised Systems     | Bitwarden cannot guarantee vault protection when hardware or OS-level integrity is fully compromised. This applies to unlocked vaults only — locked vaults are covered by P02.                                                                       |
| **P05**   | Controlled Access to Vault Data              | Vault data, whether at rest or in use, is accessible only to authorized parties under the user's explicit control. Isolation mechanisms are critical in high-risk environments like web browsers.                                                    |
| **P06**   | Minimized Impact of Security Breaches        | Limit breach scope and duration through session invalidation, key rotation (countering "harvest now, decrypt later"), and post-compromise security (new data remains protected after a breach).                                                      |

## Controlled Exceptions

Principles have documented exceptions. When threat modeling, check the full
[principles documentation](https://contributing.bitwarden.com/architecture/security/principles/)
for current exceptions.

Known examples:

- **P01 — Key Connector**: Self-hosted SSO without passwords. The server holds encryption keys on behalf of the user.
- **P01 — Icons Service**: Plaintext domain names are sent to retrieve favicons.

## Security Requirements

Security requirements define concrete MUST/SHOULD/MAY obligations organized by
category. Reference these when validating that a design satisfies Bitwarden's
security standards.

Full requirements: [Security Requirements](https://contributing.bitwarden.com/architecture/security/requirements)

| Category | Scope                 | Key Obligations                                                                                                                                     |
| -------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **VD**   | Vault Data            | Protected at rest (encrypted with UserKey), allowed in use (decrypted during unlock), trusted channels in transit, export requires informed consent |
| **EK**   | Encryption Keys       | 256-bit security strength, protected at rest and in transit, must never be exported                                                                 |
| **AT**   | Authentication Tokens | Protected storage at rest, mandatory transit protection                                                                                             |
| **SC**   | Secure Channels       | Confidentiality, integrity, replay prevention, forward secrecy for long-lived channels                                                              |
| **TC**   | Trusted Channels      | Secure channel properties plus receiver identity verification                                                                                       |
