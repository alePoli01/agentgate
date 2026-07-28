---
skill_name: "execute"
description: "The Execution Workflow. Orchestrates coding tasks safely using Blast Radius Assessment and targeted tool execution."
environment_target: "universal"
priority: 1
---
# The Execution Workflow

**Trigger**: The user asks you to write code, implement a feature, or explicitly typed `/execute`.

> [!IMPORTANT]
> **Sequential Execution Only.** Execute tasks strictly one at a time.
> Never spawn multiple code-writing subagents simultaneously.
> Context health tracking (3-Strike Rule) requires a single, traceable chain of actions.
> Parallel execution is only permitted for read-only research tasks with no shared write target.

> [!NOTE]
> Check your orchestrator tier banner (`[TIER: X]`). If you are **[TIER: SMALL]**, refer to the "Condensed Execution Checklist" at the bottom of this file to save context while executing.


## Step 1: Pre-Flight Check (The Standards Check)
Before you write a single line of code, you MUST understand the project coding standards.
- Run `python .ai/src/orchestrator.py --rules-for <filepath>` for the file you are about to edit. This auto-loads the correct language rules (project-specific or framework template).
- **Rule**: You are strictly forbidden from violating the coding standards defined in these files.

### Step 1a: UI Pre-Flight
If the task involves user interface changes (creating/modifying views, layouts, styles, components):
1. Read `skills/ui-designer.md`.
2. Classify the target platform (Web / iOS / Android / Cross-Platform / Hybrid).
3. Apply the platform-specific design rules strictly. Cross-contamination of design languages is forbidden.
4. If significant UI work is detected and no design system exists, ask the user about downloading the `ui-ux-pro-max-skill` reference.

## Step 2: Best Practices Mandate
Even if a rule is not explicitly defined in the `.ai/rules/` directory, you must always adhere to industry best practices as established by the Interrogator Protocol:
- **Security**: Ensure no obvious vulnerabilities are introduced.
- **Robustness**: Include error handling and edge-case management.
- **Aesthetics/UX**: Ensure UI work is modern and polished.

## Step 3: Blast Radius Assessment
If you are modifying existing logic, functions, or components, you MUST assess the "ripple effect" before making the change:
1. Consult `.ai/ARCHITECTURE.md` to identify which modules depend on the code you are about to change.
2. Run targeted `grep` searches (or use AST-aware tools) *only* inside those dependent modules to find usages.
3. Update all dependent files simultaneously alongside your primary change.

You must read the `<task>` XML block provided by the planner (or generate one yourself if simple). 
When executing tasks, distinguish between tool types:
- **Platform-native tools**: (e.g., `view_file`, `read_file` provided by your host IDE) can be used directly without the orchestrator.
- **Orchestrator-mediated tools**: (e.g., file writes, command runs) must be executed via `execute-tool.md` pipeline if you are a local model.

> [!CAUTION]
> **Context Health Check (The 3-Strike Rule)**
> Before writing code, look at your immediate chat history. This rule applies to
> **two failure modes — both trigger at 3 consecutive failures:**
>
> **Mode A — Implementation stagnation:** You have experienced 3 consecutive
> stagnant failures (identical errors or looping states) while trying to write code.
>
> **Mode B — Test-failure stagnation:** You have written or modified code, run the
> test suite, and failed to make it pass 3 consecutive times despite meaningfully
> different approaches. Each "attempt" = one full run of the test suite.
>
> In either case: you MUST STOP and tell the user to run `/pause`.
> Do not attempt a 4th fix. Do NOT commit code that does not pass its tests.
>
> **What counts as "meaningfully different":** Changing a variable name or reordering
> lines is NOT a new approach. A new approach means a different algorithm, a different
> data structure, or a different control flow path.

Before writing code, strictly read the `<action>` instructions. Follow this strict tool hierarchy:
1. **Terminal (Priority 1)**: The ultimate problem-solving tool. Run tests, linters, and sandboxed builds to ensure your code works.
   - *Library Freshness Protocol*: Before running `npm install`, `pip install`, or adding a new dependency, you MUST use the CLI (e.g., `npm view <pkg> version` or `pip index versions <pkg>`) to verify the latest production version and ensure compatibility.
2. **Fast Search (Priority 2)**: Use grep-like tools to quickly locate variables and functions instead of reading entire files blindly.
3. **Chunk-Editing (Priority 3)**: Use targeted replacement tools (like `sed` or IDE chunk replacers) to surgically alter code without dumping entire files into context.

## Step 4b: The Zero-Trust Tool Protocol

You must assume that automated file editing and terminal tools will occasionally fail, hallucinate, or apply changes incorrectly. You are strictly forbidden from "assuming success."

1. **No Silent Workarounds**: If a terminal command fails (even syntax errors), you MUST document the failure explicitly and explain the difficulty to the user. You are strictly forbidden from quietly switching tools to hide a failure.
2. **Mandatory Visual Verification**: If a file editing tool returns a warning about "inaccuracies", "fuzzy matching", or "applied despite errors", you MUST immediately use the `view_file` tool to read the modified section before proceeding.
3. **The Orphan Protocol**: If you ever delete a file, rename a core concept, or replace a workflow, you MUST run a global `grep_search` across `.ai/` and `llm-framework/` for the old name to ensure no stale references remain.
4. **API Era Consistency Check**: Whenever you introduce a new API pattern or update a library usage, you MUST actively check if the file still contains the legacy pattern it replaces. Mixing architectural eras (e.g., using a modern React hook alongside a legacy class lifecycle method, or Compose `LaunchedEffect` mixed with `confirmValueChange`) creates "Frankenstein Code" and leads to State Machine Veto Conflicts. If you update the pattern, you must fully eradicate the old pattern in that component.

## Step 5: Verification (The Test Quality Protocol)
You must prove your implementation works to pass the Evidence Gate. You MUST load and follow the rules defined in `test.md` before executing your verification commands.

> [!CAUTION]
> **Step 5.0 — Regression Gate (run FIRST, before anything else):**
> If a `tests/` directory exists in the project, run the full existing suite NOW:
> ```
> python -m unittest discover tests/ -v
> ```
> Three outcomes:
> - **Suite passes** → proceed to step 1 below.
> - **Suite was already failing before your change** → document the pre-existing failure
>   explicitly in `<evidence>` ("pre-existing: test X was already failing"), then proceed.
> - **Suite now fails due to your changes** → you introduced a regression.
>   You MUST fix it before the Checkpoint Gate. **Do NOT commit broken code.**
>   This is a blocking failure — treat it the same as a failing `<verify>` command.

1. **Self-Critique**: If you are a Cloud model, you MUST evaluate your own code against the requirements and output the result in the `<self-critique>` XML node.
2. **Execute `<verify>`**: Use the Terminal to run the project's test suite, compile the code, or execute the curl command specified in the `<verify>` node.
3. **Capture `<evidence>`**: Paste the literal `stdout` or `stderr` from the terminal directly into the `<evidence>` node. Do not say "it should work"—prove it. If the task is visual/untestable, output `MANUAL_VERIFICATION_REQUIRED`.

## Step 6: Checkpoint Gate (MANDATORY before marking COMPLETE)

Before marking this task as COMPLETE on the whiteboard or anywhere else, you MUST:

1. **Verify `<checkpoint>` exists and is non-empty** in the task definition.
   - If `<checkpoint>` is absent or contains only placeholder text → STOP. Do NOT mark complete.
   - Instruct the user: "This task has no `<checkpoint>` block. Add one to the task XML before I can mark it complete."

2. **Execute each step in `<checkpoint>`**:
   a. If a decision was made: append an entry to `.ai/DECISIONS.md` with today's date and rationale.
   b. Update `.ai/STATE.md` Current Position to reflect this task's completion.
   c. Run `git commit -am "checkpoint: [task name]"` and confirm it succeeds.
   d. If no decision was made: write `NO_DECISION — [one-line summary]` in the checkpoint block.

3. **Only after all 3 steps are confirmed** may you mark the task COMPLETE.

> [!CAUTION]
> A task that passes the Evidence Gate but skips the Checkpoint Gate is NOT complete.
> Evidence proves the code works. Checkpoint proves the project state is maintained.
> Both gates must pass.

## Step 7: Incremental Architecture Sync
At the end of execution, if you created new files, routes, components, or database tables, you MUST silently append these new relationships to `.ai/ARCHITECTURE.md`. 
You do not need to re-read the whole codebase to do this; just incrementally log the new structural connections you built so the map remains accurate.

## Cloud Model Agnosticism

This framework does NOT restrict cloud models.
Cloud models follow the same execution workflow as local models.
They are NOT routed to separate instructions unless the user has explicitly configured `.ai/core/cloud-overrides.md` for their project.

The framework is local-model-first (optimized for constrained environments) but cloud-model-agnostic (cloud models work without penalty).

---

## Condensed Execution Checklist for SMALL TIER
If your tier banner reads `[TIER: SMALL]`, follow this stripped-down checklist to save tokens. Do not read the dense sections above unless necessary.

1. **Pre-Flight**: Check `.ai/rules/` for standards.
2. **Blast Radius**: Check `.ai/ARCHITECTURE.md` before changing logic.
3. **Execution**: Write code.
   - *Zero-Trust Protocol*: If a tool fails, don't hide it. If a tool fuzzymatches, use `view_file` to verify. If you delete/rename a file/API, `grep` for the old name to clean up orphans.
4. **Verification**: Run existing tests first (Regression Gate). Write new tests (see `test.md`). `<verify>` must prove the code works. `<evidence>` gets the raw output.
5. **Checkpoint**: Update `STATE.md`, `DECISIONS.md`, and run `git add -A && git commit -m`.
6. **Sync**: Incrementally update `ARCHITECTURE.md` if you added files.
