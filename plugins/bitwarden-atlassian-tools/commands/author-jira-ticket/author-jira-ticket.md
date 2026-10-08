---
argument-hint: "[ticket description or context] [--type Epic|Story|Task|Spike|Bug] [--no-scenarios] | (blank to provide interactively)"
allowed-tools: AskUserQuestion, Skill(bitwarden-atlassian-tools:authoring-jira-tickets)
description: Draft a Jira ticket as a local .md file. Guides you through ticket type, context, and content, then writes a structured draft ready to copy into Jira fields. Does not create the ticket in Jira.
---

Invoke `Skill(bitwarden-atlassian-tools:authoring-jira-tickets)` and pass the full contents of `$ARGUMENTS` to it as the initial context. The skill handles all interaction, drafting, review, and file writing.
