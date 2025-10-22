# Bitwarden AI Plugins Marketplace - Claude Instructions

This repository serves as a marketplace / registry for AI development plugins and tools maintained by Bitwarden.

## Repository Purpose

This is the **Bitwarden AI Plugins** repository - a curated collection of plugins and tools designed for AI-assisted development. The repository enables:

- Discovery and distribution of AI development plugins
- Quality-controlled plugin contributions
- Integration with Claude Code and other AI development tools
- Secure, well-maintained tooling for development workflows

## Project Structure

- **Root Level**: Marketplace configuration and documentation
- **Plugin Directories**: Each plugin should have its own directory with standardized structure

## Working with Plugins

### Plugin Discovery

When users ask about available plugins:

1. Search the repository for plugin directories
2. Check each plugin's README for capabilities and usage
3. Present plugins with their descriptions and installation instructions

### Adding New Plugins

When contributing a new plugin:

1. Create a new directory with a descriptive name (e.g., `security-scanner/`, `code-reviewer/`)
2. Include the following structure:
    ```
    plugin-name/
    ├── README.md           # Plugin description, usage, and examples
    ├── package.json        # Dependencies and metadata
    ├── src/                # Source code
    ├── tests/              # Test suite
    └── docs/               # Additional documentation
    ```
3. Follow Bitwarden's contributing guidelines at contributing.bitwarden.com
4. Ensure all security best practices are followed (see SECURITY.md)
5. Add appropriate entries to `.cspell.json` for any domain-specific terms

### Plugin Requirements

All plugins MUST:

- Have comprehensive README documentation
- Include proper error handling and validation
- Follow security best practices (no credential exposure, input validation, etc.)
- Include tests with reasonable coverage
- Be compatible with Claude Code and similar AI development tools
- Have clear version numbers following semantic versioning

### Code Quality Standards

- Use `.editorconfig` settings for consistent formatting
- Run spell check against `.cspell.json`
- Pass pre-commit hooks (configured via Husky)

## Security Considerations

This is a Bitwarden-maintained repository with high security standards:

- **Never commit credentials or API keys**
- **Review all external dependencies for vulnerabilities**
- **Follow principle of least privilege for any system access**
- Use secure coding practices for all plugin implementations

## Workflow Integration

When working with PRs:

1. Automated reviews will trigger on pull request creation
2. Address any automated feedback promptly
3. Human reviewers (see CODEOWNERS) will provide final approval

## Claude-Specific Guidance

### When Users Ask About Plugins

- Search the repository structure to find available plugins
- Read plugin READMEs to understand capabilities
- Provide installation and usage instructions
- Suggest relevant plugins based on user needs

### When Implementing Plugin Features

- Follow existing patterns in the repository
- Add comprehensive comments
- Consider cross-platform compatibility (Windows, macOS, Linux)

### When Testing Plugins

- Write unit tests for core functionality
- Include integration tests for external dependencies
- Test error scenarios and edge cases
- Verify security controls work as intended

## Best Practices

1. **Documentation First**: Always write comprehensive documentation before implementation
2. **Security by Default**: Assume all inputs are untrusted
3. **Fail Safely**: Plugins should degrade gracefully on errors
4. **Version Compatibility**: Clearly document version requirements
5. **Performance**: Consider performance implications for large-scale operations
6. **User Experience**: Provide clear error messages and helpful feedback

## Marketplace Governance

- **Code Owners**: Defined in `.github/CODEOWNERS`
- **Review Process**: All changes require review from code owners
- **Quality Standards**: Automated and manual reviews ensure quality

## Resources

- Bitwarden Contributing Guidelines: https://contributing.bitwarden.com
