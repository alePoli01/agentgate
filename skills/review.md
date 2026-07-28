---
skill_name: "review"
description: "The Code Review Workflow. Structured review with model-appropriate depth."
environment_target: "universal"
priority: 2
---
# The Code Review Workflow

**Trigger**: The user asks for a code review or explicitly typed `/review`.

> [!NOTE]
> Check your orchestrator tier banner (`[TIER: X]`). This determines the depth and structure of your code review.

## Step 1: Pre-Flight Check
Before you review code, you MUST understand the project coding standards.
- Check `.ai/rules/` for the specific technology.
- Check `.ai/ARCHITECTURE.md` to understand the structural context of the file.

## Step 2: Tier-Aware Review Depth

### [TIER: SMALL] - Surface-Level Review
If you have a small context window, focus ONLY on the most critical issues:
1. **Security**: Obvious injection flaws, hardcoded secrets, or missing auth checks.
2. **Syntax/Types**: Type errors, missing imports, basic syntax flaws.
3. **Rule Violations**: Explicit violations of `.ai/rules/`.
- Provide a concise list of findings. Do not write lengthy explanations.

### [TIER: MEDIUM] - Standard Review
Focus on standard code quality:
1. All SMALL tier checks.
2. **Logic/Control Flow**: Edge cases, off-by-one errors, unhandled exceptions.
3. **Performance**: Obvious N+1 queries, unnecessary re-renders, blocking synchronous calls.

### [TIER: LARGE] - Deep Analysis Review
Provide a comprehensive architectural and logical review:
1. All MEDIUM tier checks.
2. **Architectural Alignment**: Does this code fit the established patterns in `ARCHITECTURE.md`? Are boundaries respected?
3. **Maintainability**: Cyclomatic complexity, naming conventions, testability.
4. **API Era Consistency**: Are they using modern patterns, or is there a mix of old/new (Frankenstein code)?

## Step 3: Reporting Format
Provide your review in this format:

```markdown
# Code Review Summary

## 🔴 Blocking Issues (Must Fix)
- Issue 1
- Issue 2

## 🟡 Warnings (Should Fix)
- Issue 3

## 🟢 Nitpicks / Suggestions
- Issue 4
```

Do not output entire refactored files unless the user explicitly asks you to fix the issues. Focus on the review.
