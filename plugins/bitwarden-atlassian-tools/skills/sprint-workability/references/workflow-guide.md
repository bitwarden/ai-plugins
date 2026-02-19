# Sprint Workability Workflow Guide

## Overview

This guide documents the complete workflow for sprint workability analysis.

## Data Sources

### Confluence Pages
- Pages often contain sprint data in table format
- Ticket IDs appear as hyperlinks within tables
- Sections are typically organized by sprint dates or names

### JIRA Direct
- Use JQL to query sprint assignments
- Filter by sprint name, date range, or sprint ID

### Ticket Lists
- Direct input of comma-separated ticket keys
- Useful for ad-hoc analysis of specific tickets

## Parallel Processing

The workflow leverages parallel subagent execution for efficiency:
- Each ticket investigation runs as an independent agent
- All agents execute simultaneously
- Results are collected and aggregated after completion

## Category Definitions

### BLOCKED
- External dependencies unresolved
- Waiting on other teams
- Architectural constraints

### STALLED
- Work complete but not closed
- Administrative cleanup needed
- PR merged but ticket open

### NEEDS_CLARIFICATION
- Missing requirements
- Unclear acceptance criteria
- Unassigned tickets

### IN_PROGRESS
- Active work underway
- Clear path to completion
- No blockers identified
