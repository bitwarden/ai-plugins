# Example Settings Review

**Context:** Reviewing settings.json with multiple security concerns.

### Review Comments

**`.claude/settings.json:5`** - CRITICAL: Overly broad file permissions

Current:

```json
"autoApprovedTools": [
  "Read://*"
]
```

Change to project-scoped:

```json
"autoApprovedTools": [
  "Read://Users/username/projects/myproject/**"
]
```

`Read://*` grants read access to entire filesystem including:

- `~/.ssh/` (SSH keys)
- `~/.aws/` (AWS credentials)
- `/etc/` (system config)
- All user documents and personal files

Scope to project directory only per principle of least privilege.

Reference: Security best practices - Permission scoping

---

**`.claude/settings.json:8`** - CRITICAL: Dangerous command auto-approved

Current:

```json
"Bash:rm -rf:*"
```

**REMOVE THIS IMMEDIATELY**

`rm -rf` performs recursive deletion without confirmation. Auto-approving this command creates risk of accidental data loss.

If file deletion is needed frequently, scope to specific safe directories:

```json
"Bash:rm -rf /tmp/project-build-cache:*"
```

Or require manual approval for all rm commands.

Reference: Security best practices - Dangerous commands

---

**`.claude/settings.json:12`** - IMPORTANT: Permissions reference sensitive directory

Current:

```json
"Read://Users/username/.ssh/**"
```

Remove access to `.ssh` directory containing private keys.

If SSH config reading is required (rare), scope to specific config file:

```json
"Read://Users/username/.ssh/config"
```

Never grant blanket access to directories containing credentials.

---

### Summary Comment

**Overall Assessment:** BLOCK - Critical Security Issues

**CRITICAL issues must be fixed immediately:**

- Overly broad `Read://*` permission
- Auto-approved `rm -rf` command
- Access to `.ssh` directory

These issues expose significant security risks:

- Potential data loss from dangerous commands
- Exposure of SSH private keys and credentials
- Access to sensitive system files

**Cannot approve until all CRITICAL issues are resolved.**

After fixes, re-review the scoped permissions to ensure they follow principle of least privilege.

---
