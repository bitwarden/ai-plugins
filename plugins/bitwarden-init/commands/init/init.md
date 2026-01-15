---
description: Initialize a Claude Code CLAUDE.md file with Bitwarden's standardized template format
allowed-tools: Read, Write, Edit, WebFetch, Grep, Glob
---

Initialize Claude Code configuration for this repository using a two-phase process that combines Anthropic's built-in analysis with Bitwarden's extended template.

**Phase 1: Run Anthropic's built-in init**

First, execute the built-in `/init` command to generate an initial CLAUDE.md file:

Use the Bash tool to run:
```bash
claude -p "/init" --allowedTools "Read" "Write" "WebFetch" "Grep" "Glob" --model "opus"
```

Wait for this to complete and verify that CLAUDE.md was created in the current directory.

**Phase 2: Enhance with Bitwarden template**

Once Phase 1 completes successfully, run the `/enhance` command from this plugin to extend the CLAUDE.md file with Bitwarden's standardized sections:

Use the Bash tool to run:
```bash
claude -p "/bitwarden-init:enhance" --allowedTools "Read" "Edit" "WebFetch" "Grep" "Glob" --model "opus"
```

**Completion**

After both phases complete successfully, read the generated CLAUDE.md and provide a summary report to the user:

1. **What `/init` captured**: Summarize the project-specific information discovered during Phase 1.

2. **What `/enhance` added**: Summarize the additional findings and documentation added during Phase 2.

3. **Suggested improvements**: Based on gaps or uncertainties encountered, suggest specific ways the user could improve their CLAUDE.md with their project knowledge.

Remind the user to review the generated file and commit it to their repository.
