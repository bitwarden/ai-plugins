---
name: bitwarden-sdk-internal-review-knowledge
description: Institutional knowledge for bitwarden/sdk-internal code reviews. Use BEFORE reviewing sdk-internal PRs to understand repository-specific patterns, architectural constraints, and avoid false positives.
---

# bitwarden/sdk-internal - Code Review Knowledge

## Experiment Overview

| Item | Details |
|------|---------|
| **Repository** | [bitwarden/sdk-internal](https://github.com/bitwarden/sdk-internal) |
| **Technology Stack** | bitwarden, rust, sdk |
| **Primary Languages** | Dockerfile, Handlebars, JavaScript, Kotlin, Mustache, Rust, Shell, Swift |
| **Common Issue Categories** | Severity calibration failures, Context-blindness (codebase & social), WASM architectural patterns, Team preference conflicts, Trust boundary misunderstandings, Scope validation failures |

## Verified Detection Strategies

_Copy-paste ready commands for catching common issues._

```bash
# Before starting review: Load PR context
gh pr view <PR_NUMBER> --json title,body,files
gh pr view <PR_NUMBER> --comments
gh api repos/bitwarden/sdk-internal/pulls/<PR_NUMBER>/reviews

# Check for active discussions that should pause review
gh api repos/bitwarden/sdk-internal/pulls/<PR_NUMBER>/reviews --jq '[.[] | select(.state == "CHANGES_REQUESTED")] | length'

# Validate pattern exists before flagging as issue (high count = intentional)
rg "PATTERN" crates/ -l | wc -l

# Check documentation patterns before suggesting documentation
rg "^///|^\s*///" crates/bitwarden-ipc/src/wasm/*.rs -l | wc -l

# Check macro usage (low count = team avoids macros, DO NOT recommend)
rg "macro_rules!" crates/ -l | wc -l

# Check if file is WASM boundary (simplified errors expected)
grep -q "wasm_bindgen" "$FILE" && echo "WASM interface - expect simplified errors"

# Check for WASM generic workarounds (intentional, not tech debt)
rg "workaround.*wasm.*generic" crates/bitwarden-ipc/src/wasm/ -i

# Verify PR scope - only flag issues in changed files
gh api repos/bitwarden/sdk-internal/pulls/<PR_NUMBER>/files --jq '.[].filename'

# Check if stub PR (expect temporary scaffolding)
gh pr view <PR_NUMBER> --json body --jq .body | grep -i "stub\|scaffolding\|wip"

# Verify method/trait names in documentation match implementation
rg "fn <method_name>" crates/ --type rust

# Check trust boundary for SDK configuration fields
rg "pub struct ClientSettings" crates/bitwarden-core/src/client/client_settings.rs -A 20

# Check for JIRA ticket TODOs before flagging known issues
rg "TODO.*PM-" crates/ --type rust

# Verify cargo test passes for documentation examples
cargo test --doc

# Check if WASM test command uses correct features
cargo test --target wasm32-unknown-unknown --features wasm -p bitwarden-error

# Validate dependency declarations match feature requirements
grep "uniffi" crates/*/Cargo.toml

# Check CI workflow trigger type (workflow_dispatch = trusted context)
gh api repos/bitwarden/sdk-internal/contents/.github/workflows/<workflow>.yml | jq -r .content | base64 -d | grep "workflow_dispatch"
```

## Failed Attempts (Critical Learnings)

| Issue | Why Missed | Detection Strategy | Review Date | PR Link | Severity |
|-------|------------|-------------------|-------------|---------|----------|
| Severity calibration failure - marked findings as "critical" but described as "low impact" | Applied generic best practices without validating actual impact in specific use case | Verify against PR acceptance criteria; check if pattern exists elsewhere: `rg "PATTERN" crates/ -l \| wc -l`; CRITICAL = blocks current functionality | 2025-11-07 | [#547](https://github.com/bitwarden/sdk-internal/pull/547) | ❌ CRITICAL |
| Fabricated documentation requirements not validated against codebase | Assumed external best practices apply without surveying existing patterns | Check existing patterns: `rg "///" crates/bitwarden-ipc/src/wasm/*.rs -l \| wc -l`; check CLAUDE.md for requirements | 2025-11-07 | [#547](https://github.com/bitwarden/sdk-internal/pull/547) | ⚠️ IMPORTANT |
| Suggestion escalation anti-pattern - changed severity mid-review (suggestion → critical) | Multi-pass review edited existing comments instead of adding new threads | NEVER edit review comments to change severity after posted; add NEW comment if severity changes | 2025-11-07 | [#547](https://github.com/bitwarden/sdk-internal/pull/547) | ❌ CRITICAL |
| Recommended macros despite team anti-pattern | Didn't survey codebase for macro usage patterns | Check macro prevalence: `rg "macro_rules!" crates/ -l \| wc -l`; DO NOT recommend macros in this codebase | 2025-11-07 | [#547](https://github.com/bitwarden/sdk-internal/pull/547) | ⚠️ IMPORTANT |
| Agent-based review didn't load existing PR comments/discussions | Workflow only fetched PR metadata, not comment threads | ALWAYS load: `gh pr view <PR> --comments`; check for active discussions; PAUSE if CHANGES_REQUESTED | 2025-11-13 | [#557](https://github.com/bitwarden/sdk-internal/pull/557) | ❌ CRITICAL |
| Introduced unsolicited "(5/5)" rating system | Used generic review templates from other contexts | Only use repository's established severity markers: ❌, ⚠️, 💭, 🎨; check PR template for conventions | 2025-11-13 | [#557](https://github.com/bitwarden/sdk-internal/pull/557) | ⚠️ IMPORTANT |
| Flagged changes to files not in PR scope (Breaking API change false alarm) | Analyzed intermediate commits or working tree state vs final diff | Only flag issues in final diff: `gh api repos/bitwarden/sdk-internal/pulls/<PR>/files --jq '.[].filename'` | 2025-11-27 | [#579](https://github.com/bitwarden/sdk-internal/pull/579) | ❌ CRITICAL |
| Over-engineering AI guidance documentation with usage examples | Misunderstood CLAUDE.md purpose (AI guidance vs developer docs) | CLAUDE.md = concise architectural rules; README.md = comprehensive examples; don't add tutorials to AI guidance files | 2025-11-27 to 2025-12-01 | [#586](https://github.com/bitwarden/sdk-internal/pull/586) | ⚠️ IMPORTANT |
| WASM test command feature incompatibility not validated | Didn't verify test commands against crate feature configurations | Always validate commands against Cargo.toml features; WASM cannot use `--all-features` due to UniFFI conflicts | 2025-11-27 to 2025-12-01 | [#586](https://github.com/bitwarden/sdk-internal/pull/586) | ❌ CRITICAL |
| Over-aggressive security flagging on expected key material exposure | Didn't recognize temporary patterns acknowledged by team | Check for TODO comments and PR description acknowledging temporary patterns; don't escalate if documented | 2025-12-11 to 2025-12-19 | [#596](https://github.com/bitwarden/sdk-internal/pull/596) | ❌ CRITICAL |
| Excessive repetitive comments (188+ comments, marked as "Spam") | Generated too many similar findings without grouping | Limit to 20-30 comments per review; group similar issues; summarize repetitive patterns | 2025-12-11 to 2025-12-19 | [#596](https://github.com/bitwarden/sdk-internal/pull/596) | ❌ CRITICAL |
| Private fields in foundation PR flagged as "unusable struct" | Applied production API standards to incremental development | For stub/foundation PRs, check for TryFrom/Serde; ask about intent rather than declaring "Critical" | 2025-12-01 | [#600](https://github.com/bitwarden/sdk-internal/pull/600) | ⚠️ IMPORTANT |
| Hallucinated missing semicolon on correct code | Token prediction error not verified against actual code | Trust CI build success; don't flag phantom syntax errors that would prevent compilation | 2025-12-11 to 2025-12-12 | [#609](https://github.com/bitwarden/sdk-internal/pull/609) | ❌ CRITICAL |
| Flagged missing UniFFI attributes on unchanged files (scope creep) | Analyzed existing codebase files not modified in PR | CRITICAL: Only flag issues in modified files; use `gh api repos/<owner>/<repo>/pulls/<num>/files` | 2025-12-11 to 2025-12-12 | [#609](https://github.com/bitwarden/sdk-internal/pull/609) | ❌ CRITICAL |
| Over-calibrated security severity for internal workflow_dispatch | Applied external API security standards to internal trusted tooling | Check workflow trigger: `workflow_dispatch` = trusted maintainer context, not public API | 2025-12-11 to 2025-12-15 | [#610](https://github.com/bitwarden/sdk-internal/pull/610) | ❌ CRITICAL |
| Suggested complex validation for self-correcting workflow | Didn't recognize downstream tool (cargo-release) provides validation | Check if downstream tooling validates; focus on silent failures, not obvious fast-fails | 2025-12-11 to 2025-12-15 | [#610](https://github.com/bitwarden/sdk-internal/pull/610) | ⚠️ IMPORTANT |
| Misunderstood Cargo.lock CI check placement as error | Assumed check should be before commands, not after | Read PR description for intent; post-command checks validate developers committed synchronized lockfiles | 2025-12-17 | [#617](https://github.com/bitwarden/sdk-internal/pull/617) | ⚠️ IMPORTANT |
| Documentation example doesn't match implementation (generator vs generators) | Didn't escalate when author disagreed with factual correction | Factual corrections require objective proof; suggest `cargo test --doc` to verify; BLOCK if examples won't compile | 2025-12-17 to 2025-12-19 | [#618](https://github.com/bitwarden/sdk-internal/pull/618) | ❌ CRITICAL |
| Over-escalated security concern for SDK configuration .expect() | Misunderstood trust boundary (client-provided config vs user input) | Check if fields are controlled by SDK consumers (trusted) vs end-users (untrusted); calibrate severity accordingly | 2025-12-18 to 2025-12-19 | [#621](https://github.com/bitwarden/sdk-internal/pull/621) | ❌ CRITICAL |
| Questioned USER_AGENT duplication without checking TODO comment | Didn't read code context before flagging | Search for TODO comments with `rg "TODO.*PM-"`; check PR description for ticket references before questioning | 2025-12-18 to 2025-12-19 | [#621](https://github.com/bitwarden/sdk-internal/pull/621) | ⚠️ IMPORTANT |

## Repository Gotchas

_Architectural patterns and conventions specific to this repository._

### 1. WASM Interface Error Handling Philosophy

**Pattern**: WASM boundary code intentionally uses simplified string errors (not structured types). This is an architectural decision trading error granularity for simpler JS/WASM interop.

**Common Mistake**: Flagging string error conversions like `.map_err(|e| format!("{e:?}"))` as "loses type safety."

**Detection Strategy**: Check for `wasm_bindgen` attribute - if present, simplified errors are expected pattern. Files in `crates/*/src/wasm/` typically use this pattern.

**Impact**: Flagging this pattern wastes contributor time explaining architectural decisions and creates perception of reviewer not understanding codebase.

**References**: PR [#547](https://github.com/bitwarden/sdk-internal/pull/547)

---

### 2. Breaking Change Tolerance for Internal SDK

**Pattern**: The bitwarden/sdk-internal repository accepts breaking changes more readily than public APIs. Developers frequently state "breaking change is fine" when discussing API modifications.

**Common Mistake**: Treating internal SDK API stability with same rigor as public client APIs, flagging potential breaking changes as critical issues.

**Detection Strategy**: Repository name contains "internal" - breaking changes are acceptable and often preferred over maintaining legacy patterns.

**Impact**: Over-emphasizing API stability wastes review attention on non-issues and frustrates developers who understand the project's stability requirements.

**References**: PR [#547](https://github.com/bitwarden/sdk-internal/pull/547)

---

### 3. Generic Parameter Limitations in WASM Bindings

**Pattern**: wasm-bindgen does not handle generic parameters, requiring workarounds like type erasure, concrete type aliases, or enum-based polymorphism (runtime dispatch).

**Common Mistake**: Flagging hardcoded concrete types or enum dispatch in WASM binding layers as technical debt without recognizing these are inherent WASM interop constraints.

**Detection Strategy**: Check for `src/wasm/` path + `#[wasm_bindgen]` attribute. Look for comments mentioning "workaround" + "wasm" + "generic".

**Impact**: Flagging necessary workarounds as fixable technical debt creates confusion about whether issue is actually addressable.

**References**: PR [#547](https://github.com/bitwarden/sdk-internal/pull/547), CLAUDE.md Cross-Platform Bindings section

---

### 4. Emoji-Based Severity Markers Convention

**Pattern**: Repository has established convention for review feedback severity using specific emojis: ❌ (critical), ⚠️ (important), 🎨 (suggestions), 💭 (questions).

**Common Mistake**: Introducing alternative assessment systems like numerical ratings "(5/5)", letter grades, or custom severity scales.

**Detection Strategy**: Check `.github/pull_request_template.md` for reviewer guidelines. Only use established emoji markers.

**Impact**: Introduces cognitive overhead when reviewers must interpret multiple assessment systems. Creates confusion about issue priority.

**References**: PR [#557](https://github.com/bitwarden/sdk-internal/pull/557)

---

### 5. Macro Avoidance Preference

**Pattern**: Team prefers explicit code over macros for reducing code duplication. Low macro usage throughout codebase indicates intentional architectural decision.

**Common Mistake**: Suggesting `macro_rules!` for code deduplication without checking team preferences.

**Detection Strategy**: Check macro prevalence: `rg "macro_rules!" crates/ -l | wc -l` returns low count. DO NOT recommend macros in this codebase.

**Impact**: Wastes contributor time with disagreeable suggestions that conflict with established team preferences.

**References**: PR [#547](https://github.com/bitwarden/sdk-internal/pull/547) - User explicitly stated macro recommendations should stop

---

### 6. Stub/Scaffolding PRs Are Common and Acceptable

**Pattern**: SDK team frequently merges "stub" PRs that create crate structure and API skeletons without full implementation, test coverage, or production readiness.

**Context**:
- PR descriptions explicitly state "stub", "scaffolding", or "unblock [feature] work"
- Temporary example methods with `#[allow(unused)]` attributes are expected
- 0% test coverage accepted for stub PRs
- Human reviewers approve despite incomplete functionality

**Common Mistake**: Treating stub PRs like production-ready PRs, flagging missing tests, incomplete implementations, or temporary patterns as issues.

**Detection Strategy**:
- Check PR description for keywords: `gh pr view <PR> --json body --jq .body | grep -i "stub\|scaffolding\|wip"`
- Look for `#[allow(unused)]` attributes signaling temporary code
- Focus review on API design and structure, not completeness
- Defer test coverage and implementation concerns to future PRs

**Impact**: Excessive completeness requirements on stub PRs waste review time and frustrate authors who understand the incremental development approach.

**References**: PR [#579](https://github.com/bitwarden/sdk-internal/pull/579) - Explicit stub PR with temporary example methods

---

### 7. CLAUDE.md Files Are AI Guidance, Not Developer Documentation

**Pattern**: CLAUDE.md files in sdk-internal serve as AI guidance documentation with concise architectural rules and patterns, not comprehensive developer tutorials.

**Context**:
- Purpose: Help AI assistants understand codebase conventions
- Style: Concise "what" and "why", not exhaustive "how"
- Should NOT include: Extensive usage examples, step-by-step tutorials, comprehensive API documentation
- Should include: Architectural constraints, security/performance guidelines, critical patterns

**Common Mistake**: Suggesting to expand CLAUDE.md files with detailed usage examples, code snippets, and tutorials appropriate for developer documentation (README.md).

**Detection Strategy**:
- When reviewing CLAUDE.md files, ask: "Does this add clarity to rules/patterns, or is it a usage tutorial?"
- ✅ Clarity to existing rules, missing architectural constraints, critical guidelines
- ❌ Step-by-step tutorials, extensive code examples, comprehensive API docs

**Impact**: Understanding this distinction prevents wasted review cycles and maintains appropriate documentation scope.

**References**: PR [#586](https://github.com/bitwarden/sdk-internal/pull/586) - Author feedback: "Not really the intention here... supposed to help YOU figure out our code base better"

---

### 8. WASM Feature Compatibility Constraints

**Pattern**: WASM test commands cannot use `--all-features` flag due to feature incompatibility between WASM target and UniFFI features.

**Context**:
- Some crate features are unavailable in WASM contexts
- UniFFI feature is incompatible with WASM compilation
- Must specify individual packages with WASM-compatible features

**Common Mistake**: Using `--all-features` in WASM test commands, assuming all features are compatible.

**Detection Strategy**:
```bash
# ❌ WRONG - Will fail
cargo test --target wasm32-unknown-unknown --all-features

# ✅ CORRECT - Specify packages
cargo test --target wasm32-unknown-unknown --features wasm -p bitwarden-error -p bitwarden-threading
```

**Impact**: CRITICAL - Command will fail in CI/CD and mislead developers.

**References**: PR [#586](https://github.com/bitwarden/sdk-internal/pull/586) - dani-garcia caught WASM command incompatibility

---

### 9. Documentation Examples Must Compile

**Pattern**: Rust documentation examples in README files are compiled during `cargo test --doc` unless explicitly marked with `ignore`, `no_run`, or `compile_fail`.

**Context**:
- All code blocks in crate READMEs should compile
- Documentation examples are executable code, not pseudocode
- Discrepancies between documented APIs and actual implementation break user code

**Common Mistake**: Treating documentation examples as "illustrative" rather than verifiable, allowing method names or signatures that don't match implementation.

**Detection Strategy**:
- Verify method/trait names against implementation: `rg "fn <method_name>" crates/ --type rust`
- Suggest running `cargo test --doc` to verify examples
- Flag discrepancies as BLOCKING issues, not suggestions

**Impact**: Broken examples cause compilation errors for developers following documentation and erode trust in SDK quality.

**References**: PR [#618](https://github.com/bitwarden/sdk-internal/pull/618) - Documentation used `generators()` instead of actual `generator()` method

---

### 10. Workspace Dependency Ordering Convention

**Pattern**: Cargo.toml workspace dependencies section maintains strict separation between Bitwarden-internal crates and third-party dependencies.

**Context**:
- Bitwarden crates listed first (e.g., bitwarden-api-api, bitwarden-core, bitwarden-policies)
- Blank line separator
- Third-party crates second (e.g., async-trait, serde, uuid)

**Common Mistake**: Accidentally reorganizing third-party dependencies when adding new Bitwarden crates (often from tools like `cargo add`).

**Detection Strategy**:
- Verify Bitwarden crates are grouped together at the top
- Check that third-party dependencies remain in separate section
- Watch for unintended dependency modifications in refactoring PRs

**Impact**: Maintains clean visual separation of internal vs external dependencies; prevents accidental dependency changes.

**References**: PR [#600](https://github.com/bitwarden/sdk-internal/pull/600) - dani-garcia: "Can you move these two lines were they were? We want to keep our dependencies separated from third parties."

---

### 11. GitHub Actions `workflow_dispatch` Inputs Are Trusted Context

**Pattern**: Workflows triggered by `workflow_dispatch` with manual inputs operate in a trusted security context (internal tools executed by repository maintainers, not public APIs).

**Context**:
- Manual execution by maintainers with write access
- Inputs are trusted (self-compromise doesn't expand threat surface)
- Different security assumptions than `pull_request` or `pull_request_target` triggers

**Common Mistake**: Applying external API security validation standards (command injection prevention, input sanitization, allowlist validation) to internal workflow inputs.

**Detection Strategy**:
```bash
# Check workflow trigger type
gh api repos/bitwarden/sdk-internal/contents/.github/workflows/<workflow>.yml | jq -r .content | base64 -d | grep "workflow_dispatch"
```

**Impact**: Over-flagging security issues in trusted internal tooling creates review noise and reduces maintainer trust. Author response: "This feedback from Claude seems a bit silly."

**References**: PR [#610](https://github.com/bitwarden/sdk-internal/pull/610) - Security concerns dismissed for workflow_dispatch inputs

---

### 12. Trust Boundaries in SDK Configuration

**Pattern**: SDK library crates distinguish between client-provided configuration (trusted) and end-user input (untrusted). Configuration structs like `ClientSettings` are populated by trusted Bitwarden clients, not arbitrary users.

**Context**:
- `ClientSettings` fields populated by first-party client code
- Validation happens at HTTP API boundaries, not SDK configuration structs
- `.expect()` with descriptive messages acceptable for "should never fail" cases

**Common Mistake**: Treating all `String` fields in public APIs as potentially malicious user input, over-escalating validation gaps to CRITICAL security issues.

**Detection Strategy**:
```bash
# Check struct documentation for trust level
rg "ClientSettings" --type rust -A 20

# Check if fields are documented as controlled (e.g., "random guid generated by our devs")
rg "device_identifier|bitwarden_package_type" --type rust
```

**Impact**: Over-escalation reduces signal-to-noise ratio; SDK configuration validation gaps are SUGGESTED improvements, not CRITICAL security issues.

**References**: PR [#621](https://github.com/bitwarden/sdk-internal/pull/621) - Developer: "device_identifier is a random guid generated by our devs so it's fine"

---

### 13. Intentional Technical Debt with JIRA Ticket References

**Pattern**: Code contains TODO comments with JIRA ticket numbers (PM-XXXXX) documenting known issues and cleanup plans.

**Context**:
- TODO comments indicate tracked technical debt
- Team has existing roadmap for addressing these issues
- PR descriptions often reference related tickets

**Common Mistake**: Flagging patterns as new findings without checking if they're already tracked in JIRA.

**Detection Strategy**:
```bash
# Search for related TODO comments
rg "TODO.*PM-" crates/ --type rust

# Check PR description for ticket references
gh pr view <PR> --json body --jq .body
```

**Impact**: Appearing uninformed about team's existing technical debt management.

**References**: PR [#621](https://github.com/bitwarden/sdk-internal/pull/621) - TODO for PM-29938 already documented USER_AGENT duplication

## Methodology Improvements

_What worked and what didn't in review approaches._

### 1. Load PR Context First

**What Worked**: Prompt-based reviews that explicitly loaded PR comments and existing review threads before code analysis successfully integrated discussion context into findings.

**What Didn't Work**: Agent-based reviews that only fetched code diffs without loading comment threads appeared tone-deaf to ongoing conversations.

**Lesson**: Code reviews exist in social context. Before posting findings, ALWAYS:
1. Load PR metadata: `gh pr view <PR> --json title,body,files`
2. Load comments: `gh pr view <PR> --comments`
3. Load review history: `gh api repos/bitwarden/sdk-internal/pulls/<PR>/reviews`
4. Check for CHANGES_REQUESTED state
5. If active discussions exist, acknowledge in summary

**Applicability**: EVERY code review in repositories with active collaboration. Essential for agent-based workflows.

**Example**: PR [#557](https://github.com/bitwarden/sdk-internal/pull/557) - Prompt-based approach successfully integrated existing comments, agent-based approach did not.

---

### 2. Signal Active Discussion State

**What Worked**: Reviews that "hit the pause button" when detecting active discussions signaled to future PR readers that concerns were being actively addressed.

**What Didn't Work**: Posting comprehensive findings with "Recommendations" section as if PR was ready for final judgment when reviewers had already requested changes.

**Lesson**: Review summaries should reflect PR state. If unresolved threads or CHANGES_REQUESTED state detected, summary should state: "⚠️ Active reviewer discussions in progress. Monitoring threads before additional findings."

**Applicability**: Essential for agent-based reviews that may run automatically. Prevents "talking over" human reviewers.

**Example**: PR [#557](https://github.com/bitwarden/sdk-internal/pull/557) - Agent-based review should have flagged active review state.

---

### 3. Context-Aware Severity Assessment

**What Didn't Work**: Applying generic "best practices" severity without assessing actual impact in specific use case. Example: Flagging simplified error handling in WASM boundaries without validating whether structured errors were actually needed.

**Lesson**: Before assigning severity to any finding, explicitly validate against:
- PR/ticket acceptance criteria (does this violate stated requirements?)
- Existing codebase patterns (is this an established pattern?)
- CLAUDE.md rules (is there explicit guidance?)
- Contributor's stated context (what does PR description say?)

Use consistent severity language: CRITICAL = blocks current functionality, IMPORTANT = significant future technical debt, SUGGESTED = nice-to-have improvement.

**Applicability**: Every code review should include "severity calibration" step where findings are validated against actual context, not theoretical concerns.

**Example**: PR [#547](https://github.com/bitwarden/sdk-internal/pull/547) - Findings marked "critical" but "low impact" created confusion.

---

### 4. Reduce Chattiness - Optimize Signal-to-Noise Ratio

**What Didn't Work**: Reviews with 6+ numbered findings, multiple status indicators per finding (❌, ✅, ⚠️), separate sections for "Critical Issues", "Issues Requiring Attention", "Code Quality Observations", "Good Practices Observed" creating visual noise.

**Lesson**: Optimize for signal-to-noise ratio:
- Skip "Good Practices Observed" sections
- Don't enumerate resolved findings with status indicators
- Group by actionability ("Must Fix", "Should Consider", "Active Discussions") not finding number
- Target concise summaries focused on actionable items

**Applicability**: All automated reviews. Especially important for agent-based workflows that may post frequently.

**Example**: PR [#557](https://github.com/bitwarden/sdk-internal/pull/557) - Agent-based review was notably chattier than ideal.

---

### 5. Surface High-Signal Findings Prominently

**What Worked**: Identifying "Potential Information Leakage in Error Messages" - genuinely valuable security finding.

**What Didn't Work**: Burying the valuable finding among excessive praise comments ("strengths and good practices") and lower-value suggestions, reducing its impact and visibility.

**Lesson**: High-signal findings (security implications, actual bugs, data leakage) should be prominently surfaced and clearly separated from routine suggestions and praise. Structure reviews with clear hierarchy:
1. Security/Correctness Issues (❌ CRITICAL) - always first
2. Architectural/Maintainability Concerns (⚠️ IMPORTANT)
3. Suggestions for improvement (🎨 SUGGESTED)
4. Strengths (optional, collapsed by default)

**Applicability**: All code reviews. Signal-to-noise ratio directly impacts whether contributors trust and act on findings.

**Example**: PR [#547](https://github.com/bitwarden/sdk-internal/pull/547) - Security finding was valuable but buried in noise.

---

### 6. Verify PR Scope Before Flagging Issues

**What Didn't Work**: Flagging issues in files not modified by the PR, treating existing technical debt as new PR-introduced problems.

**What Works Better**:
1. Fetch file change list first: `gh api repos/bitwarden/sdk-internal/pulls/<PR>/files --jq '.[].filename'`
2. Only flag issues in changed files as PR-blocking
3. Label out-of-scope findings as "FUTURE IMPROVEMENT"
4. Distinguish "this PR introduces problem" from "existing code has issue"

**Lesson**: Only block PR for issues introduced IN THIS PR. Existing technical debt should be noted separately, not used to block merge.

**Applicability**: All PRs, especially critical when reviewing multi-file changes or refactoring work.

**Example**: PR [#579](https://github.com/bitwarden/sdk-internal/pull/579) - Flagged changes to files not in PR scope; PR [#609](https://github.com/bitwarden/sdk-internal/pull/609) - Flagged missing UniFFI attributes on unchanged files

---

### 7. Read PR Description and Context Before Reviewing

**What Didn't Work**: Reviewing code in isolation without checking PR description, TODO comments, or linked tickets, leading to questioning already-documented patterns.

**What Works Better**:
1. Read PR description first: `gh pr view <PR> --json body,title`
2. Check for keywords: "stub", "scaffolding", "WIP", ticket references
3. Search for TODO comments in modified code: `rg "TODO" <modified_files>`
4. Understand the stated objective before evaluating completeness

**Lesson**: Code reviews exist in context. PR descriptions, TODO comments, and ticket references provide critical information about intent, known limitations, and planned follow-up work.

**Applicability**: ALL code reviews. Context research prevents false positives.

**Example**: PR [#579](https://github.com/bitwarden/sdk-internal/pull/579) - Didn't recognize stub PR from description; PR [#617](https://github.com/bitwarden/sdk-internal/pull/617) - Misunderstood CI check placement; PR [#621](https://github.com/bitwarden/sdk-internal/pull/621) - Questioned TODO-documented pattern

---

### 8. Calibrate Severity Based on Actual Threat Model

**What Didn't Work**: Over-escalating configuration validation to CRITICAL severity, using "DoS vulnerability" language for library configuration structs, applying external API security standards to internal trusted contexts.

**What Works Better**:
1. Distinguish threat scenarios:
   - Web form input → HIGH severity
   - CLI arguments → MEDIUM severity
   - SDK configuration by first-party code → LOW severity
   - Internal workflow_dispatch inputs → INFORMATIONAL

2. Use appropriate severity markers:
   - ❌ CRITICAL: Authentication bypass, SQL injection, actual DoS vectors in untrusted paths
   - ⚠️ IMPORTANT: Input validation on semi-trusted data, missing tests for security code
   - 🎨 SUGGESTED: Defensive programming improvements, better error handling
   - 💭 QUESTION: Clarifications about design decisions

3. Ask clarifying questions when threat model is unclear

**Lesson**: Severity inflation reduces credibility and causes alert fatigue. Trust boundaries matter - SDK configuration is not user input.

**Applicability**: All security-related findings. Essential for library/SDK code reviews.

**Example**: PR [#596](https://github.com/bitwarden/sdk-internal/pull/596) - Over-escalated temporary key exposure; PR [#610](https://github.com/bitwarden/sdk-internal/pull/610) - Over-flagged workflow_dispatch security; PR [#621](https://github.com/bitwarden/sdk-internal/pull/621) - Over-escalated .expect() in configuration

---

### 9. Control Comment Volume - Optimize Signal-to-Noise Ratio

**What Didn't Work**: Generating 188+ comments in single review, repeating similar issues across multiple files, excessive praise sections, multiple status indicators per finding.

**What Works Better**:
1. Limit total comments to 20-30 per review
2. Group similar issues into summary comments (if same issue appears 5+ times, it's a pattern, not individual failures)
3. Skip "Good Practices Observed" sections
4. Focus on actionable items only
5. If issue gets no response in first round, don't re-flag in subsequent rounds

**Lesson**: Review fatigue reduces effectiveness. Human reviewers marked repetitive comments as "Spam" when volume became counterproductive.

**Applicability**: All automated reviews, especially multi-round reviews.

**Example**: PR [#596](https://github.com/bitwarden/sdk-internal/pull/596) - 188+ comments created review fatigue; PR [#609](https://github.com/bitwarden/sdk-internal/pull/609) - Repeated trailing newline comment twice

---

### 10. Factual Corrections Require Stronger Assertion

**What Didn't Work**: Correctly identifying documentation didn't match implementation, but not escalating when author disagreed based on preference ("plural makes more sense").

**What Works Better**:
1. Verify against source of truth (actual code)
2. Distinguish factual corrections from stylistic suggestions
3. If author disagrees with factual issue, suggest objective test: `cargo test --doc`, `cargo check`, grep verification
4. Escalate to BLOCKING if incorrect examples will break user code
5. Use language: "This is a factual accuracy issue, not a style preference"

**Lesson**: Documentation accuracy is not a matter of opinion. When examples won't compile, block merge until resolved or explicitly acknowledged as future work.

**Applicability**: Any PR touching documentation examples, especially SDK/API documentation where developers copy-paste examples.

**Example**: PR [#618](https://github.com/bitwarden/sdk-internal/pull/618) - Documentation used `generators()` but implementation has `generator()`, merged without fix despite being incorrect

---

### 11. Don't Hallucinate Errors - Trust CI and Verify Claims

**What Didn't Work**: Flagging phantom syntax errors that would prevent compilation, claiming code has issues that don't exist in actual source.

**What Works Better**:
1. If CI builds pass, syntax is valid - don't flag phantom syntax errors
2. Before suggesting syntax fixes, verify current code doesn't already match suggestion
3. Trust compiler over token prediction for syntax validation
4. When author disputes finding with certainty ("It literally has a semi-colon"), verify your claim immediately

**Lesson**: Rust compiler is strict - compilation success means syntax is correct. Hallucinating errors severely erodes reviewer credibility.

**Applicability**: All reviews, especially critical for statically-typed languages with strict compilers.

**Example**: PR [#609](https://github.com/bitwarden/sdk-internal/pull/609) - Claimed missing semicolon on code that had proper syntax

---

### 12. Learn Repository Philosophy from Human Dismissal Patterns

**What Worked**: When human reviewers quickly dismiss concerns with brief explanations, this encodes repository-specific conventions.

**What to Capture**:
- "device_identifier is a random guid generated by our devs" → Trust boundary exists at SDK API
- "It's actually very clear + the ticket provides more context" → Check tickets before questioning TODO patterns
- "This feedback from Claude seems a bit silly" → Severity/context mismatch signal
- 4 approvals with no discussion of flagged issue → Team comfortable with this pattern

**Lesson**: Human reviewer responses are training data for repository-specific conventions. Brief dismissals indicate established patterns Claude didn't understand.

**Applicability**: Building institutional knowledge across multiple reviews. This skill itself is an example of learning from dismissal patterns.

**Example**: PR [#610](https://github.com/bitwarden/sdk-internal/pull/610) - Author's "silly feedback" comment indicates review miscalibration; PR [#621](https://github.com/bitwarden/sdk-internal/pull/621) - Quick dismissals taught trust boundaries

---

### 13. Understand Domain-Specific Tools Before Reviewing

**What Didn't Work**: Reviewing Rust documentation without understanding rustdoc's specific rendering capabilities (HTML support, callouts, doc tests).

**What Works Better**:
1. Before reviewing specialized domains, check if domain-specific knowledge is required
2. For Rust documentation: Understand rustdoc renders HTML, compiles code examples, supports doc tests
3. For GitHub Actions: Understand workflow_dispatch vs pull_request triggers, trusted vs untrusted contexts
4. When uncertain about domain pattern, phrase as question rather than issue: "Is this HTML tag intentional for rustdoc?"

**Lesson**: Specialized documentation systems have domain-specific conventions that must be understood before review. False positives waste expert time.

**Applicability**: Any specialized documentation system (rustdoc, JSDoc, JavaDoc, Sphinx) or domain-specific tooling.

**Example**: PR [#586](https://github.com/bitwarden/sdk-internal/pull/586) - Flagged valid rustdoc HTML patterns; PR [#618](https://github.com/bitwarden/sdk-internal/pull/618) - Comments dismissed by rustdoc expert
