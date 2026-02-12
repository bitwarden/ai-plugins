---
name: detecting-secrets
description: This skill should be used when the user asks to "find hardcoded secrets", "audit for credential leaks", "check for API keys in code", "review secret scanning alerts", "rotate a leaked secret", or needs to detect hardcoded credentials, review secret handling patterns, or remediate exposed secrets.
---

## Secret Patterns

Look for these categories of hardcoded secrets in code:

### High-Confidence Patterns

| Type               | Example Patterns                                                                                                        |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| API Keys           | `AKIA[0-9A-Z]{16}` (AWS), `AIza[0-9A-Za-z_-]{35}` (Google), strings assigned to variables named `*apiKey*`, `*api_key*` |
| Connection Strings | `Server=...;Password=...`, `mongodb://user:pass@host`, `postgres://user:pass@host`                                      |
| Private Keys       | `-----BEGIN RSA PRIVATE KEY-----`, `-----BEGIN OPENSSH PRIVATE KEY-----`                                                |
| Tokens             | `ghp_[A-Za-z0-9]{36}` (GitHub PAT), `xoxb-` (Slack bot), `sk-` (OpenAI)                                                 |
| Passwords          | Values assigned to variables named `*password*`, `*passwd*`, `*secret*`, `*credential*`                                 |
| Certificates       | PFX/P12 files with embedded passwords, PEM files with private keys                                                      |

### Lower-Confidence Patterns (Require Context)

- Base64-encoded strings in configuration (may be encrypted or may be cleartext secrets)
- JWT tokens (may be test tokens or production tokens)
- Hex strings of 32+ characters (may be encryption keys or hashes)
- URLs with embedded credentials (`https://user:pass@host`)

## Context-Aware Detection

Distinguish real secrets from false positives. Not every pattern match indicates an actual secret — consider context:

### Test Fixtures and Mock Data

```csharp
// NOT a real secret — test fixture with obvious fake value
var testApiKey = "test-api-key-not-real-12345";
var mockPassword = "P@ssword123"; // Used only in unit tests

// REAL secret — production-looking value in non-test code
var apiKey = "sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx";
```

**Decision criteria:**

- Is it in a test directory (`**/test/**`, `**/tests/**`, `**/*.Test/**`)?
- Does the value contain obvious placeholder text ("test", "fake", "mock", "example", "placeholder")?
- Is the value used in assertions or mock setups?

### Example and Placeholder Values

```json
// NOT a real secret — documented example
{
  "apiKey": "YOUR_API_KEY_HERE"
}

// REAL secret — actual value in config
{
  "apiKey": "sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx"
}
```

### Encrypted or Hashed Values

- Hashed passwords (bcrypt `$2b$`, argon2 `$argon2id$`) are NOT secrets — they're properly stored
- Encrypted values with proper key management are NOT secrets in the same way
- But the encryption KEY itself, if hardcoded, IS a secret

## Common Hiding Spots

Search these locations when auditing for secrets:

| Location                                            | What to Look For                                           |
| --------------------------------------------------- | ---------------------------------------------------------- |
| `appsettings.json` / `appsettings.Development.json` | Connection strings, API keys, service credentials          |
| `.env` / `.env.local`                               | Environment variable definitions with real values          |
| `web.config` / `app.config`                         | Machine keys, connection strings                           |
| `docker-compose.yml` / `Dockerfile`                 | `ENV` directives with credentials, build args with secrets |
| CI/CD files (`.github/workflows/*.yml`)             | Inline secrets instead of `${{ secrets.* }}` references    |
| Test seed scripts / migration files                 | Database passwords, service account credentials            |
| Comments and TODO notes                             | "Temporary" credentials left in comments                   |
| Default parameter values                            | `function connect(password = "admin123")`                  |
| Constants files                                     | Centralized credential definitions                         |

## GitHub Secret Scanning Integration

```bash
# List all secret scanning alerts
gh api /repos/{owner}/{repo}/secret-scanning/alerts --jq '.[] | {number, state, secret_type, secret_type_display_name, created_at, push_protection_bypassed}'

# Get details for a specific alert
gh api /repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}

# List alerts that bypassed push protection
gh api "/repos/{owner}/{repo}/secret-scanning/alerts?state=open" --jq '.[] | select(.push_protection_bypassed == true)'
```

**Push protection** prevents commits containing detected secrets from being pushed. When someone bypasses push protection, the alert is flagged — review these with extra scrutiny.

## Remediation Workflow

When a secret is found in code, follow this sequence:

### 1. Rotate Immediately

Assume any committed secret is compromised. Even if the repo is private, the secret may have been cached, logged, or accessed by CI/CD systems.

- Revoke the existing credential
- Generate a new credential
- Update the credential wherever it's used (services, deployments)

### 2. Remove from Code

Replace the hardcoded secret with a secure reference:

```csharp
// WRONG — hardcoded secret
var connectionString = "Server=prod.db;Password=s3cr3t!";

// CORRECT — environment variable
var connectionString = Environment.GetEnvironmentVariable("DB_CONNECTION_STRING");

// CORRECT — Azure Key Vault (Bitwarden's approach)
var connectionString = await keyVaultClient.GetSecretAsync("db-connection-string");
```

### 3. Remove from Git History (If Needed)

If the secret was committed to a public repo or a repo that will become public:

```bash
# Using git filter-repo (preferred over filter-branch)
git filter-repo --path-glob '*.json' --replace-text expressions.txt

# expressions.txt format:
# literal:the-secret-value==>REDACTED
```

**Warning:** Rewriting git history is destructive and affects all collaborators. Only do this when the secret was exposed in a public or soon-to-be-public repository.

### 4. Prevent Recurrence

- Add patterns to `.gitignore` for files that should never be committed (`.env`, `*.pfx`, `appsettings.Development.json`)
- Enable GitHub push protection for the repository
- Use secret scanning custom patterns for organization-specific secret formats

## Secure Alternatives

Bitwarden uses Azure Key Vault for secrets management, provisioned by the BRE team:

| Instead Of                      | Use                                            |
| ------------------------------- | ---------------------------------------------- |
| Hardcoded connection strings    | Azure Key Vault secrets                        |
| API keys in config files        | Environment variables set at deployment        |
| Certificates in source          | Azure Key Vault certificates                   |
| Shared team credentials in code | Managed identities (Azure)                     |
| Secrets in CI/CD workflow files | GitHub Actions secrets (`${{ secrets.NAME }}`) |

For local development, use user-secrets or `.env` files that are `.gitignore`d — never commit them.

## Critical Rules

- **Assume any committed secret is compromised.** Always rotate, even if the repo is private. No exceptions.
- **Never suppress secret scanning alerts without rotation.** Dismissing an alert doesn't make the exposure go away.
- **Validation, not just detection.** When a potential secret is found, verify it's real before raising an alarm. Check if it's a test value, placeholder, or encrypted content.
- **Check the full commit history.** A secret removed in the latest commit may still exist in git history. Use `git log -p -S "secret-pattern"` to search history.
- **Bitwarden uses Azure Key Vault** for secrets management. If a new secret needs to be stored, work with BRE to provision vault access for the repository.

## Further Reading

- [GitHub Secret Scanning Documentation](https://docs.github.com/en/code-security/secret-scanning)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [git-filter-repo Documentation](https://github.com/newren/git-filter-repo)
