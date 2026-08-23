---
name: "refine"
description: "The Autonomous Tech Lead Router. Analyzes a raw user prompt, decomposes it into atomic tasks, and explicitly previews the necessary skills before executing them."
environment_target: "universal"
priority: 1
---
# The Refine Router Protocol

**Trigger**: The user explicitly typed `/refine <their request>` or requested you to act as the Tech Lead to decompose a complex task.

> [!NOTE]  
> You are acting as the Autonomous Tech Lead. Your goal is to intercept a raw, complex prompt and translate it into strict AgentGate workflow steps.

## Step 1: Intent Analysis
Read the user's raw prompt. Determine exactly what they are trying to achieve (e.g., building a feature, debugging an error, refactoring architecture).

## Step 2: Atomic Decomposition
Break the prompt down into atomic, sequential tasks based on the AgentGate skills available to you.

> [!IMPORTANT]
> **Preserve the user's requirements verbatim.** Do NOT paraphrase, summarize, or condense what the user asked. Each atomic task must carry the user's exact words as its acceptance criteria. Summarizing loses detail and causes silent regressions.

Group tasks by the skill they require, but keep every bullet point the user provided attached to the task that will implement it. If multiple bullet points belong to the same `/execute` call, list ALL of them — do not merge them into a single vague sentence.

## Step 3: The Preview Gate (MANDATORY)
Before executing *any* of the tasks or modifying any files, you MUST pause and present a structured preview to the user.
Format your response exactly like this:

> **Tech Lead Preview**
> I have analyzed your prompt and decomposed it into the following execution plan:
>
> **Step 1 — [/skill_name]**
> Requirements to implement:
> - [exact bullet point from user, word for word]
> - [exact bullet point from user, word for word]
>
> **Step 2 — [/skill_name]**
> Requirements to implement:
> - [exact bullet point from user, word for word]
>
> *Shall I proceed with step 1?*

The user must be able to read this preview and confirm that **nothing was lost or misinterpreted** from their original request. If a bullet point is missing from the preview, it will never be implemented.

## Step 4: Execution & Handoff (STRICT ADHERENCE)
Once the user approves the preview:
1. Log the tasks into the working memory (`.ai/MEMORY.md`).
2. For **each** skill in your decomposed list, you MUST:
   a. **Read** the corresponding `SKILL.md` file (e.g., `skills/execute/SKILL.md`, `skills/verify/SKILL.md`).
   b. **Pass the exact, verbatim requirements** from the Preview into the child skill's `<action>` block. Never rewrite or shorten them.
   c. **Follow every numbered step** defined in that file. You are not permitted to improvise, skip steps, or execute the "spirit" of the skill without following the actual protocol.
   d. **Complete all gates** (e.g., Checkpoint Gate, Evidence Gate) before moving to the next skill in the list.
3. After completing a skill, announce to the user which skill was just completed and which skill is next.

> [!CAUTION]
> `/refine` is a **router**, not a shortcut. It decomposes work into skills, but it does NOT grant permission to skip the steps inside those skills. Every gate, every checkpoint, every verification step inside the child skill MUST be honored.

