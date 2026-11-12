## Cryptography Protecting Vault Data

- **Symmetric:** AES-CBC with 256-bit keys, authenticated with HMAC-SHA-256 — scheme `AES256-CBC-HMAC-SHA256` [4]
- **Asymmetric:** RSA with OAEP padding [4]
- **No hand-built crypto:** make and check tokens, signatures and encrypted formats with the vetted library the codebase already uses (`Microsoft.IdentityModel` on the server, the SDK in clients), never composed from primitives, even when the result would be correct. A direct use needs the owning team's agreement before any code.
- **EK-1 requirement:** _"The UserKey **MUST** have 256 bits of security."_ [5]
