# Status Lifecycle

The template defines six states. Status is how cross-team consumers know whether to engage — move through them deliberately.

| State           | Meaning                                                        | Entry criteria                                                                                                |
| --------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **In Planning** | Committed to but not actively being drafted yet.               | Team has agreed to produce a breakdown; nobody has started writing.                                           |
| **In Progress** | Actively being drafted. Cross-team review not yet appropriate. | Drafting Specification, Plan, and supporting sections; intra-team discussion to flesh out questions.          |
| **Proposed**    | Ready for review. Two parallel streams run during this state.  | Specification, Plan, Tasks, Agent Context complete; Cross-team engagement signoff table identifies reviewers. |
| **Accepted**    | The agreed-on technical design. Implementation can begin.      | **Two gates closed:** all signoffs captured **and** the team has completed a refinement pass on Tasks.        |
| **Complete**    | Implementation has shipped.                                    | File moved to `<team>/complete/` on the same PR that flips status.                                            |
| **Rejected**    | Terminal alternative to Complete.                              | Review surfaced incompatibilities or blockers that can't be resolved; a new breakdown supersedes it.          |

Files under `**/complete/**` are point-in-time records, not source of truth. Don't edit them except to correct factual errors.
