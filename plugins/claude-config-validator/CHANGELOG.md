# Changelog

All notable changes to the Claude Config Validator Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-14

### Added

- Initial release of `claude-config-validator` plugin
- **Comprehensive configuration validation** for 6 file types:
  - Agents (`.claude/agents/*.md`)
  - Skills (skill directories with `SKILL.md`)
  - CLAUDE.md (project instructions)
  - Prompts (`.claude/prompts/*.md`)
  - Commands (`.claude/commands/*.md`)
  - Settings (`.claude/settings.json`)
  - Plugin configurations (`plugins/*/`)
- **Security-first validation** with critical checks:
  - Detection of committed `settings.local.json` files
  - Hardcoded credential scanning (API keys, passwords, tokens)
  - Appropriate permission scoping validation
  - Principle of least privilege for agent tool access
  - Dangerous command pattern detection in hooks/scripts
- **Multi-pass review strategy**:
  - Pass 1: Security scan (critical checks first)
  - Pass 2: Structure validation (YAML frontmatter, file organization)
  - Pass 3: Functionality review (logic, completeness, integration)
  - Pass 4: Quality assessment (best practices, prompt engineering)
  - Pass 5: Marketplace standards (elevated requirements for public plugins)
- **Agent validation** with 6-pass comprehensive strategy:
  - YAML frontmatter validation
  - Tool access security and least privilege enforcement
  - Description clarity and activation trigger assessment
  - System prompt quality evaluation
  - Model selection appropriateness
  - Marketplace readiness checks
- **Skill validation** with 4-pass strategy:
  - Structure and YAML validation
  - Progressive disclosure pattern enforcement (500-line guideline)
  - Token efficiency optimization
  - Reference accuracy and completeness checks
- **Evidence-based recommendations** sourced from:
  - Official Anthropic documentation
  - Microsoft Azure AI enterprise patterns
  - Agent tool access security matrices
  - Progressive disclosure guidelines
  - Model selection decision trees
- **Priority-classified feedback system**:
  - CRITICAL: Security vulnerabilities, blocking issues
  - IMPORTANT: Significant quality or functionality issues
  - SUGGESTED: Best practice improvements
  - OPTIONAL: Nice-to-have enhancements
- **16 reference files** covering:
  - Security patterns and tool access matrices
  - Agent configuration best practices
  - Progressive disclosure guidelines
  - Quality and specificity standards
  - YAML validation rules
  - Model selection guidance
- **5 specialized validation checklists**:
  - Agent validation checklist
  - Skill validation checklist
  - CLAUDE.md validation checklist
  - Prompt/command validation checklist
  - Settings validation checklist
- **6 example review outputs** demonstrating validation patterns
- **Inline, actionable feedback** with file:line references and specific fixes
- Validation automation scripts for security scanning
- Plugin manifest with metadata and skill registration
- Comprehensive README documentation

---

## Version Format

Plugin version tracks validation system changes:

- **Major version**: Breaking changes to validation checklists, security rules, or plugin structure
- **Minor version**: New validation features, additional configuration type support, new reference documentation
- **Patch version**: Bug fixes, clarifications, documentation improvements, checklist refinements
