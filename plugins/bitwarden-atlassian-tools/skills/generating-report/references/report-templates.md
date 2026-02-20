# Report Templates Reference

## JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "sprint": { "type": "string" },
        "analysisDate": { "type": "string", "format": "date-time" },
        "platform": { "type": "string" },
        "totalTickets": { "type": "integer" }
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "healthScore": { "type": "number" },
        "categoryBreakdown": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "count": { "type": "integer" },
              "percentage": { "type": "number" }
            }
          }
        }
      }
    },
    "categories": {
      "type": "object",
      "properties": {
        "BLOCKED": { "$ref": "#/definitions/categoryDetail" },
        "STALLED": { "$ref": "#/definitions/categoryDetail" },
        "NEEDS_CLARIFICATION": { "$ref": "#/definitions/categoryDetail" },
        "IN_PROGRESS": { "$ref": "#/definitions/categoryDetail" }
      }
    },
    "recommendations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "priority": { "type": "string" },
          "action": { "type": "string" },
          "tickets": { "type": "array", "items": { "type": "string" } }
        }
      }
    }
  },
  "definitions": {
    "categoryDetail": {
      "type": "object",
      "properties": {
        "tickets": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "key": { "type": "string" },
              "summary": { "type": "string" },
              "status": { "type": "string" },
              "assignee": { "type": "string" },
              "reason": { "type": "string" },
              "recommendation": { "type": "string" },
              "confidence": { "type": "number" }
            }
          }
        }
      }
    }
  }
}
```

## YAML Template

```yaml
sprint_analysis:
  metadata:
    sprint: "{sprint_identifier}"
    analysis_date: "{timestamp}"
    platform: "{platform}"
    total_tickets: {total_count}

  summary:
    health_score: {health_score}
    categories:
      blocked:
        count: {blocked_count}
        percentage: {blocked_pct}
      stalled:
        count: {stalled_count}
        percentage: {stalled_pct}
      needs_clarification:
        count: {clarify_count}
        percentage: {clarify_pct}
      in_progress:
        count: {progress_count}
        percentage: {progress_pct}

  blocked_tickets:
    - key: "{ticket_key}"
      summary: "{summary}"
      blocker: "{blocker}"
      recommendation: "{recommendation}"

  stalled_tickets:
    - key: "{ticket_key}"
      summary: "{summary}"
      evidence: "{evidence}"
      recommendation: "{recommendation}"

  needs_clarification_tickets:
    - key: "{ticket_key}"
      summary: "{summary}"
      issues:
        - "{issue_1}"
      recommendation: "{recommendation}"

  in_progress_tickets:
    - key: "{ticket_key}"
      summary: "{summary}"
      progress: "{progress}"
      blockers: []

  recommendations:
    immediate:
      - "{action_1}"
    short_term:
      - "{action_2}"
    process_improvements:
      - "{improvement_1}"
```

## Inline Summary Template

```
Sprint Analysis: {sprint_identifier} ({platform})

{total_count} tickets analyzed:
- {blocked_count} BLOCKED: {blocked_keys}
- {stalled_count} STALLED: {stalled_keys}
- {clarify_count} NEEDS CLARIFICATION: {clarify_keys}
- {progress_count} IN PROGRESS: {progress_keys}

Health Score: {health_score}/100 ({health_status})

Top 3 Actions:
1. {action_1}
2. {action_2}
3. {action_3}
```
