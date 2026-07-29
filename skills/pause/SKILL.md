---
name: "pause"
description: "The Pause Workflow. Executes a State Dump and Context Compression to prevent context degradation and allow safe session transfer."
environment_target: "universal"
priority: 1
---
# The Pause Workflow (Context Compression)

**Trigger**: The user asks to pause, or you hit the 3-Strike Rule and explicitly prompt the user to run `/pause`.

## Step 1: Current Problem Summary
Evaluate exactly what task you were working on and why you are pausing.
- If pausing due to a normal break: Note the exact step you are on.
- If pausing due to a 3-Strike loop: Extract the *conceptual lesson* (e.g., "Attempted X, blocked by Y"). **DO NOT** include raw failed code, stack traces, or variable dumps. Keep the poison out of the context.

## Step 2: Write to MEMORY.md
Take the conceptual lesson from Step 1 and append it to `.ai/MEMORY.md` (or the project's equivalent).
Ensure you are not violating the 5-item limit (as defined in `core-rules.md`).

## Step 3: Architecture Sync
Read the current contents of `MEMORY.md`. 
If there are any permanent, structural decisions (e.g., "Decided to use Redux instead of Context API for state management"), you MUST remove them from `MEMORY.md` and append them to `.ai/ARCHITECTURE.md` (or the project's architecture file).
This clears short-term memory while persisting structural knowledge.

## Step 4: Update STATE.md
Ensure `.ai/STATE.md` (or equivalent) accurately reflects:
- Current Phase
- Active Tasks
- Blocking issues

## Step 5: Handoff
Output a message to the user confirming the context has been compressed and saved, and that it is safe to close the chat instance.

```markdown
# ⏸️ Session Paused

State and Memory have been updated. 
Context compression is complete.

**It is now safe to close this chat.**
When you start a new chat, type `/resume` to onboard the new agent.
```
