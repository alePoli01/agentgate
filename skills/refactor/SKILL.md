---
name: "refactor"
description: "The Safe Refactoring Protocol. Ensures behavioral-preserving refactors backed by tests."
environment_target: "universal"
priority: 2
---
# The Safe Refactoring Protocol

**Trigger**: The user asks to refactor, clean up, or reorganize code, or explicitly typed `/refactor`.

> [!CAUTION]
> A refactor MUST NOT change observable behavior. If you are adding features or fixing bugs at the same time, it is NOT a refactor.

## Auto-Include Policies (MANDATORY Pre-Flight)
Before refactoring, inspect the `<files>` listed in the task. If ANY file matches a condition below, you MUST load and apply the corresponding skill.

| Condition on `<files>` | Auto-Include Skill |
|---|---|
| File is a view, screen, layout, or component (e.g., `*Screen.kt`, `*.jsx`, `*.css`, `*.xml` layout) | Read `skills/ui-designer/SKILL.md` — ensure the refactor does not break platform design consistency |
| File touches a public API, shared interface, or module boundary | Read `skills/review/SKILL.md` — run a self-review pass to confirm the API contract is unchanged |

> [!CAUTION]
> Skipping an Auto-Include Policy is a protocol violation. The detection is file-based, not judgment-based.

## Step 1: Test Suite Verification (MANDATORY)
You are strictly forbidden from refactoring code that does not have tests.
1. Use `grep_search` to find tests related to the target code.
2. If no tests exist, you MUST STOP and inform the user.
3. Offer to write tests first using the `/execute` (with `test.md` protocol) workflow. Do NOT proceed with the refactor until tests exist.

## Step 2: Baseline Regression Run
Before touching any code, run the existing tests to establish a baseline:
```bash
python -m unittest discover tests/ -v
# (or the equivalent test runner for this project)
```
- If the tests fail *before* you start, STOP. Inform the user and ask if they want to `/debug` the failure first. You cannot safely refactor broken code.

## Step 3: Blast Radius Assessment
1. Check `.ai/ARCHITECTURE.md`.
2. Determine what modules depend on the code you are refactoring.
3. Keep the refactor scope as narrow as possible. Do not boil the ocean.

## Step 4: The Refactor Execution
Make the structural or stylistic changes.
- Use surgical chunk replacements rather than rewriting entire files if possible.
- Ensure the API signature/contract remains identical unless the refactor explicitly requires changing it (and all dependents are updated simultaneously).

## Step 5: Post-Refactor Verification
Run the exact same test suite again.
- If the tests fail, you have introduced a regression. You MUST fix it immediately or revert your changes.
- Do NOT mark the task COMPLETE or commit the code if the tests do not pass.

## Step 6: Commit
Once tests are green, commit the change:
```bash
git add -A && git commit -m "refactor: [component] [reason]"
```
