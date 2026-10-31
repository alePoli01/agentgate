---
name: "execute"
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

## Auto-Include Policies (MANDATORY Pre-Flight)
Before executing, inspect the `**Files:**` listed in the task. If ANY file matches a condition below, you MUST load and apply the corresponding skill. This is NOT optional.

| Condition on `**Files:**` | Auto-Include Skill |
|---|---|
| File is a view, screen, layout, component, or stylesheet (e.g., `*Screen.kt`, `*View.kt`, `*.jsx`, `*.tsx`, `*.html`, `*.css`, `*.xml` layout) | Read `skills/ui-designer/SKILL.md` and apply its platform-specific rules to all UI code written |
| File touches authentication, crypto, API keys, tokens, passwords, or user input validation | Read `skills/security/SKILL.md` and apply its rules before writing any logic |
| Task modifies a public API, shared interface, or exported function/component used by other modules | Read `skills/review/SKILL.md` and run a self-review pass on the output before the Checkpoint Gate |

> [!CAUTION]
> Skipping an Auto-Include Policy because the task "seems simple" is a protocol violation. The detection is file-based, not judgment-based. If the file matches, the skill loads.

## Step 1: Pre-Flight Check (Standards & Decisions Lock)
Before you write a single line of code, you MUST understand the project coding standards and prior architectural decisions:
- Run `python .ai/src/orchestrator.py --rules-for <filepath>` for the file you are about to edit. This auto-loads the correct language rules (project-specific or framework template).
- Read `.ai/DECISIONS.md` to verify all locked architectural decisions, polling intervals, caching rules, and constraints.
- **Rule**: You are strictly forbidden from violating the coding standards or overriding user-approved decisions in `.ai/DECISIONS.md`.

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
1. **Semantic Awareness**: Consult `.ai/ARCHITECTURE.md` to understand high-level architectural dependencies (e.g., if you change the DB schema, the API layer will break). Do not assume this file contains every granular dependency.
2. **Codebase-Wide Verification**: You MUST run a global `grep` search across the entire project for the specific function name, class, or component you are modifying to find all actual usages. Do NOT restrict your search only to the modules listed in the architecture file.
3. **Atomic Updates**: Update all dependent files simultaneously alongside your primary change to prevent breaking the build.


You must read the Structured Markdown Task block provided by the planner (or generate one yourself using `core/task-schema.md` if simple).

## Step 2b: Effort-Based Behavior
Check the `Effort` column in the task's metadata table. Your workflow adapts based on the effort level:

| Effort | Blast Radius Check | Self-Critique (4-Point Audit) | Architecture Sync |
|---|---|---|---|
| `low` | Skip (unless files touch >2 modules) | Skip | Skip |
| `medium` | Required | **Required** | Required if new files created |
| `high` | Required + spawn `/researcher` subagent if >3 files in blast radius | **Required** | Always required |


> [!IMPORTANT]
> **Smart Dispatcher Rule**: Check the `Skill` column in the task's metadata table. If it is specified and is NOT `/execute` (e.g., `/debug`, `/refactor`, `/verify`), you MUST immediately STOP reading this file, load the corresponding `skills/<skill>/SKILL.md` file, and follow its workflow instead.

When executing tasks, distinguish between tool types:
- **Platform-native tools**: (e.g., `view_file`, `read_file` provided by your host IDE) can be used directly without the orchestrator.
- **Orchestrator-mediated tools**: (e.g., file writes, command runs) must be executed via `execute-tool.md` pipeline if you are a Small tier model.

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

Before writing code, strictly read the `### Action` instructions. Follow this strict tool hierarchy:
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
>   explicitly in `### Evidence` ("pre-existing: test X was already failing"), then proceed.
> - **Suite now fails due to your changes** → you introduced a regression.
>   You MUST fix it before the Checkpoint Gate. **Do NOT commit broken code.**
>   This is a blocking failure — treat it the same as a failing `Verify Command`.

1. **Self-Critique (4-Point Implementation & Modularity Audit)**: For `medium` and `high` effort tasks, you MUST inspect the actual code you just wrote and output a `### Self-Critique (4-Point Audit)` Markdown section answering these four checks before running `Verify Command`:
   - **Check 1 — Docstring/Comment vs. Code (Anti-Stubbing)**: Read every comment and docstring in the files you edited. Is every branch, condition, or schedule described in your comments actually implemented in the code below it? (Writing a comment describing a 6h/90s condition and then calling a 1-line function unconditionally is a critical failure).
   - **Check 2 — Constants, Cache & Test-Data Isolation**: Compare your code against `.ai/DECISIONS.md` and `### Action`. Did you preserve the user's exact intervals and caching strategy? Confirm you did NOT leave `force=True` or cache-bypass flags hardcoded in background jobs, NEVER fell back to test fixtures (`fixtures/`, `real_fixtures/`, `mock_*`) inside production code, and isolated all test disk writes via `tmp_path` so tests never touch production state files.
   - **Check 3 — External API & Scheduler Safety**: If your code schedules a background task, loop, or external API/scraper call, verify that off-hours guards, TTL caching, and rate limits are active in code and explicitly asserted in the test suite.
   - **Check 4 — Modularity & Separation of Concerns (core-rules §11)**:
     - *New Code*: Did you separate distinct layers (e.g. API clients, business logic, endpoints, models) into dedicated files? Are new files under ~300 lines and functions under ~50 lines?
     - *Existing Code*: Did you avoid performing an unsolicited, inline refactoring of an existing monolithic file while writing the feature? If adding a modified file caused it to exceed ~300 lines, finish verification first and then trigger the **`/refactor` Workflow Hook** below to analyze the file and extract cohesive functions into a separate module.
2. **Execute `Verify Command`**: Use the Terminal to run the project's test suite, compile the code, or execute the command specified in `### Verification`.
3. **Capture `### Evidence`**: Paste the literal `stdout` or `stderr` from the terminal directly into a `### Evidence` code block. Do not say "it should work"—prove it. If the task is visual/untestable, output `MANUAL_VERIFICATION_REQUIRED`.

> [!CAUTION]
> **Step 5.4 — Production Build Gate (compiled projects only):**
> If the project uses a compiled language or framework (Next.js, TypeScript, Android/Kotlin, iOS/Swift, Java, Go, Rust, etc.), the `Verify Command` MUST use the **production build**, not the development server.
>
> | Stack | Required verify command | NOT acceptable |
> |---|---|---|
> | Next.js / TypeScript | `npm run build` | `npm run dev` (skips type-checking) |
> | Android | `./gradlew assembleRelease` | Running on emulator only |
> | iOS/Swift | `xcodebuild -scheme X build` | Running in simulator only |
> | Python | `python -m py_compile` + tests | Running the script manually |
>
> The development server (`npm run dev`, `gradle run`, etc.) does not perform full type checking or dead-code analysis. A task that only passes the dev server has **NOT passed the Evidence Gate** for compiled projects.


## Step 6: Checkpoint Gate (MANDATORY before marking COMPLETE)

Before marking this task as COMPLETE on the whiteboard or anywhere else, you MUST:

1. **Verify `### Checkpoint` exists and is non-empty** in the task definition.
   - If `### Checkpoint` is absent or contains only placeholder text → STOP. Do NOT mark complete.
   - Instruct the user: "This task has no `### Checkpoint` section. Add one to the task before I can mark it complete."

2. **Execute each step in `### Checkpoint`**:
   a. If a decision was made: append an entry to `.ai/DECISIONS.md` with today's date and rationale.
   b. Update `.ai/STATE.md` Current Position to reflect this task's completion.
   c. Update `.ai/MEMORY.md` to check off or remove this task from Active TODOs, and log any decisions in Active Decisions.
   d. Run `git commit -am "checkpoint: [task name]"` and confirm it succeeds.
   e. If no decision was made: write `NO_DECISION — [one-line summary]` in the checkpoint report.

3. **Only after all steps are confirmed** may you mark the task COMPLETE.

> [!CAUTION]
> A task that passes the Evidence Gate but skips the Checkpoint Gate is NOT complete.
> Evidence proves the code works. Checkpoint proves the project state is maintained.
> Both gates must pass.

## Step 7: Incremental Architecture Sync
At the end of execution, if you created new files, routes, components, or database tables, you MUST silently append these new relationships to `.ai/ARCHITECTURE.md`. 
You do not need to re-read the whole codebase to do this; just incrementally log the new structural connections you built so the map remains accurate.

## Step 8: Handoff
Once execution and the Checkpoint Gate are fully complete, print the following handoff message:

```markdown
> **AgentGate ► EXECUTION COMPLETE**
> ✓ Tests passed and verified
> ✓ `.ai/STATE.md` and `.ai/MEMORY.md` updated
> ✓ Incremental `.ai/ARCHITECTURE.md` sync complete
>
> **NEXT STEP:** Provide your next instruction or run `/plan` for the next phase.
```

## Workflow Hooks (Conditional Internal Skill Invocations)
These hooks fire automatically at specific points during execution when conditions are met.

| Trigger Condition | Invoke | Action |
|---|---|---|
| After Verification (Step 5) — if any modified file exceeds ~300 lines or mixes multiple responsibilities | `/refactor` | Read `skills/refactor/SKILL.md`. Analyze the file's cohesion: determine which functions belong in the file vs. which should be extracted into dedicated modules, and execute the safe refactoring with tests green |
| After Checkpoint Gate (Step 6) — if you created new public functions, APIs, or classes | `/document` | Read `skills/document/SKILL.md`. Generate inline docstrings and update README if applicable |
| Step 3 (Blast Radius) — if you are **[TIER: SMALL]** and >3 files are in the blast radius | `/researcher` | Delegate blast-radius exploration to a read-only `/researcher` subagent via `/delegate` to preserve your main context |


---

## Condensed Execution Checklist for SMALL TIER
If your tier banner reads `[TIER: SMALL]`, follow this stripped-down checklist to save tokens. Do not read the dense sections above unless necessary.

1. **Pre-Flight**: Check `.ai/rules/` for standards and `.ai/DECISIONS.md` for locked decisions.
2. **Blast Radius**: Check `.ai/ARCHITECTURE.md` before changing logic.
3. **Execution**: Write code.
   - *Zero-Trust Protocol*: If a tool fails, don't hide it. If a tool fuzzymatches, use `view_file` to verify. If you delete/rename a file/API, `grep` for the old name to clean up orphans.
4. **Verification**: Run existing tests first (Regression Gate). Verify docstrings match actual code and no `force=True` or unrequested timers exist. Write new tests (see `test.md`). `Verify Command` must prove the code works. `### Evidence` gets the raw output.
5. **Checkpoint**: Update `STATE.md`, `DECISIONS.md`, and run `git add -A && git commit -m`.
6. **Sync**: Incrementally update `ARCHITECTURE.md` if you added files.
