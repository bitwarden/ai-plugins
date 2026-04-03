# Jira Custom Fields by Issue Type

Maps each Bitwarden Jira issue type to its known custom fields. Use this to know which custom fields to look for and surface when reading an issue.

## Field Reference

| Field ID | Name | Type | Description |
|---|---|---|---|
| `customfield_10011` | Epic Name | string | The name of the epic (only on Epics) |
| `customfield_10012` | Epic Status | option | Status of the epic (only on Epics) |
| `customfield_10014` | Epic Link | string | Key of the parent epic (on child issue types) |
| `customfield_10020` | Sprint | array | Sprint(s) the issue belongs to |
| `customfield_10028` | Story Points | number | Estimated story points |
| `customfield_10170` | Github Url | string | URL of the associated GitHub PR (Contributions) |
| `customfield_10171` | Github ID | string | GitHub ID of the contributor (Contributions) |
| `customfield_10172` | QA testing notes | rich text | Notes and instructions for QA testing |
| `customfield_10173` | Goals / Deliverables | rich text | Expected goals and deliverables (Spikes) |
| `customfield_10175` | Outcome | rich text | Outcome of the work (Spikes) |
| `customfield_10192` | Acceptance criteria | rich text | Criteria that must be met for acceptance |
| `customfield_10216` | Testing Branch | option | Branch designated for testing |
| `customfield_10218` | Initiative Owner | option | Owner of the parent initiative |
| `customfield_10219` | Defect Source | option | Source classification for defects |
| `customfield_10224` | Security Approver | array | Designated security approver(s) |
| `customfield_10307` | Replication steps | rich text | Steps to reproduce the bug (QA Bugs) |
| `customfield_10313` | Technical breakdown | rich text | Technical implementation details |
| `customfield_10981` | Bug category | option | Classification category for bugs (QA Bugs) |

## Fields by Issue Type

### Epic

| Field ID | Name |
|---|---|
| `customfield_10011` | Epic Name |
| `customfield_10012` | Epic Status |
| `customfield_10028` | Story Points |
| `customfield_10218` | Initiative Owner |
| `customfield_10219` | Defect Source |
| `customfield_10224` | Security Approver |

### Spike

| Field ID | Name |
|---|---|
| `customfield_10014` | Epic Link |
| `customfield_10020` | Sprint |
| `customfield_10028` | Story Points |
| `customfield_10173` | Goals / Deliverables |
| `customfield_10175` | Outcome |
| `customfield_10218` | Initiative Owner |
| `customfield_10219` | Defect Source |
| `customfield_10224` | Security Approver |

### Story

| Field ID | Name |
|---|---|
| `customfield_10014` | Epic Link |
| `customfield_10020` | Sprint |
| `customfield_10028` | Story Points |
| `customfield_10172` | QA testing notes |
| `customfield_10192` | Acceptance criteria |
| `customfield_10216` | Testing Branch |
| `customfield_10218` | Initiative Owner |
| `customfield_10219` | Defect Source |
| `customfield_10224` | Security Approver |
| `customfield_10313` | Technical breakdown |

### Task

| Field ID | Name |
|---|---|
| `customfield_10014` | Epic Link |
| `customfield_10020` | Sprint |
| `customfield_10028` | Story Points |
| `customfield_10192` | Acceptance criteria |
| `customfield_10218` | Initiative Owner |
| `customfield_10219` | Defect Source |
| `customfield_10224` | Security Approver |
| `customfield_10313` | Technical breakdown |

### QA Bug

| Field ID | Name |
|---|---|
| `customfield_10020` | Sprint |
| `customfield_10172` | QA testing notes |
| `customfield_10218` | Initiative Owner |
| `customfield_10219` | Defect Source |
| `customfield_10224` | Security Approver |
| `customfield_10307` | Replication steps |
| `customfield_10981` | Bug category |

### Subtask

| Field ID | Name |
|---|---|
| `customfield_10020` | Sprint |
| `customfield_10218` | Initiative Owner |
| `customfield_10219` | Defect Source |
| `customfield_10224` | Security Approver |

### Bug

| Field ID | Name |
|---|---|
| `customfield_10014` | Epic Link |
| `customfield_10218` | Initiative Owner |
| `customfield_10219` | Defect Source |
| `customfield_10224` | Security Approver |

### Contribution

| Field ID | Name |
|---|---|
| `customfield_10170` | Github Url |
| `customfield_10171` | Github ID |
| `customfield_10216` | Testing Branch |
| `customfield_10218` | Initiative Owner |
| `customfield_10219` | Defect Source |
| `customfield_10224` | Security Approver |
