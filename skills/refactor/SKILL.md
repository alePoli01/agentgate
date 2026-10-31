---
name: "refactor"
description: "The Safe Refactoring Protocol. Ensures behavioral-preserving refactors and monolith decomposition backed by tests."
environment_target: "universal"
priority: 2
---
# The Safe Refactoring Protocol

**Trigger**: The user asks to refactor, clean up, or reorganize code, explicitly typed `/refactor`, or a Workflow Hook in `/debug` or `/execute` detected a file exceeding ~300 lines.

> [!CAUTION]
> A refactor MUST NOT change observable behavior. If you are adding features or fixing bugs at the same time, it is NOT a refactor.

## Auto-Include Policies (MANDATORY Pre-Flight)
Before refactoring, inspect the `**Files:**` listed in the task. If ANY file matches a condition below, you MUST load and apply the corresponding skill.

| Condition on `**Files:**` | Auto-Include Skill |
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

## Step 3: Cohesion & Blast Radius Assessment
1. **Check `.ai/ARCHITECTURE.md`**: Determine what external modules depend on the file you are refactoring.
2. **Cohesion Analysis (When splitting a >300-line file)**:
   - List all functions/methods inside the file and group them by responsibility (e.g., in an API client file: session/auth management vs. raw HTML/JSON parsing helpers vs. data normalization).
   - Decide which functions belong to the file's core responsibility and which cohesive group of helper functions should be extracted into a dedicated module (e.g. extracting HTML parsers from `fantacalcio_client.py` into `fantacalcio_parsers.py`).
   - Verify dependency direction: extracted modules must NEVER import back from the parent file (zero circular imports).
3. Keep the refactor scope focused on the target file and its extracted modules. Do not boil the ocean.

## Step 4: The Refactor Execution
Make the structural or stylistic changes.
- Extract the identified cohesive function groups into their new module(s) and import them cleanly into the original file.
- Preserve existing public signatures/re-exports on the original module if external callers or tests import them directly, so the external contract remains 100% compatible.

## Step 5: Post-Refactor Verification
Run the exact same test suite again.
- If the tests fail, you have introduced a regression. You MUST fix it immediately or revert your changes.
- Verify that all resulting files are now under the ~300-line modularity threshold (`core-rules §11`).
- Do NOT mark the task COMPLETE or commit the code if the tests do not pass.

## Step 6: Commit & Architecture Sync
Once tests are green:
1. Update `.ai/ARCHITECTURE.md` if new modules were created.
2. Commit the change:
```bash
git add -A && git commit -m "refactor: [component] [reason]"
```

## Workflow Hooks (Conditional Internal Skill Invocations)
These hooks fire automatically at specific points during refactoring when conditions are met.

| Trigger Condition | Invoke | Action |
|---|---|---|
| Step 4 — if function signatures, class names, or module boundaries changed | `/document` | Read `skills/document/SKILL.md`. Update all affected docstrings so documentation does not go stale |
| Step 5 — if the refactor touched >5 files | `/auditor` | Spawn an `/auditor` subagent via `/delegate` to run a compliance check against `SPEC.md` and confirm the refactor did not violate requirements |
