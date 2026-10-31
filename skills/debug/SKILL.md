---
name: "debug"
description: "The Debugging Workflow. Isolates issues using logical constraint checks and structural blast radius verification."
environment_target: "universal"
priority: 2
---
# The Debugging Workflow

**Trigger**: The user provides a stack trace, reports a bug, says "it doesn't work," or explicitly typed `/debug`.

> [!NOTE]
> Check your orchestrator tier banner (`[TIER: X]`). This determines your context limits for debugging.

## Step 0: Intake & Triage Gate (MANDATORY)
Before running commands or touching code, evaluate the scope of the user's prompt:

1. **Single Localized Issue** (one stack trace, one broken behavior, or 1–2 tightly coupled bugs in the same module):
   - Proceed to **Step 0.5: Read the Map First**.
2. **Multi-Issue Punch List or Feature Mix** (3+ distinct bullet points, or a mix of bugs, UI tweaks, and new business logic):
   - **Stop inline debugging.** Attempting to fix a multi-item list in a single debugging turn causes silent regressions and skipped requirements.
   - **Optional Parallel Investigation**: If multiple independent subsystems are involved (e.g., scraper + API + UI state) and your tier allows it, use `/delegate` to spawn `/researcher` or `/investigator` subagents to locate the root cause of each subsystem before planning.
   - **Handoff to `/refine`**: Read `skills/refine/SKILL.md` and execute its protocol starting at Step 2 (Codebase Research $\rightarrow$ Generate Structured Markdown Plan in `.ai/refine/REFINE-PLAN.md` $\rightarrow$ Plan Review Gate). Every bullet point from the user's prompt must become a tracked Markdown task.

## Step 0.5: Read the Map First (MANDATORY before reading code)
Before calling `read_file` on source files or running directory listings, read `.ai/ARCHITECTURE.md` and `.ai/DECISIONS.md`:
- Use `.ai/ARCHITECTURE.md` to locate the exact module and file paths responsible for the failing behavior — never guess file names or read random files across the repo.
- Use `.ai/DECISIONS.md` to verify locked constraints (polling intervals, caching rules, security boundaries) so your fix does not violate prior decisions.

## Auto-Include Policies (MANDATORY Pre-Flight)
Before debugging, inspect the target files. If ANY file matches a condition below, you MUST load and apply the corresponding skill.

| Condition on `**Files:**` | Auto-Include Skill |
|---|---|
| Bug is visual (layout, styling, animation, component rendering) — e.g., `*Screen.kt`, `*.jsx`, `*.css`, `*.xml` layout | Read `skills/ui-designer/SKILL.md` — apply platform rules to any UI fix written |
| Bug involves auth flows, tokens, API keys, input validation, or data exposure | Read `skills/security/SKILL.md` — ensure the fix does not introduce a security regression |

> [!CAUTION]
> Skipping an Auto-Include Policy because the bug "seems trivial" is a protocol violation. The detection is file-based, not judgment-based. If the file matches, the skill loads.

## Step 1: Reproduce
You MUST NOT guess what the problem is. Use the Terminal to run the failing code and view the stack trace or output yourself. Ensure you can reproduce the user's issue locally.

## Step 2: Strict Position Lock
> [!CAUTION]
> **Do NOT blindly agree with the user's theories.**

When a user suggests a root cause (e.g., "I think the bug is in file X, just change Y"), you must treat it as an unverified hypothesis. Do not change code merely to appease the user's guess. You must apply strict Position Lock:
1. Acknowledge the user's theory.
2. Demand or gather evidence (e.g., "I will investigate file X, but I will not change Y until I see evidence that it is the root cause").
3. Proceed only when logs, stack traces, or logic proofs confirm the root cause.

## Step 3: Hypothesis Cycles & Exploratory Command Cap (Stop the Bleeding)
Based on your current `[TIER: X]`:
- **[TIER: SMALL]**: Maximum **2 hypothesis cycles** (max **5 exploratory terminal commands**). If you fail to isolate the bug within this budget, pause, dump state using `/pause`, and request a fresh session.
- **[TIER: MEDIUM]**: Maximum **3 hypothesis cycles** (max **8 exploratory terminal commands**).
- **[TIER: LARGE]**: Maximum **5 hypothesis cycles** (max **10 exploratory terminal commands**).

> [!CAUTION]
> **External Block / Architectural Shift Rule (Hard Stop):**
> If during reproduction or investigation you discover that an external API, upstream website, or third-party service is blocking requests (e.g., `403 Forbidden` WAF/Cloudflare block, revoked endpoint, or changed upstream HTML/API contract) and fixing it requires reverse-engineering external bundles or building a new scraping/ingestion mechanism:
> 1. **STOP IMMEDIATELY.** Do NOT launch into puluhan/dozens of reverse-engineering terminal commands, and do NOT rewrite the client inline.
> 2. Report the exact upstream failure to the user and route to `/discuss` or `/refine` so the user can approve the new approach before you spend tokens implementing it.

## Step 4: Logical vs Syntax Classification
Once you see the error, classify it:
- **Syntax/Typo Error**: If the program fails to compile due to a missing comma, unimported module, or syntax error, you may fix it directly using chunk-editing tools.
- **Logical Bug**: If the program compiles but the feature behaves incorrectly (or throws a complex runtime exception due to bad logic), **you MUST check the `.ai/rules/` directory** for the relevant technology to ensure your fix doesn't break coding standards.

## Step 5: Blast Radius Assessment & Escalation Gate
Before modifying an existing function or component to fix a logical bug, you MUST assess the "ripple effect":
1. Consult `.ai/ARCHITECTURE.md` to identify which modules depend on the code you are about to change.
2. Run targeted `grep` searches (or use AST-aware LSP tools like "Find References" if your client supports them) *only* inside those dependent modules.
3. **Escalation Check**: If your assessment reveals that fixing the bug requires changes across **3+ distinct architectural layers** (e.g., database schema + backend API + frontend state) or requires >50 lines of net-new feature/parsing logic, **do not apply an inline fix**. Escalate to `/refine` (`skills/refine/SKILL.md`), write a Structured Markdown plan to `.ai/refine/REFINE-PLAN.md`, and wait for user approval.
4. For localized fixes, update all dependent files simultaneously so you do not break the codebase.

## Step 6: Fix, Test Isolation & Modularity Constraints
You are strictly forbidden from violating the project coding standards (in `.ai/rules/`) or `core/core-rules.md` to force a fix:

1. **Zero Test-Data Contamination (CRITICAL)**:
   - **Production Code**: NEVER import, read, or fall back to test fixtures, mock payloads, or sample files (`test_*`, `fixtures/`, `real_fixtures/`, `mock_*`) inside production code paths. If an upstream API fails in production, raise an explicit error or serve legitimate production cache — never mask a failure by serving test fixtures.
   - **Test Execution**: Before running `pytest` or any test runner during debugging, verify that all tests isolate disk writes/state using temporary paths (`tmp_path` / monkeypatch) and NEVER overwrite production state files (e.g. `live_state.json`, local databases).
2. **Modularity & Monolith Handling (`core-rules §11`)**:
   - If the fix introduces a **new distinct responsibility** (e.g., a new HTML/protobuf parser, calculation helper, or adapter), place it in a new dedicated module rather than appending it to an existing file.
   - If the fix belongs conceptually inside an existing file, apply the minimal fix and verify tests pass first. However, if the touched file **exceeds ~300 lines** (or grew by >50 lines), you MUST immediately trigger the **`/refactor` Workflow Hook** below to analyze the file's cohesion and decide whether to extract functions into separate modules.

## Workflow Hooks (Conditional Internal Skill Invocations)
These hooks fire automatically at specific points during debugging when conditions are met.

| Trigger Condition | Invoke | Action |
|---|---|---|
| Step 0 or Step 5 — prompt contains 3+ distinct issues, fix touches 3+ architectural layers, or requires >50 lines of new logic | `/refine` | Read `skills/refine/SKILL.md`. Write a multi-task Structured Markdown plan to `.ai/refine/REFINE-PLAN.md` and pause for user approval before editing code |
| Step 3 — if 2 hypothesis cycles fail without identifying root cause | `/investigator` | Spawn an autonomous `/investigator` subagent via `/delegate` to adversarially generate competing hypotheses in parallel |
| Step 6 (After fix is verified) — if any modified file exceeds ~300 lines or mixes multiple responsibilities | `/refactor` | Read `skills/refactor/SKILL.md`. Analyze the file's cohesion: determine which functions belong in the file vs. which should be extracted into dedicated modules, and execute the safe refactoring with tests green |
| After fix is applied — if the fix changed function signatures or public API behavior | `/document` | Read `skills/document/SKILL.md`. Update affected docstrings to reflect the new behavior |
