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
- Example: "Add a login page" -> 1. `/plan` the architecture. 2. `/execute` the frontend components. 3. `/verify` the output.

## Step 3: The Preview Gate (MANDATORY)
Before executing *any* of the tasks or modifying any files, you MUST pause and present a structured preview to the user. 
Format your response exactly like this:

> **Tech Lead Preview**
> I have analyzed your prompt and decomposed it into the following execution plan:
> 1. **[/skill_name]**: [Brief description of what this step will do]
> 2. **[/skill_name]**: [Brief description of what this step will do]
> 
> *Shall I proceed with step 1?*

## Step 4: Execution & Handoff
Once the user approves the preview:
1. Log the tasks into the working memory (`.ai/MEMORY.md`).
2. Immediately launch into the first skill in your list (e.g., follow the instructions in `plan/SKILL.md` or `execute/SKILL.md`).
