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

After both phases complete:
1. Inform the user that CLAUDE.md has been created and enhanced
2. Suggest they review and customize the generated file
3. Remind them to commit CLAUDE.md to their repository
