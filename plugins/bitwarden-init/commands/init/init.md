---
description: Initialize a Claude Code CLAUDE.md file with Bitwarden's standardized template format
---

Initialize Claude Code configuration for this repository with Bitwarden's standardized template format.

**Instructions:**

1. **Generate Initial Context**: First, analyze the codebase to gather comprehensive information about the project:
   - Examine the repository structure, build system, and configuration files
   - Identify the primary programming languages, frameworks, and tools used
   - Understand the architecture patterns and module organization
   - Review existing documentation, README files, and comments
   - Identify data models, API endpoints, and key business logic

2. **Create CLAUDE.md**: Generate a CLAUDE.md file in the repository root with the following standardized sections:

## Overview
- Brief description of the business domain and project purpose
- Key concepts and terminology specific to this codebase
- Primary user types and their main workflows
- Integration points with external systems

## Architecture & Patterns
- High-level folder structure and organization
- Module boundaries and layer dependencies
- Communication patterns between components
- Design patterns and architectural decisions
- External service integrations

## Stack Best Practices
- Language-specific idioms and conventions used in this codebase
- Framework patterns and recommended approaches
- Dependency injection and configuration patterns
- Error handling and validation strategies
- Testing approaches and utilities
- Where to find authoritative documentation on the web

## Anti-Patterns
- Common mistakes to avoid in this codebase
- Security concerns (e.g., logging sensitive data, hardcoded secrets)
- Performance pitfalls
- Maintenance anti-patterns (e.g., non-parameterized SQL queries)

## Data Models
- Core domain entities and their relationships
- Key value objects and DTOs
- Data validation rules and constraints
- Database migration patterns
- API request/response formats

## Configuration, Security, and Authentication
- Environment variable management
- Secrets handling 
- Authentication and authorization flows
- API security patterns and middleware
- Compliance requirements and security controls

**Content Guidelines:**
- Keep content **clear, concise, and specific to THIS repository**
- Use bullet points for readability
- Include specific examples from the codebase where helpful
- Avoid generic advice—focus on patterns actually used in this project
- Preserve critical technical details that would help someone understand the codebase quickly

**Final Step**: After creating CLAUDE.md, inform the user that they can customize the content further and should commit the file to their repository.
