---
name: bitwarden-ai-plugins-review-knowledge
description: Institutional knowledge for bitwarden/ai-plugins code reviews. Use BEFORE reviewing ai-plugins PRs to understand repository-specific patterns, architectural constraints, and avoid false positives.
---

# bitwarden/ai-plugins - Code Review Knowledge

## Repository Overview

| Item | Details |
|------|---------|
| **Repository** | [bitwarden/ai-plugins](https://github.com/bitwarden/ai-plugins) |
| **Technology Stack** | Claude Code plugins, YAML configurations, Bash scripts |
| **Primary Languages** | TypeScript, YAML, Bash |
| **Common Issue Categories** | SDK execution models, input validation, plugin manifest registration, repository URL consistency, documentation separation |

## Verified Detection Strategies

_Copy-paste ready commands for catching common issues._

### Version Mismatch Investigation

Before flagging version inconsistencies as errors:

```bash
# Check if other plugins have marketplace vs plugin.json version differences
jq -r '.plugins[] | "\(.name): marketplace=\(.version)"' .claude-plugin/marketplace.json

# For each plugin, compare with plugin.json version
for plugin in plugins/*/; do
  plugin_name=$(basename "$plugin")
  plugin_version=$(jq -r '.version' "$plugin/.claude-plugin/plugin.json" 2>/dev/null)
  echo "$plugin_name: plugin.json=$plugin_version"
done

# If pattern exists (version differences are common), flag as QUESTION not CRITICAL
```

## Failed Attempts (Critical Learnings)

| Issue | Why Missed | Detection Strategy | Review Date | PR Link | Severity |
|-------|------------|-------------------|-------------|---------|----------|
| Repository URLs flagged piecemeal across 3 commits instead of comprehensive single finding | Didn't perform comprehensive grep for ALL occurrences before creating finding. Detection was reactive (file-by-file) instead of proactive (pattern search upfront) | For pattern-based issues (URLs, versions, naming), perform repository-wide search FIRST with grep. Create ONE comprehensive finding listing ALL locations. Prevents multiple fix iterations. | 2025-11-14 | [#9](https://github.com/bitwarden/ai-plugins/pull/9) | ⚠️ MODERATE |
| Version mismatch between marketplace.json and plugin.json flagged as CRITICAL when intentional | Didn't understand semantic difference: marketplace version tracks marketplace schema, plugin version tracks plugin lifecycle. Applied generic rule without checking repository patterns | Before flagging version mismatches, check if other plugins have similar patterns. If uncertain, frame as QUESTION not CRITICAL. Severity should reflect certainty. | 2025-11-14 | [#9](https://github.com/bitwarden/ai-plugins/pull/9) | ⚠️ MODERATE |

## Repository Gotchas

_Architectural patterns and conventions specific to this repository._

### Repository URL Consistency Enforcement

**Category**: Documentation Quality

**Pattern**: All repository URLs across plugin metadata, documentation, and examples must use current repository name (ai-plugins), not legacy names (ai-marketplace).

**Common Mistake**: Plugin authors copy-paste from existing plugins and perpetuate outdated URLs, or perform find-replace but miss locations like GitHub Actions YAML examples, support/issues links, homepage URLs in plugin.json.

**Why It Happens**: Repository was renamed from ai-marketplace to ai-plugins. Existing plugins may still reference old name. Copy-paste propagates errors.

**Detection Strategy**:
- Extract current repo name: `gh repo view --json name,owner`
- Check all plugin files for old repository references: `grep -r "ai-marketplace" plugins/<new-plugin>/`
- Required locations to verify:
  - `.claude-plugin/plugin.json`: repository, homepage fields
  - `README.md`: ALL github.com URLs in examples and links
  - GitHub Actions examples: plugin_marketplaces configuration

**Impact**: Broken links lead to wrong repository, installation instructions fail, issues/PRs filed in wrong location, unprofessional appearance.

**References**: PR [#9](https://github.com/bitwarden/ai-plugins/pull/9) - URL inconsistency required 3 commits to fix piecemeal

---

### Defense-in-Depth Input Validation Philosophy

**Category**: Security - Input Validation

**Pattern**: This repository explicitly values thorough input validation as a "defense-in-depth" security measure, even for internal scripts or tools.

**Common Mistake**: Assuming minimal input validation is sufficient for internal scripts, leading reviewers to suggest reducing validation checks as "over-engineered" or "excessive."

**Why It Happens**: Scripts feel "internal" or "trusted" so extensive validation seems unnecessary. Reviewers may not recognize the repository's security philosophy.

**Detection Strategy**:
- Look for input validation patterns in bash scripts (parameter validation, format checks, injection prevention)
- Note if reviewer questions or suggests removing validation
- This repository treats extensive validation as appropriate and necessary

**Impact**: Suggesting removal of validation reduces defense-in-depth protections and contradicts repository security standards.

**References**: PR [#17](https://github.com/bitwarden/ai-plugins/pull/17) - Extensive validation acknowledged as "precise use" and appropriate
