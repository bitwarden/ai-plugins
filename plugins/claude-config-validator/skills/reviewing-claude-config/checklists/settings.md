# Settings Review Checklist

Review checklist for changes to `.claude/settings.json` and `.claude/settings.local.json`.

---

## CRITICAL SECURITY CHECK

<thinking>
CRITICAL security considerations:
1. Is settings.local.json committed to git?
2. Are there hardcoded credentials or secrets?
3. Are file permissions overly broad?
4. Are command auto-approvals safe?
</thinking>

**Before anything else, verify:**

- [ ] **settings.local.json is NOT committed to git**
- [ ] **No hardcoded API keys, tokens, or passwords**
- [ ] **No sensitive paths exposed in permissions**
- [ ] **No dangerous command auto-approvals**

**If ANY of these fail, FLAG IMMEDIATELY as CRITICAL and stop review.**

---

## Multi-Pass Review Strategy

### First Pass: Committed Settings Detection

**CRITICAL SECURITY ISSUE: settings.local.json in git**

`settings.local.json` must NEVER be committed. It contains user-specific and potentially sensitive configuration.

**Detection:**
Check if `settings.local.json` appears in changed files list. If present in git diff or PR, this is CRITICAL.

**Fix:**
```bash
# Remove from git but keep locally
git rm --cached .claude/settings.local.json

# Ensure .gitignore includes it
echo ".claude/settings.local.json" >> .gitignore
```

**Rationale:** Local settings may contain:
- User-specific file paths
- API keys or tokens
- Personal preferences
- Machine-specific configuration

Committing these exposes sensitive data and creates conflicts between users.

---

### Second Pass: Hardcoded Secrets

<thinking>
Secret detection:
1. Are there API keys in plaintext?
2. Are there passwords or tokens?
3. Are there authentication credentials?
4. Should any values be environment variables instead?
</thinking>

**Scan for Common Secret Patterns:**

❌ **CRITICAL ISSUES:**
```json
{
  "apiKey": "sk-1234567890abcdef",
  "password": "mypassword123",
  "token": "ghp_xxxxxxxxxxxx",
  "secret": "shared-secret-value"
}
```

✅ **SAFE ALTERNATIVES:**
```json
{
  "apiKeyVar": "$OPENAI_API_KEY",
  "authMethod": "environment",
  "note": "Set API key in environment: export OPENAI_API_KEY=xxx"
}
```

**Common Secret Patterns:**
- `apiKey`, `api_key`, `API_KEY`
- `password`, `passwd`, `pwd`
- `token`, `auth_token`, `access_token`
- `secret`, `shared_secret`
- Keys starting with `sk-`, `ghp_`, `gho_`, etc.

---

### Third Pass: Permission Scoping

<thinking>
Permission scoping:
1. Are file permissions appropriately limited?
2. Are read permissions scoped to project directories?
3. Are write permissions even more restrictive?
4. Are there any wildcard patterns that are too broad?
</thinking>

**Appropriate Permission Scoping:**

❌ **TOO BROAD:**
```json
{
  "autoApprovedTools": [
    "Read://*",
    "Write://*",
    "Bash:*"
  ]
}
```

✅ **APPROPRIATELY SCOPED:**
```json
{
  "autoApprovedTools": [
    "Read://Users/username/projects/myproject/**",
    "Write://Users/username/projects/myproject/src/**",
    "Bash:git status:*",
    "Bash:npm install:*"
  ]
}
```

**Permission Guidelines:**

**Read Permissions:**
- Scope to project directory and relevant config
- Avoid `Read://*` (entire filesystem)
- Consider what actually needs to be read

**Write Permissions:**
- Even more restrictive than Read
- Limit to source directories, not config or root
- Avoid write access outside project

**Bash Permissions:**
- Specific commands, not `Bash:*`
- Safe operations: `git status`, `npm install`, `./gradlew test`
- NEVER auto-approve: `rm -rf`, `dd`, `chmod 777`, `curl | sh`

---

### Fourth Pass: Command Auto-Approval Safety

<thinking>
Command safety:
1. Are auto-approved commands safe to run?
2. Could they cause data loss or system damage?
3. Are they read-only or idempotent?
4. Should any require explicit approval?
</thinking>

**Safe vs Dangerous Commands:**

✅ **SAFE to auto-approve:**
```json
{
  "autoApprovedTools": [
    "Bash:git status:*",
    "Bash:git log:*",
    "Bash:git diff:*",
    "Bash:./gradlew test:*",
    "Bash:npm install:*",
    "Bash:ls:*"
  ]
}
```

❌ **DANGEROUS - require approval:**
```json
{
  "autoApprovedTools": [
    "Bash:rm -rf:*",        // Data destruction
    "Bash:git push --force:*",  // Destructive git operation
    "Bash:chmod 777:*",     // Security risk
    "Bash:curl * | sh:*",   // Arbitrary code execution
    "Bash:dd:*",            // Low-level disk operations
    "Bash:mkfs:*"           // Filesystem formatting
  ]
}
```

**Safety Criteria:**
- **Read-only operations:** Generally safe (ls, git status, git diff)
- **Idempotent operations:** Safe to run multiple times (npm install, git pull)
- **Destructive operations:** Require approval (rm, force push, formatting)
- **External code execution:** Require approval (curl | sh, wget | bash)

---

### Fifth Pass: JSON Syntax and Structure

<thinking>
Syntax validation:
1. Is the JSON valid (no trailing commas, proper quotes)?
2. Are field names correct (check documentation)?
3. Are values the right type (string vs array vs boolean)?
4. Is the structure logical and organized?
</thinking>

**Common JSON Issues:**

❌ **Syntax errors:**
```json
{
  "autoApprovedTools": [
    "Read://path/**",  // Trailing comma error
  ]
}
```

✅ **Valid JSON:**
```json
{
  "autoApprovedTools": [
    "Read://path/**"
  ]
}
```

**Field Validation:**
- Check field names against Claude Code documentation
- Verify value types (string, boolean, array, object)
- Ensure required fields are present
- Remove unknown or deprecated fields

---

## Priority Classification

Classify findings using `reference/priority-framework.md`:
- **CRITICAL** - Prevents functionality or exposes security vulnerabilities
- **IMPORTANT** - Significantly impacts quality or maintainability
- **SUGGESTED** - Improvements that aren't essential
- **OPTIONAL** - Personal preferences

---
