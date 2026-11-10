# Known Feature-to-Repo Mappings

Use these mappings as search priors — which repos and paths to check first — then confirm each path with `gh search code` or `gh api` before presenting it. Never present a mapped path that this session did not confirm; flag any mapped path the search fails to find as possibly moved.

## Passkeys (vault storage)

Bitwarden has two separate passkey concepts:

1. **Passkeys saved in vault** (Bitwarden as a software authenticator):
   - **passkey-rs** — Core WebAuthn/CTAP2 protocol engine (Rust)
   - **sdk-internal** → `crates/bitwarden-fido/` — Bridge layer to Bitwarden vault
   - **clients** → `apps/browser/src/autofill/fido2/`, `libs/common/src/platform/services/fido2/`
   - **android** and **ios** — consume SDK via UniFFI bindings
   - **server** — stores encrypted cipher only

2. **Passkeys for Bitwarden account login** (WebAuthn):
   - **server** → `src/Api/Auth/Controllers/WebAuthnController.cs`
   - **clients** → `apps/browser/src/auth/`
   - **sdk-internal** → `crates/bitwarden-fido/src/device_auth_key.rs`

## Passwordless.dev (separate product)

- **passwordless-server**, **passwordless-client-js**, **passwordless-dotnet**, **passwordless-java**, **passwordless-python** — separate Bitwarden product, not the vault passkey feature
