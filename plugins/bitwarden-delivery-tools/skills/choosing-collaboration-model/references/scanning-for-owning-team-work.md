# Scanning for Owning-Team In-Flight Work

Load this reference when running the domain-velocity scan (input 6 in the parent `SKILL.md`). The scan surfaces whether the owning team is actively reshaping the area the cross-team change touches — a signal that shifts the recommended model from Internal Open-Source toward File a Ticket so the owning team can sequence the change into their work.

The scan is operationally similar to the broader collision scan in `Skill(writing-tech-breakdowns)`, but narrower in two ways: it's run **per impact** (per cross-team interaction) rather than per breakdown, and it's focused on **one owning team's area** rather than the whole org. The output feeds the model recommendation, not just a coordination note.

## What to scan

Two surfaces, in order. The first catches planned work; the second catches in-flight work.

### 1. In-flight breakdowns in the owning team's folder

Search `bitwarden/tech-breakdowns` under the owning team's directory (e.g., `platform/`, `auth/`, `key-management/`, `mobile/`), **excluding `**/complete/**`**. Files under `complete/` are point-in-time historical records, not active work.

**What to look for:**

- **Agent Context's `Repos affected`** overlapping the repos the change touches.
- **Plan-section per-layer subsections** discussing the same files, modules, or domain areas.
- **Tasks-section `Affected files / crates / modules`** overlapping the files the change touches.
- **Specification or Plan** mentioning the same feature surface, contract, or pattern.

**How to scan, from a locally cloned `bitwarden/tech-breakdowns`:**

```bash
# Surface affected-repo names in the owning team's folder
grep -rli "<repo-name>" <owning-team>/ --include="*.md" --exclude-dir=complete

# Surface specific module/file/pattern names
grep -rli "<file-or-module-name>" <owning-team>/ --include="*.md" --exclude-dir=complete
```

Use the `Grep` tool for the first pass; refine with file-path searches once candidate breakdowns are identified. Read each candidate's Tasks and Plan sections to confirm overlap rather than relying on grep matches alone — a breakdown that mentions a repo in passing is different from one whose Tasks reshape it.

### 2. Open PRs in the owning team's repos

For each repo the change touches, list open PRs and check whether they overlap on file paths:

```bash
gh pr list -R bitwarden/<repo> --state open --json number,title,headRefName,files,author --limit 50
```

**What to look for:**

- PRs from the owning team's engineers touching the same paths the change touches.
- Long-lived feature branches (older than a sprint) that name the same domain.
- Refactor PRs touching the modules the change depends on.

Open PRs are the higher-collision signal: an in-flight branch may land before, during, or after the cross-team change, and the conventions can shift between draft and merge.

## What the findings mean

| What the scan surfaced                                                                 | Model implication                                                                                                                                                                                 |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No active work in the area                                                             | Original model recommendation stands. Note the scan output explicitly in Step 6 ("scan: no in-flight Platform breakdowns or PRs in the audit-event-bus area").                                    |
| Owning team's in-flight breakdown names the same area or files                         | Shift toward **File a Ticket** so the owning team can sequence the change into their planned work. Link the in-flight breakdown in the signoff-table row.                                         |
| Open PR overlapping the change's file paths                                            | Model usually doesn't change, but timing does. Coordinate to land changes together or sequence them — capture in the breakdown's `Coordination notes`.                                            |
| Recent material churn (multiple merged PRs in the last sprint touching the same files) | Conventions to code against may not be stable. Surface as a Clarifications Log entry; defer defaulting to Internal Open-Source until conventions settle.                                          |
| Cross-team interfaces evolving on both sides simultaneously                            | Don't pick a model unilaterally. Escalate to the initiative owner (or both teams' EMs if no initiative). The contested domain needs cross-team alignment before the model decision is meaningful. |

## Surfacing the findings

The Step 6 output must include:

- **What was scanned** (which folders, which repos).
- **What was found** (specific breakdowns, PRs, or churn signals — with links).
- **How it shifted the model choice**, or "no shift — area is quiet."

A recommendation that says "Internal Open-Source — assuming the area is quiet, which I didn't check" is worse than one that says "Internal Open-Source — confirmed via scan: no in-flight Platform breakdowns under `platform/`, no open PRs touching the event-bus topic-registration path." The scan output is part of the working artifact, not just an internal sanity check.

## When to skip the scan

Pure consumption of an unchanged API doesn't need a model and doesn't need a scan. Advisory-only signoffs (no code change on the owning team's side) don't need a scan either. Everything else does — the scan is cheap enough that skipping it is rarely defensible.

## Relationship to the breakdown-level collision scan

`Skill(writing-tech-breakdowns)` runs a similar scan at the **breakdown level** — before drafting and again at `Proposed` — to surface any team's overlapping work and prevent two breakdowns from being drafted in parallel in the same area. The findings of that broader scan are inputs to this skill's per-impact scan: if the breakdown-level scan flagged an overlap with team X, the per-impact scan for team X's signoff row is already half-done. Read the breakdown-level findings first; this scan refines them per impact rather than re-doing them.
