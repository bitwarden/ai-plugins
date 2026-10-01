---
name: managing-feature-flags
description: 'Bitwarden''s feature-flag conventions and lifecycle — how server and clients evaluate flags, how to name and scope them, and how a release flag progresses from creation to cleanup. Use when deciding whether work needs a flag, gating a new code path, naming a flag, planning a rollout, or removing a launched one. Triggered by "feature flag", "flag this", "put it behind a flag", "LaunchDarkly", "IFeatureService", "FeatureFlagKeys", "RequireFeature", "gradual rollout", "flag cleanup", "kill switch".'
allowed-tools: Skill, Read, Glob, Grep, WebFetch(domain:contributing.bitwarden.com)
---

# Managing Feature Flags

Bitwarden holds an enterprise LaunchDarkly license and ships flag infrastructure on both server and clients. The canonical reference is the [feature flags guidance](https://contributing.bitwarden.com/contributing/feature-flags/); this skill is the operating convention layered on top of it.

A flag separates **deployment** from **release**. Code ships behind a flag at 0% and is released later by changing the flag, independent of the deploy.

## When to Flag

Flag new work by default. A flag is warranted for progressive rollouts, high-risk changes, cross-platform coordination, and merging incomplete work to mainline.

Skip the flag for simple or dependency updates, permanent architectural or database-logic changes, and anything where the flag itself would become long-term debt.

Decide **where the flag lives** — server-side, client-side, or both — before designing the change. Placement shapes the design, not the other way around.

## Flag Categories

| Category        | Lifespan                           | Examples                                   |
| --------------- | ---------------------------------- | ------------------------------------------ |
| **Release**     | Temporary; needs a retirement plan | Gating a new feature until it reaches 100% |
| **Operational** | May be permanent                   | Kill switches, infrastructure toggles      |

An un-retired release flag is tech debt owned by the team that created it. Operational flags are categorized separately and are **not** cleanup candidates — do not propose removing a kill switch as stale-flag hygiene.

## Discipline Rules

- **One flag per independently releasable feature.** Coupling separable features onto one flag recreates large-batch releases: a ready feature waits on an unready one because they share activation.
- **Default off.** Code the disabled path defensively; it is the path that runs in production first.
- **Name in kebab-case, after the feature.** `new-feature`, not `enable-new-feature` — the flag's state already carries the enable/disable sense.
- **Plan a gradual rollout,** not a binary flip. Step the percentage up with a monitoring hold at each stage rather than going 0% to 100%.

## Evaluating Flags

### Server-side (.NET)

Evaluate through the [`Bitwarden.Server.Sdk.Features`](https://github.com/bitwarden/dotnet-extensions/tree/main/extensions/Bitwarden.Server.Sdk.Features/src) package. **Do not hand-roll a flag abstraction and do not call the LaunchDarkly SDK directly.** The package wraps LaunchDarkly, is part of the core server SDK, and already ships in the larger solutions.

- Inject `IFeatureService` (and `ICurrentContext` where the evaluation is user- or org-scoped).
- Reference the key from the `FeatureFlagKeys` constants rather than a string literal.
- Read with `IsEnabled`, `GetIntVariation`, or `GetStringVariation`.
- Gate an endpoint or controller declaratively with `[RequireFeature(FeatureFlagKeys.MyFlag)]` or `.RequireFeature(FeatureFlagKeys.MyFlag)`. `FeatureFlagKeys` members are `const string`, so they are valid attribute arguments.

### Clients

Clients are simple consumers. They read flag state from the server's `/config` endpoint and **never** talk to LaunchDarkly directly.

- **Web, browser, desktop, CLI:** add the key to the `FeatureFlags` enum and read via `ConfigService` — `getFeatureFlagBool`, `getFeatureFlagString`, `getFeatureFlagNumber`.
- **Mobile:** add the constant and read via `IConfigService` — `GetFeatureFlagBoolAsync`, `GetFeatureFlagStringAsync`, `GetFeatureFlagNumberAsync`.

## Lifecycle

| Stage       | Flag state         | Who drives it        |
| ----------- | ------------------ | -------------------- |
| Created     | 0%                 | Tech lead or manager |
| Development | 0%                 | Engineer             |
| Testing     | Internal targeting | Engineer with QA     |
| Rollout     | Stepped to 100%    | Tech lead            |
| Cleanup     | Removed            | Engineer             |

Creating the LaunchDarkly flag is a manual tech-lead or manager step today. Production rollout percentages are a release decision — surface them to the tech lead rather than deciding them during implementation.

Cleanup means removing the flag check and hardcoding the winning variation, then archiving the flag in LaunchDarkly. Both halves are required; a removed code path with a live flag still reads as an active flag.

## Optional: the LaunchDarkly Plugin

The third-party [`launchdarkly`](https://github.com/launchdarkly/ai-tooling) plugin adds skills that drive LaunchDarkly over MCP. They require **both** the plugin installed and its hosted MCP server configured ([install](https://mcp.launchdarkly.com/mcp/launchdarkly/install)). Degrade gracefully if either is absent — everything above stands on its own, so never stop over a missing LaunchDarkly plugin.

| Skill                                | Use for                                                       |
| ------------------------------------ | ------------------------------------------------------------- |
| `Skill(launchdarkly-flag-discovery)` | Finding an existing flag before touching code                 |
| `Skill(launchdarkly-flag-create)`    | Gating a new or risky code path                               |
| `Skill(launchdarkly-flag-targeting)` | Toggling a flag while verifying locally                       |
| `Skill(launchdarkly-flag-cleanup)`   | Removing a launched flag and hardcoding the winning variation |
| `Skill(launchdarkly-metric-choose)`  | Picking the metric a rollout is gated on                      |
| `Skill(launchdarkly-metric-create)`  | Defining that metric when none fits                           |

`launchdarkly-flag-create` explores the repo's existing flag patterns first. In .NET server code that pattern is `Bitwarden.Server.Sdk.Features`, so steer the generated evaluation onto `IFeatureService` or `[RequireFeature]` rather than a raw SDK call.

The plugin can create the LaunchDarkly flag over MCP, but flag creation is owned by a tech lead or manager. Confirm with the owner before creating one rather than assuming authority.
