# reviewing-claude-config

Comprehensive skill for reviewing Claude Code configuration files with security-first approach.

## Overview

This skill provides systematic review guidance for Claude Code configuration files in `.claude` directories. It detects file types, applies appropriate review checklists, and enforces security best practices with executable detection scripts.

**Use this skill when:**
- Reviewing changes to `CLAUDE.md` files
- Reviewing skill files (`skill.md` and supporting files)
- Reviewing prompts or commands (`.claude/prompts/*.md`, `.claude/commands/*.md`)
- Reviewing settings files (`.claude/settings.json`)
- Validating Claude configuration security and quality

## Features

### Security-First Approach
- Detects committed `settings.local.json` files
- Scans for hardcoded secrets and credentials
- Validates permission scoping
- Identifies dangerous command auto-approvals
- Includes executable `security-scan.sh` script

### Intelligent Routing
- Detects configuration file type automatically
- Routes to appropriate specialized checklist
- Progressive disclosure for token efficiency
- Structured thinking throughout review process

### Quality Enforcement
- YAML frontmatter validation
- Progressive disclosure enforcement (500 line limit)
- Prompt engineering quality checks
- File reference integrity validation
- Token efficiency optimization

### Comprehensive Coverage
- **4 specialized checklists**: Skills, CLAUDE.md, Prompts, Settings
- **3 reference guides**: Priority framework, security patterns, quality criteria
- **4 review examples**: Demonstrating proper feedback format
- **Executable security script**: Automated security scanning

## Installation

### Option 1: Copy to Your Project

```bash
# Copy the entire skill directory to your project's .claude/skills/ directory
cp -r reviewing-claude-config /path/to/your/project/.claude/skills/
```

### Option 2: Clone from Repository

```bash
# In your project's .claude/skills/ directory
cd .claude/skills/
git clone [repository-url] reviewing-claude-config
```

### Verify Installation

```bash
# Check that skill is recognized by Claude Code
ls -la .claude/skills/reviewing-claude-config/SKILL.md

# Optionally, make security script executable
chmod +x .claude/skills/reviewing-claude-config/scripts/security-scan.sh
```

## Usage

### As a Skill (Recommended)

Claude Code will automatically invoke this skill when appropriate based on the description. You can also invoke it explicitly:

```
Review the changes to .claude/CLAUDE.md
```

The skill will:
1. Detect the file type (CLAUDE.md in this case)
2. Execute security scan
3. Load the appropriate checklist
4. Provide structured review with inline comments

### Manual Security Scan

Run the executable security script directly:

```bash
# From the scripts directory
cd .claude/skills/reviewing-claude-config/scripts
./security-scan.sh

# Or scan a specific directory
./security-scan.sh /path/to/.claude
```

The script checks for:
- Committed settings.local.json
- Hardcoded secrets (API keys, tokens, passwords)
- Overly broad permissions
- Dangerous command auto-approvals

### Examples

**Review a new skill:**
```
Review .claude/skills/my-new-skill/skill.md
```

**Review settings changes:**
```
Review the changes to .claude/settings.json
```

**Review CLAUDE.md updates:**
```
Review .claude/CLAUDE.md for quality and security
```

## File Structure

```
reviewing-claude-config/
├── skill.md                          # Main orchestration file
├── checklists/                       # Specialized review checklists
│   ├── skills.md                     # Skill review checklist
│   ├── claude-md.md                  # CLAUDE.md review checklist
│   ├── prompts.md                    # Prompts/commands checklist
│   └── settings.md                   # Settings security checklist
├── reference/                        # Reference materials (loaded on-demand)
│   ├── priority-framework.md         # Issue classification system
│   ├── security-patterns.md          # Security checks and remediation
│   ├── prompt-engineering-quality.md # Quality criteria index (modular)
│   ├── quality-clarity.md            # Clarity criteria
│   ├── quality-specificity.md        # Specificity criteria
│   ├── quality-examples.md           # Examples criteria
│   ├── quality-emphasis.md           # Emphasis criteria
│   ├── quality-structure.md          # Structure criteria
│   ├── quality-context.md            # Context criteria
│   ├── quality-actionability.md      # Actionability criteria
│   ├── quality-structured-thinking.md # Structured thinking criteria
│   ├── quality-checklist.md          # Comprehensive quality checklist
│   └── quality-improvement-patterns.md # Common improvement patterns
├── examples/                         # Sample review outputs
│   ├── README.md                     # Examples index and loading guide
│   ├── example-skill-review.md       # Skill review example
│   ├── example-claude-md-review.md   # CLAUDE.md review example
│   ├── example-settings-review.md    # Settings review example
│   └── example-prompts-review.md     # Prompts review example
├── scripts/                          # Executable automation
│   └── security-scan.sh              # Comprehensive security scanner
├── docs/                             # Historical documentation
│   ├── CHANGELOG.md                  # Version history
│   ├── IMPLEMENTATION_PLAN.md        # Original implementation plan
│   └── FINAL_REPORT.md               # Implementation completion report
├── README.md                         # This file
└── LICENSE                           # MIT License
```

## Review Process

The skill follows a systematic 5-step review process:

1. **Detect File Type**: Determines whether reviewing skills, CLAUDE.md, prompts, or settings
2. **Execute Security Scan**: Always performs critical security checks first
3. **Load Appropriate Checklist**: Routes to specialized review guidance
4. **Consult References**: Loads detailed criteria only when needed
5. **Document Findings**: Provides inline comments with specific fixes

### Security Checks (Always First)

Regardless of file type, these checks are performed:
- ✅ settings.local.json NOT in git
- ✅ No hardcoded credentials
- ✅ Permissions appropriately scoped
- ✅ No dangerous command auto-approvals

If any security check fails, it's flagged as **CRITICAL** immediately.

### Priority Levels

Issues are classified into four priority levels:

- **CRITICAL**: Prevents functionality, exposes security vulnerabilities (must fix)
- **IMPORTANT**: Significantly impacts quality or maintainability (should fix)
- **SUGGESTED**: Nice-to-have improvements (optional)
- **OPTIONAL**: Personal preferences (author decides)

## Requirements

- Claude Code (tested with latest version)
- Git (for committed file detection in security scan)
- Bash (for security-scan.sh script)

## Configuration

This skill works out-of-the-box with no configuration needed. It's 100% generic and supports any project type or language.

### Customization

If you want to customize for your organization:

1. **Modify checklists**: Add project-specific requirements to checklist files
2. **Adjust security patterns**: Add organization-specific secret patterns to `security-scan.sh`
3. **Update priority framework**: Adjust severity levels based on team standards

**Note**: Keep changes generic to maintain portability if sharing with other teams.

## Examples

Available review examples for each configuration type:
- `examples/example-agent-review.md` - Agent review with security and quality issues
- `examples/example-skill-review.md` - Skill review with multiple issues
- `examples/example-claude-md-review.md` - CLAUDE.md review with duplication
- `examples/example-settings-review.md` - Settings review with security concerns
- `examples/example-prompts-review.md` - Prompts review with quality improvements

## Research Foundation

This skill incorporates research-backed best practices:

- **Chain of Thought prompting**: 40% error reduction (Anthropic)
- **Progressive disclosure**: <500 line main files (Anthropic)
- **Structured thinking**: Systematic analysis before feedback
- **Security-first approach**: Critical checks before quality review

See `docs/IMPLEMENTATION_PLAN.md` for detailed research sources.

## Troubleshooting

### Skill Not Recognized

**Issue**: Claude doesn't invoke the skill automatically

**Solutions:**
1. Verify YAML frontmatter exists in `skill.md`
2. Check skill name is `reviewing-claude-config`
3. Ensure file is in `.claude/skills/reviewing-claude-config/`
4. Try invoking explicitly: "Use reviewing-claude-config skill"

### Security Script Fails

**Issue**: `./security-scan.sh` returns errors

**Solutions:**
1. Make executable: `chmod +x security-scan.sh`
2. Verify you're in a git repository (for git commands)
3. Check script has access to `.claude` directory
4. Review error messages for specific issues

### False Positives in Security Scan

**Issue**: Security scan detects patterns in documentation

**Solutions:**
1. Security scan excludes `examples/` and `security-patterns.md`
2. Use "example" or "your-key-here" as placeholders in docs
3. Review manually to confirm false positives

## Contributing

This skill is designed for internal team use but follows open-source best practices.

**To contribute improvements:**
1. Test changes in your project first
2. Ensure changes remain 100% generic (no project-specific references)
3. Update CHANGELOG.md with changes
4. Increment version in `skill.md` YAML frontmatter (semver)

## Versioning

This skill follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes to skill interface or file structure
- **MINOR**: New features, new checklists, backward-compatible changes
- **PATCH**: Bug fixes, documentation updates, minor improvements

Current version: **1.0.0**

See CHANGELOG.md for version history.

## License

MIT License - See LICENSE file for details.

## Support

For issues, questions, or feedback:
1. Check troubleshooting section above
2. Review examples in `examples/review-outputs.md`
3. Consult reference files for detailed guidance
4. Contact your team's Claude Code administrator

## Acknowledgments

Built with research-backed best practices from:
- Anthropic Official Documentation (Chain of Thought, Progressive Disclosure)
- Claude Code Best Practices
- Security best practices for credential detection
- Prompt engineering quality standards

---

**Version**: 1.0.0
**Last Updated**: 2025-10-30
**Maintainer**: Internal Team
