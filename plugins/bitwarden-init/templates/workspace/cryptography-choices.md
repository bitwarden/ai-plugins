## Cryptography Protecting Vault Data

- **Symmetric:** AES-CBC with 256-bit keys, authenticated with HMAC-SHA-256 — scheme `AES256-CBC-HMAC-SHA256` [4]
- **Asymmetric:** RSA with OAEP padding [4]
- **No hand-built crypto:** make and check tokens, signatures and encrypted formats with the vetted library the codebase already uses (`Microsoft.IdentityModel` for tokens on the server, the SDK for EncStrings and in clients), never composed from primitives, even when the result would be correct. The client SDK's `bitwarden-crypto` crate, which implements the scheme above, and HMAC used as a keyed digest or for key derivation are not hand-built crypto. Hand-building one anyway needs the owning team's agreement before any code, recorded in a comment on the code that says which team agreed and where.
- **EK-1 requirement:** _"The UserKey **MUST** have 256 bits of security."_ [5]
