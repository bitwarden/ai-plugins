# Known Feature-to-Repo Mappings

Use these mappings as search priors — which repos to check first — then confirm with `gh search code` or `gh api` before presenting. Never present a mapping that this session did not confirm with a live query.

## Passkeys

Two separate concepts; search for the one the user means:

- **Saved in the vault** (Bitwarden as an authenticator): passkey-rs, sdk-internal, clients, android, ios. The server only stores the encrypted cipher.
- **Logging in to Bitwarden** (WebAuthn): server, clients, sdk-internal.

## Passwordless.dev

A separate product (passwordless-server and its client SDKs), not the vault passkey feature.
