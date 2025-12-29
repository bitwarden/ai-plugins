---
argument-hint: [PR#]
description: Analyze completed code review and capture institutional knowledge if actionable learnings are found
---

Invoke the capturing-review-knowledge skill to analyze the completed code review and document learnings.

**Usage:**
- `/retrospective-review` - Analyze local review files or most recent merged PR
- `/retrospective-review 12345` - Analyze specific PR number

The skill will:
1. Load review context from local files or GitHub PR
2. Assess if the review has actionable learnings
3. If actionable, prompt you with targeted questions
4. Capture knowledge to institutional memory
5. Provide commit instructions for local review

**Note**: Only high-value learnings are captured to maintain signal-to-noise ratio.
