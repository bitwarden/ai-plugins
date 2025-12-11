# Bitwarden Software Engineer Plugin

A comprehensive full-stack development plugin for Claude Code with language-specific skills and specialized agents.

## What This Plugin Provides

**Skills** that disclose to Claude language patterns and conventions:
- TypeScript, C#, Rust, SQL development patterns
- Progressive loading: only relevant skills activate when needed

**Agents** that coordinate complex workflows across languages:
- Architecture design, security review, code review, performance optimization
- Leverage skills automatically without requiring explicit language selection

**Commands** for common development workflows:
- Quick access to multi-step processes

## Why This Architecture

Software languages and frameworks are expertise, not workflows. Claude should apply software specific idioms automatically when working with specific files. Claude should not require explicit agent invocation.

### Skills vs Agents: Expertise vs Execution

> "Skills say 'here's how to do things.' Projects say 'here's what you need to know.' Skills provide capabilities that work everywhere—any conversation, any project."
>
> — [Skills explained: How Skills compares to prompts, Projects, MCP, and subagents](https://www.claude.com/blog/skills-explained), Claude.com

> "Use Skills to teach expertise that any agent can apply; use subagents when you need independent task execution with specific tool permissions and context isolation."
>
> — [Skills explained](https://www.claude.com/blog/skills-explained), Claude.com

**Skills teach patterns.** Agents execute workflows. This separation means security-reviewer can analyze TypeScript, C#, AND Rust without duplicating language expertise across multiple agent files.

### Progressive Disclosure: Unbounded Context Without Token Waste

> "Progressive disclosure is the core design principle that makes Agent Skills flexible and scalable. Like a well-organized manual that starts with a table of contents, then specific chapters, and finally a detailed appendix, skills let Claude load information only as needed"
>
> — [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), Anthropic Engineering Blog

> "Agents with a filesystem and code execution tools don't need to read the entirety of a skill into their context window when working on a particular task. This means that the amount of context that can be bundled into a skill is effectively unbounded."
>
> — [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), Anthropic Engineering Blog

At startup, only skill metadata (~100 tokens per skill) loads. Full instructions and examples load on-demand when Claude needs them.

## Plugin Structure

```
bitwarden-software-engineer/
├── skills/
│   ├── typescript/
│   └── csharp/
├── agents/
│   ├── security-reviewer.md
│   └── fullstack-architect.md
└── commands/
    ├── built-a-feature.md
```

Skills provide language expertise. Agents use those skills. Commands invoke agents.

## Installation

```bash
/plugin install bitwarden-software-engineer
```
