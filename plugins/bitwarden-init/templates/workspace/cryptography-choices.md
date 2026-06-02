## Cryptography Protecting Vault Data

- **Symmetric:** AES-CBC with 256-bit keys, authenticated with HMAC-SHA-256 — scheme `AES256-CBC-HMAC-SHA256` [4]
- **Asymmetric:** RSA with OAEP padding [4]
- **EK-1 requirement:** _"The UserKey **MUST** have 256 bits of security."_ [5]
