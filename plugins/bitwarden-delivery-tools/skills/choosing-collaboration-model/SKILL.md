---
name: choosing-collaboration-model
description: Evaluate a proposed cross-team change and recommend a collaboration model — File a Ticket, Internal Open-Source, or (rarely) Embedded Expert. Use when shaping a tech breakdown's cross-team impacts, planning a work transition, picking up an initiative-funnel handoff, or any time a team is about to ask another team to take on, review, or contribute to a change. Begins by interrogating whether the change should cross domain boundaries at all (including the case where the change is internal-only and just needs owning-team review), evaluates the change shape, scans the owning team's in-flight breakdowns and open PRs for collision risk in the same area, and outputs a recommendation with reasoning, a runner-up, the in-flight findings, and the confirmation step the owning team has to walk through.
allowed-tools: Skill, Read, Bash, Glob, Grep
---

This skill answers two questions about a specific cross-team change:

1. **Should this change cross the domain boundary?** Or is it a sign of a misshaped scope, a missing platform capability, or a candidate for an internal reorganization?
2. **If yes, how should the crossing happen?** Pick a collaboration model and name it on the impact.

The output is a single recommended model plus reasoning. The skill is deliberately opinionated: vague crossings ("we'll figure it out with the other team") are the failure mode it exists to prevent.

**The model is a joint decision.** The driving team proposes; the owning team confirms or counter-proposes during signoff. A model in a breakdown without owning-team confirmation is a proposal, not a commitment.

## What makes a change cross-team

**The trigger is code ownership of files.** A change is a cross-team change when it adds, modifies, or deletes files whose ownership belongs to a team other than the driving team. Ownership is established by:

- `CODEOWNERS` files in each repo — the authoritative source. If an affected path matches an `@<other-team>` entry, the change touches that team's domain.
- Repo-level ownership when a whole repo is owned by one team and the driving team isn't an owner.
- Folder-level ownership inside multi-team repos (e.g., a feature library or a service module owned by a different team than the consumer touching it).

If no file in scope crosses an ownership line, it's an internal change and this skill doesn't apply. Run the chooser only when at least one affected file has an `@<other-team>` owner. The boundary is whatever `CODEOWNERS` says it is, not whatever the driving team's mental model says — re-check the file before assuming.

Edges to watch:

- **Shared files with multiple `CODEOWNERS` entries.** A change to a shared file is a cross-team change for each non-driving owner. Walk this skill once per owner — different impacts on the same file can use different models.
- **Files with no owner.** Orphan files are an ownership question first, a collaboration model question second. Identify the de facto maintainer (via `git log` / `git blame`) and surface the ownership gap before picking a model. If no team will own it, escalate.
- **Reading another team's code without modifying it.** Not a cross-team change in this skill's sense. Pure consumption of an API or service needs no model (see `Skill(writing-tech-breakdowns)` for the consumption-vs-extension distinction).
- **Modifying tests or fixtures owned by another team.** Yes — still a cross-team change. Test files in another team's `CODEOWNERS` scope follow the same rules as production code.

## Why be explicit about boundary crossings

Domain boundaries reflect cognitive-load decisions and ownership commitments. Crossing one carries cost: review overhead, knowledge gap, divergent conventions, coordination friction. The three models below are different ways of paying that cost; "no model" means somebody pays it implicitly, usually at the worst possible time. Being explicit about which crossings happen, why, and how is what keeps cognitive load bounded across teams.

## When to invoke

- A tech breakdown's `Cross-team engagement` section lists an impact in another team's code, another team's API, or an interface being built jointly. Invoke once per impact, not per team — different impacts to the same team can use different models.
- A platform team is rolling out a migration that requires feature-team code changes.
- A work transition is moving a framework, codebase, or operational responsibility between teams.
- A feature is being scoped that requires work that crosses team domain boundaries.

## Step 1: Should this crossing happen at all?

Before picking a model, validate that crossing is the right call. Three escape hatches:

1. **The change doesn't actually need to cross.** The driving team's mental model of the boundary may be stale. Re-check whether the change is in code the driving team owns, has been re-org'd into, or could be moved into. A "cross-team change" that resolves to "internal change" doesn't need a model.
2. **The change is in the driving team's code only — this is consumption (or other internal work), not cross-team work.** By the strict `CODEOWNERS` test in "What makes a change cross-team," if no affected file crosses to another team's ownership, this isn't a cross-team change in the skill's sense. Common cases: consuming a stable API the owning team built for consumption (Platform Consumption), integrating a new platform capability or SDK into your own feature, calling a new owning-team service from your own code, using a security primitive a different team owns. **The driving team owns the change; the owning team's involvement is governed by their API contract, not by a collaboration model.** Consuming a published API is what it's there for — don't reflexively add the owning team as `CODEOWNERS` on your code, demand their approval on every PR, or treat consumption as if it were a cross-team commitment from them. That conflates "this code is risky" with "this is cross-team work," and it loads the owning team with review work that their API was supposed to abstract away.

   _Exception, narrowly:_ if the integration is **novel, security-sensitive, or first-of-its-kind** enough that targeted owning-team input would meaningfully reduce risk (a first integration of a new cryptographic primitive into product code, a novel use of an API outside its documented use cases, an integration where misuse has compounding security risk), request a **one-time, bounded ask** — a design review, a threat-model review, or signoff on the integration shape before code is written. Frame it as a one-shot ask, not as ongoing review responsibility. If the owning team is "nervous about consumers getting it wrong," that's also feedback that the API itself may need better defaults, guardrails, or docs — not that every consumer needs ongoing review.

   **Embedded Expert is only the right answer here if the owning team explicitly opts into committing an engineer for the integration — and that's rare. The driving team can't propose Embedded Expert unilaterally for their own consumption work.**

3. **The crossing is a symptom of a missing platform capability.** If multiple feature teams are independently making the same change to the same platform code, the platform team should be absorbing that work into its API surface instead of accepting N parallel cross-team contributions. Surface this back to the platform team and choose a model only if absorption isn't on their roadmap.

If Step 1 surfaces an escape hatch, **don't return a model** — return the escape hatch. "Don't cross — this is an internal change that needs the owning team as reviewers" is a more valuable output than the least-bad model. If none apply, proceed to Step 2.

## Step 2: The three models

### File a Ticket

**Mechanic:** Driving team raises a request; **the owning team takes the work into their own domain.** If the change warrants a tech breakdown, the owning team writes it (often as a sibling breakdown linked from the driving team's signoff table). The owning team creates their own epic and stories on their board. The driving team specifies the contract they need (inputs, outputs, behavior) but not the internal implementation; their post-filing involvement is clarifying intent, reviewing the design, and signing off on the approach.

**What this implies for the driving team:** File a Ticket is **not** a low-cost option for the driving team's roadmap. It transfers planning and execution load to the owning team, who must absorb it into their sprint, their breakdown queue, and their metrics. Confirm the owning team can absorb it before defaulting to File a Ticket.

**Change shape this fits:**

- The change requires domain knowledge the driving team doesn't have.
- The change touches the owning team's internal architecture, not just its API surface.
- The change has compounding risk if done wrong (security primitives, data integrity, cryptography).
- The change is touching another team's core domain invariants - the change is deep enough that the owning team's mental model needs to absorb it; new architectural decisions, contract changes, security primitives.
- The change alters the mental model that the owning team has of their code.
- The change impacts areas in the owning team's domain that are under active development (open PRs, open breakdowns) - multiple changes in the same files from multiple teams will result in coordination friction.

**Bitwarden examples:**

- Mobile UI parity for a new feature — owned by Mobile (different stack, native expertise required).
- Modifications to authentication or session-management primitives — owned by Auth.
- Cryptographic implementation work — owned by KM.
- Database schema migrations on shared, high-traffic tables — owned by the data-owning team.
- Refactoring the internal architecture of a shared service — owned by the service team.
- Changes to the event-bus mechanism itself (not just adding a topic to it).

**Common shape:** "Change how it works internally" rather than "use it in a new way." If the change requires the owning team to reason about their domain invariants, they should hold the pen.

### Internal Open-Source

**Mechanic:** Driving team writes the change and opens a PR; owning team reviews and merges as maintainers. Work appears on the driving team's roadmap and metrics; the owning team's involvement is design review on the API and merge gatekeeping.

**Change shape this fits:**

- The change extends an existing pattern the owning team has documented.
- Codebase conventions are mature enough that an outside PR can land cleanly.
- The driving team has bandwidth and enough familiarity with the codebase to write a passable PR.

**Bitwarden examples:**

- Adding a new component to a shared component library, following the library's conventions.
- Adding a new endpoint to an existing API where similar endpoints already exist.
- Registering a new event topic on an event bus where topic-registration is a documented pattern.
- Extending a public type or interface with a new optional field.

**Common shape:** "Build on top of" or "add another instance of" — the owning team has anticipated this kind of extension, and the conventions are stable enough that the change can land without owning-team domain reasoning. The owning team's value-add is design review on the API, not writing the boilerplate.

### Embedded Expert

**Mechanic:** An engineer from the owning team embeds with the driving team for a defined period, working inside the driving team's codebase as a paired contributor through design, implementation, review, and (often) post-launch hardening.

**This is a rare model.** It's the heaviest pattern in the catalog and the only one where the owning team commits an engineer to the driving team's codebase rather than the other way around. **Two conditions must both hold** before recommending it:

1. **The owning team has explicitly agreed to commit bench capacity for the embed.** Embedded Expert is not a model the driving team can pick unilaterally — it's a real engineer-week commitment from the owning team. If they haven't volunteered or confirmed, route through Step 1's escape hatch instead (request them as reviewers) and let them counter-propose Embedded Expert if they want it.
2. **The driving team's success genuinely depends on owning-team presence inside the codebase, not just guidance.** Examples: a security-critical first integration where the owning team wants to be in the build (and has volunteered for it), a launch window where a one-time design review isn't enough, a foundational early integration where the owning team wants real-consumer feedback during the build. "We want their expertise" alone isn't enough — most "want their expertise" cases are satisfied by a one-time bounded design or threat-model review (the Step 1 escape hatch), not by an embed.

**Bitwarden examples (rare):**

- KM bench-commits an engineer to embed with a feature team during a security-critical first integration of a new cryptographic primitive, riding through design, review, and one sprint post-launch. KM proposes the embed; the feature team doesn't pre-assume it.
- Platform bench-commits an engineer to embed with a feature team for the first consumer adoption of a major new SDK, specifically to feed real-consumer learnings back into the SDK's API during the integration.

**Common shape:** "The owning team is sending an engineer." If that sentence isn't already true when the model is being proposed, the right answer is the escape hatch (request them as reviewers), not Embedded Expert.

## Internal Open-Source vs. owning-team development

This is the most common decision point — and the one teams most often default through without thinking. The split is about **change shape**, not preferences or capacity:

| Change shape                                                                                                                                               | Model                      | Why                                                                                                                                                                                                                                                                                      |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Add a new instance of an established pattern (component, endpoint, topic, flag, fixture)                                                                   | **Internal Open-Source**   | The pattern's conventions are documented; the owning team's value-add is design review on the API, not writing the boilerplate. A PR from the driving team is cheaper than queue time on the owning team's sprint.                                                                       |
| Change how the pattern works (event-bus mechanism, library renderer, auth flow internals)                                                                  | **File a Ticket**          | The change requires the owning team to reason about its own invariants. An outside PR will get rewritten in review, which wastes both teams' time and produces a worse result than the owning team writing it.                                                                           |
| Touch primitives where wrong code has compounding risk (crypto, auth, data integrity)                                                                      | **File a Ticket**          | The cost of a near-miss caught only in review is too high. The owning team writes; the driving team specifies the contract and reviews.                                                                                                                                                  |
| Mobile UI work for a feature originating on another team                                                                                                   | **File a Ticket**          | Native stack expertise, separate codebase, separate sprint cadence. The owning team writes their own breakdown and stories.                                                                                                                                                              |
| Driving team's codebase needs owning-team expertise inside it for a critical period, and the owning team has explicitly committed an engineer to the embed | **Embedded Expert** (rare) | Both conditions matter. The shape on the driving-team side justifies the embed; the owning-team commitment makes it real. Without the explicit commitment, the right answer is the escape hatch (treat as internal consumption — the driving team owns the change), not Embedded Expert. |

The driving team's preference doesn't drive this split, and neither does the owning team's capacity. Match the **shape of the change** to the model first. Capacity is a tie-breaker, not a driver. When the change is in the driving team's code only and the owning team hasn't committed to an embed, route through Step 1's escape hatch — proceed as internal consumption, with at most a one-time targeted ask if the integration is novel or security-sensitive.

## Step 3: Evaluate the change

Gather these six inputs before recommending a model. Don't skip any — if the answer is unknown, name it as unknown so the recommendation can be conditional.

| Input                                               | What to capture                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Whose code changes?**                          | Driving team's, owning team's, or both. If only the driving team's, the default path is Step 1's escape hatch — treat as internal consumption, with at most a bounded one-time review request if the integration is novel or security-sensitive. Embedded Expert applies only if the owning team has explicitly committed to embedding an engineer.                                                                                                       |
| **2. Domain-overlap depth**                         | _Surface_ (mechanical changes, well-documented patterns, no domain reasoning required), _Mid_ (must follow established contracts, naming, error-handling conventions), _Deep_ (touches the owning team's core invariants, mental model, or design rationale).                                                                                                                                                                                             |
| **3. Driving team's familiarity with the codebase** | _No / one-time / sustained_. Tied to how much review overhead the owning team will need to absorb.                                                                                                                                                                                                                                                                                                                                                        |
| **4. Repetition shape**                             | _One-shot / first-of-many / sustained_. The same engineers contributing to the same codebase repeatedly is a different state than one-off contribution.                                                                                                                                                                                                                                                                                                   |
| **5. Capacity and timing on both sides**            | Owning-team bandwidth to write the change. Driving-team bandwidth to draft a PR. Owning-team bench capacity to commit an engineer to an embed (rarely available; only relevant if Embedded Expert is being considered). Timeline tolerance for owning-team backlog wait. Capture both teams, not just the driving team's preference.                                                                                                                      |
| **6. Owning-team domain velocity**                  | Is the owning team actively reshaping the same area? Open breakdowns in their folder of `bitwarden/tech-breakdowns`, in-flight PRs from them in the affected repos, or recent material churn in the files the change touches. High velocity raises the collision risk on Internal Open-Source and increases the value of sequencing through File a Ticket. **Scan explicitly — don't guess.** Procedure in `references/scanning-for-owning-team-work.md`. |

## Step 4: Match to a model

The recommendation is driven by inputs 1–2; inputs 3–6 are tie-breakers and escalators.

**If only the driving team's code changes**, the default isn't to pick a collaboration model — return to Step 1's escape hatch. This is internal consumption: the driving team owns the change, and the owning team's involvement is whatever their API contract dictates. If the integration is novel or security-sensitive enough to warrant a bounded one-time design or threat-model review, request that as a targeted ask — but don't reflexively add the owning team as `CODEOWNERS` or require their approval on ongoing PRs. Embedded Expert only applies if the owning team has explicitly opted to commit an engineer; otherwise it's too heavy for what's really internal work.

**If the owning team's code changes, walk the depth axis:**

| Depth       | Default                  | Escalate when                                                                                                                            |
| ----------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Surface** | **File a Ticket**        | Owning team has no capacity AND driving team has bandwidth and codebase familiarity → **Internal Open-Source**.                          |
| **Mid**     | **Internal Open-Source** | Owning team's review process is immature, OR conventions aren't documented enough for an outside PR to land cleanly → **File a Ticket**. |
| **Deep**    | **File a Ticket**        | _No escalation._ Deep-depth changes belong with the owning team; the deep context is what makes the work theirs to do.                   |

**Velocity adjustment.** If input 6 surfaced active owning-team work in the area, shift the recommendation:

- **Surface or Mid depth + active owning-team work** → shift toward **File a Ticket** so the owning team sequences the change into their work. Internal Open-Source becomes higher-risk when the conventions being coded against are themselves in flight.
- **Cross-team interfaces evolving on both sides simultaneously** → escalate to the initiative owner (or both teams' EMs if no initiative) rather than picking unilaterally. A model decided in a contested domain has a high chance of being wrong.
- **Link the in-flight breakdown(s) in the signoff-table row** so the owning team sees the relationship at signoff and the driving team sees whose roadmap the dependency now sits on.

## Step 5: Confirm the model with the owning team

**The collaboration model is a joint decision, not a unilateral driving-team call.** The driving team proposes; the owning team confirms or counter-proposes during cross-team signoff. The flow:

1. **Driving team proposes the model** during breakdown drafting, based on the change shape and the inputs from Step 3. Capture it in the signoff-table row's `Interface` cell with the reasoning ("Model: Internal Open-Source — driving team writes the PR following library conventions; UIF reviews").
2. **Owning team confirms (or counter-proposes) during signoff.** Signoff implicitly endorses the proposed model. If the owning team objects, that's a Clarifications Log entry or a Coordination notes update, not a silent signoff with a different model in mind.
3. **Counter-proposals are material design changes.** Re-circulate to anyone who's already signed off; bump `Last substantive update` on the breakdown.
4. **Mark the model as confirmed in the signoff table** once both teams have agreed. The breakdown reads `Model: Internal Open-Source (confirmed @platform-tl, 2026-05-15)` instead of just `Model: Internal Open-Source` once signoff lands.

Common counter-proposal patterns:

- Driving team proposed Internal Open-Source → owning team counter-proposes File a Ticket because the change is deeper than the driving team realized, or because conventions aren't documented enough for an outside PR.
- Driving team proposed File a Ticket → owning team counter-proposes Internal Open-Source because they don't have sprint capacity but the conventions are documented enough that a PR will land cleanly.
- Driving team proposed Internal Open-Source → owning team counter-proposes File a Ticket because the area is in active flux and they'd rather sequence the change into their own work than absorb a parallel PR.
- Driving team requested reviewers via Step 1's escape hatch → owning team counter-proposes Embedded Expert because the change is high enough risk that they want an engineer inside the integration during the build, not just at review. This is the path Embedded Expert most often arrives by: as a counter-proposal from the owning team, not a unilateral pick by the driving team.

When a counter-proposal happens, the breakdown is the right place to capture the negotiation — both teams need the record for later.

## Step 6: Output the recommendation

A useful recommendation has five parts:

1. **The model.** File a Ticket, Internal Open-Source, or (rarely) Embedded Expert — or an escape hatch from Step 1 (most commonly: "this isn't a cross-team change; the driving team owns it as internal consumption, with at most a bounded one-time review request if the integration is novel or security-sensitive"). Embedded Expert should only be recommended when the owning team has explicitly opted to commit an engineer; otherwise it's an escape-hatch case, not a model recommendation.
2. **The reasoning, traced to inputs.** Two or three sentences. Cite the depth and repetition shape; name the tie-breaker if one was used.
3. **The runner-up.** What the recommendation would have been if one input changed. This is what the team needs if the owning team pushes back during signoff.
4. **The domain-velocity findings.** What the in-flight scan surfaced (links to specific owning-team breakdowns or PRs, or "no shift — area is quiet") and how it shifted the recommendation. A recommendation that says "assuming the area is quiet, which I didn't check" is worse than one that names the scan output.
5. **The confirmation step.** Surface that the model is a proposal until the owning team signs off. Name the human who needs to confirm.

## Common Mistakes

- **The driving team picks the model unilaterally.** The driving team proposes; the owning team confirms. A model that lands in the breakdown without owning-team agreement is a proposal in disguise — and discovers as the wrong model at the worst possible time.
- **Treating File a Ticket as the low-cost option for the driving team.** File a Ticket transfers planning, breakdown, and execution load to the owning team. It's cheap on the driving team's roadmap but not on the owning team's. Confirm absorption before defaulting to it.
- **Defaulting to Internal Open-Source because the driving team wants to move fast.** The Mid-depth default assumes the owning team's review process is mature and conventions are documented. If they aren't, the PR sits in review and "move fast" produces the opposite outcome.
- **Picking Embedded Expert because the change is hard.** Embedded Expert is the heaviest model and only fits when (a) the change is in the driving team's code, (b) the owning team has explicitly committed to embedding an engineer, and (c) the driving team's success genuinely needs that engineer inside the build, not just at review. Most "we need their expertise" cases are satisfied by Step 1's escape hatch — treat as internal consumption with at most a bounded one-time targeted review. Don't default to Embedded Expert just because the change is security-critical or risky.
- **Treating consumption as a cross-team commitment.** Consuming a published API is what the API is there for. The owning team isn't responsible for reviewing every consumer's code, and adding them as ongoing `CODEOWNERS` on consumer-side files loads them with review work their API was supposed to abstract away. If the API is risky enough to need consumer-by-consumer review, that's a signal the API itself needs better defaults, guardrails, or docs — fix the API, don't tax every consumer's review process.
- **Recommending Embedded Expert without the owning team's commitment.** The owning team is the one paying the embed cost (engineer-weeks). Driving teams can't propose Embedded Expert unilaterally — it only enters the table after the owning team has volunteered or counter-proposed it. The default for "driving team's code only" is the Step 1 escape hatch.
- **Skipping Step 1.** Picking a model for a crossing that shouldn't happen turns the model into a workaround for a missing platform capability or a misshaped boundary.
- **Letting capacity drive the model.** "We'd rather write it ourselves" or "we'd rather they write it" isn't input to the model choice — change shape is. Capacity is a tie-breaker, not a driver.
- **Recommending a model without a runner-up.** Half the value of an explicit recommendation is the line of retreat — what the recommendation becomes if the assumption changes during signoff.
- **Skipping the owning-team in-flight scan.** A model that's clean on paper turns into merge-conflict purgatory when the owning team is mid-refactor on the same files. The scan (input 6, procedure in `references/scanning-for-owning-team-work.md`) is cheap; skipping it is the leading cause of "the recommended model didn't survive contact with reality."

## Reference

- [Pete Hodgson — Patterns of Cross-Team Collaboration](https://blog.thepete.net/blog/2021/06/17/patterns-of-cross-team-collaboration/) — background on the cross-team collaboration patterns this skill builds on. Bitwarden's tech-breakdown workflow adopts three: File a Ticket, Internal Open-Source, and Embedded Expert.
- `references/scanning-for-owning-team-work.md` — operational procedure for the domain-velocity scan (input 6): which folders and repos to scan, what patterns to look for, and how findings map to model shifts.
- Related: `Skill(writing-tech-breakdowns)` — names a model per cross-team impact in the breakdown's signoff table and runs the signoff cycle that confirms it. `Skill(navigating-the-initiative-funnel)` — phases involving cross-team work pick models for handoff and execution. `Skill(running-work-transitions)` — picks models for the shape of a transition (framework rollout, codebase handoff, operational responsibility move). `Skill(architecting-solutions)` (in `bitwarden-tech-lead`) — when Step 1 surfaces a deep-architecture concern, route there before picking a model.
