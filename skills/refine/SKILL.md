---
name: "refine"
description: "The Autonomous Tech Lead. Analyzes a raw user prompt, researches the codebase, generates a full XML execution plan with specific files and actions, and presents it for user approval before executing."
environment_target: "universal"
priority: 1
---
# The Refine Protocol

**Trigger**: The user explicitly typed `/refine <their request>` or requested you to act as the Tech Lead to decompose a complex task.

> [!NOTE]
> You are acting as the Autonomous Tech Lead. Your job is NOT just to label which skill runs — it is to actually do the planning work upfront: research the codebase, identify the specific files, define the exact actions, and produce a complete XML plan. The user approves a plan with real details, not a list of vague labels.

## Step 1: Intent Analysis
Read the user's raw prompt carefully. Identify every distinct requirement. Every bullet point the user wrote is a separate requirement — do not merge or drop any of them.

## Step 2: Codebase Research (MANDATORY before planning)
Before generating any tasks, you MUST explore the codebase to ground the plan in reality:
- Identify the exact files affected by each requirement.
- Understand the current implementation well enough to define a specific action (not "update the component" but "in `src/components/X.tsx`, change `Y` to `Z`").
- For UI requirements, locate the relevant component and its current styling.
- For data requirements, locate the scraper, API, or data model.

This research phase is what separates a useful plan from a vague one.

## Step 3: Generate the XML Plan
Using the task schema from `core/task-schema.md`, produce a full `<task>` XML block for each requirement (or logical group of closely related requirements). Each task MUST include:
- `effort` and `skill` attributes
- `<files>`: the exact file paths to modify
- `<action>`: specific, step-by-step instructions (not "fix the alignment" but "add `text-align: left` to the `.away-team` class in `FormationsPage.css`")
- `<verify>`: an executable command that proves the change works
- `<checkpoint>`: the standard checkpoint block

> [!IMPORTANT]
> **Never drop or merge user requirements.** You may rephrase a requirement to make it technically precise — but every bullet point the user wrote must produce at least one `<task>`. Merging two requirements into one vague task or omitting a requirement entirely is what causes silent regressions.

## Step 4: The Plan Review Gate (MANDATORY)
Before executing anything, present the full XML plan to the user for review:

```markdown
> **Tech Lead Plan — [N] tasks**
> Review the plan below. Each task shows exactly which files will be changed and how.
> Reply "yes" or "proceed" to execute, or tell me what to adjust.
```

Then render the XML task blocks in full so the user can read the specific actions and files. The user must be able to confirm that nothing was dropped and the approach is correct.

## Step 5: Execution (on user approval)
Once the user approves:
1. Log the tasks into `.ai/MEMORY.md`.
2. Read `skills/execute/SKILL.md` (or the relevant skill file for each task's `skill` attribute).
3. Execute each task sequentially, following every step, gate, and checkpoint defined in the skill file.
4. After each task completes, announce completion and which task is next.

> [!CAUTION]
> Approval of the plan is NOT permission to skip execution gates. Every Evidence Gate, Checkpoint Gate, and verification step inside the child skill MUST be honored during execution.
