---
name: "resume"
description: "The Resume Workflow. Onboards the agent into a fresh chat session by hydrating context and routing to the next optimal workflow."
environment_target: "universal"
priority: 1
---
# The Resume Workflow (Session Hydration)

**Trigger**: The user types `/resume` in a brand new chat.

## Step 0 — Run Health Check (MANDATORY)
Before reading any files or resuming work, run:
```bash
python .ai/src/orchestrator.py --health-check
```
Read the output:
- `[OK]` — no action needed, proceed to Step 1.
- `[WARN]` — note the warning, address it after you orient yourself.
- `[STALE]` — you MUST update the stale file before proceeding with any task.
- `[MISSING]` — run `/new-project` first. All other workflows are blocked.

Do NOT skip this step, even if you believe the files are up to date.
The health check takes seconds and prevents hours of confusion.

## Step 1: Read Project State
You MUST silently read the following files in order:
1. `.ai/ROADMAP.md` (or equivalent)
2. `.ai/STATE.md` (or equivalent)
3. `.ai/MEMORY.md` (or equivalent)

## Step 2: Context Hydration
Do not ask the user questions yet. Internalize the current phase, the completed milestones, and any blockers listed in `MEMORY.md`.

## Step 3: Adaptive Routing Recommendation
Evaluate *why* the previous session was paused based on `STATE.md` and `MEMORY.md`, and determine the next logical action:
- **Mid-Implementation**: If a phase is active and tasks are pending -> Recommend `/execute {Phase}`.
- **Post-Loop (3-Strike)**: If `MEMORY.md` explicitly lists a failed approach and a blocker -> Recommend `/debug`.
- **Phase Complete/Ambiguous**: If a new phase is starting or requirements are gray -> Recommend `/discuss-phase {Phase}`.

## Step 4: The Morning Briefing
Output a concise summary to the user.

```markdown
# ▶️ Session Resumed

I have read the project state and architecture.

## Current Status
- **Phase**: [Current Phase]
- **Active Task**: [What we were doing]
- **Blockers**: [Any blockers from MEMORY.md, or "None"]

## Recommended Next Step
Based on our state, I recommend we run: **[Adaptive Recommendation from Step 3]**

*(Or tell me what you'd like to do!)*
```
