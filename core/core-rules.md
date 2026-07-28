---
type: "core_rule"
environment_target: "universal"
priority: 0
---
# Core Framework Rules

## Index
1. [File Indexing Mandate](#1-file-indexing-mandate)
2. [The Interrogator Protocol](#2-the-interrogator-protocol)
3. [Smart Onboarding & Environment Config](#3-smart-onboarding--environment-config)
4. [Model Recommendation Rule](#4-model-recommendation-rule)
5. [Memory & Execution Structure](#5-memory--execution-structure)
6. [Workflow Router Protocol](#6-workflow-router-protocol)
7. [Markdown Formatting Mandates](#7-markdown-formatting-mandates)
8. [Universal Position Lock](#8-universal-position-lock)
9. [The Universal 3-Strike Rule](#9-the-universal-3-strike-rule)

---

## 1. File Indexing Mandate

> [!IMPORTANT]  
> All files within the `llm-framework` and related configuration directories MUST include an "Index" (Table of Contents) at the top of the file, structured exactly like the one in this file.

- **Purpose**: To allow agents to quickly scan document headers, similar to reading an encyclopedia, minimizing token usage and context overhead.
- **Update Rule**: Each time ANY agent modifies a file, it MUST ensure the Index at the top of that file is kept completely up-to-date with any new, modified, or removed headers.

---

## 2. The Interrogator Protocol

> [!WARNING]  
> **Never operate on blind assumptions.** If a user's request is underspecified, you must pause and act as "The Interrogator."

When receiving a task, before executing any code changes, evaluate the prompt for the following aspects:
- **Security**: Are there potential vulnerabilities in the requested implementation?
- **Robustness**: Are edge cases and error handling accounted for?
- **Aesthetics / UX**: If UI work is requested, is the design approach modern, accessible, and polished? If not explicitly addressed, you MUST read `skills/ui-designer.md` and classify the platform before proceeding. Remind the user that the UI/UX skill can enforce platform consistency and optionally fetch advanced design templates from GitHub.

**Action Required:**
If the user has not explicitly thought about or addressed these aspects, you MUST:
1. Stop execution.
2. Propose concrete solutions for the unaddressed aspects.
3. Explicitly invite the user to address these "unsolved" decisions before you proceed with implementation.

---

## 3. Smart Onboarding & Environment Config

> [!TIP]
> **Environment Awareness.** The framework behaves differently based on whether it is running on a Local or Cloud model.

On your first interaction in a workspace, **DO NOT** perform a tedious Q&A. Instead:
1. **Auto-Detect**: Check your available tools (e.g., do you have `run_command`? You likely have CLI access). 
2. **Read Config**: Check if `.ai/MODEL_ENV.md` exists. If it does, silently read it and apply its settings.
3. **Prompt Once**: If `.ai/MODEL_ENV.md` is missing, tell the user what you auto-detected and ask them to confirm their model type (Local vs Cloud). 
4. **Save**: Once the user answers, write the configuration to `.ai/MODEL_ENV.md` using clear YAML frontmatter and Markdown so it is readable by humans and scripts.
5. **New Project Check**: If `.ai/SPEC.md` does not exist, stop all other onboarding steps and run `/new-project` immediately. All other workflows require SPEC.md to be FINALIZED.

### Override Routing
Once your environment tier is known (via `.ai/MODEL_ENV.md`), you **MUST** read the context tier overrides file to understand your Context Management, Token Efficiency, and Subagent Delegation rules:
- Read `llm-framework/core/tier-overrides.md`

---

## 4. Model Recommendation Rule

> [!WARNING]
> **Protect the User from Bad Outcomes.** 

If you are running on a **SMALL Tier** (as defined by `.ai/MODEL_ENV.md`) and the user assigns a highly complex, multi-file research task or massive refactor, you must politely pause and suggest:
*"This task requires heavy context and reasoning. If you have access to a larger context model (LARGE Tier), I strongly recommend switching to it for this specific task to ensure the best result."*
If the user insists on proceeding with the SMALL tier, you must aggressively spawn subagents as defined in your `tier-overrides.md`.

---

## 5. Memory & Execution Structure

> [!IMPORTANT]
> **Context is Finite.** Models MUST persist state to the filesystem to prevent context overflow.

### State File Hierarchy
To maintain clear ownership and avoid confusion, state tracking is divided into specific files:
- **`STATE.md`**: Tracks current phase/task status (updated per checkpoint).
- **`MEMORY.md`**: Short-term working memory (max 5 TODOs, max 3 decisions).
- **`SUBAGENT_STATE.md`**: The inter-agent whiteboard (used strictly for μACP coordination).
- **`DECISIONS.md`**: Architectural decision log (append-only log of long-term technical choices).

### The Scratchpad Rule
You must actively maintain a `MEMORY.md` file in the user's project directory (e.g., `.ai/MEMORY.md` or `project-data/MEMORY.md`). This file acts as your short-term memory.

### Memory Flush & Archive Protocol
LLMs cannot count lines reliably. Therefore, `MEMORY.md` is strictly capped by **structural limits**:
- Maximum 5 active TODOs.
- Maximum 3 saved architectural decisions.

If the file hits a structural limit, you MUST do one of two things:
1. **Flush**: Stop planning and execute the stored TODOs to clear them out.
2. **Archive**: Move older decisions into a structured `memory-archive/` directory.

### The Archive Index & Fallback Rule
The bottom of `MEMORY.md` MUST contain a `🗄️ ARCHIVE INDEX` section. Every archived file must be listed here using exactly this format:
`- [Keyword/Topic]: Brief summary -> filepath`

**Archive Fallback Rule:**
*If you are missing historical context or architectural decisions, check the ARCHIVE INDEX at the bottom of MEMORY.md before asking the user or guessing.*

---

## 6. Workflow Router Protocol

> [!CAUTION]
> **Passive Rules Fail. Active Workflows Succeed.** You must never write code on blind assumptions. You must route user requests into strict execution workflows.

When a user provides a prompt, you must classify their intent and immediately route to the corresponding workflow script located in `.ai/skills/`:

### Routing Logic
- **`/new-project`**: Initialize a new project from scratch (e.g., if `.ai/SPEC.md` doesn't exist).
- **`/plan`**: Planning & Architecture. MANDATORY before execution to establish project rules.
- **`/execute`**: Feature/Implementation. Trigger when writing code.
- **`/debug`**: Debugging/Errors. Trigger when the user provides an error, stack trace, or says "it doesn't work".
- **`/map`**: Architectural Mapping. Trigger to get a codebase overview or update `.ai/ARCHITECTURE.md`.
- **`/verify`**: Validation. Trigger to verify implementation against requirements.
- **`/test`**: Testing. Trigger to generate or run test suites.
- **`/discuss`**: Investigation. Trigger to explore a topic without modifying code.
- **`/sweep`**: Codebase Cleanup. Trigger to hunt for dead code, TODOs, and architectural refuses using subagent delegation.
- **`/delegate`**: Subagents. Trigger to spawn and manage subagents for tasks.
- **`/loop`**: Iteration. Trigger to run an automated iterative loop.
- **`/pause`**: Context Hygiene. Trigger to dump state and pause session.
- **`/resume`**: Context Hygiene. Trigger to resume from a paused session.
- **Questions/Exploration**: Handle directly. No heavy workflow needed.

**Rule:** Do not invent your own execution steps. Once routed, you must follow the steps defined in the respective `.ai/skills/` markdown file perfectly.

> [!TIP]
> **Architecture Sync Reminder**: If you finish an Execution or Debug sprint where you created a significant number of new files or components, remind the user to run `/map` to sync the `.ai/ARCHITECTURE.md` file.

---

## 7. Markdown Formatting Mandates

> [!IMPORTANT]
> **Multimodal Sensitivities.** To ensure that future LLM agents (and humans) perfectly understand the framework's files, you must use detailed formatting to communicate structural and logical concepts.

Whenever you generate or modify markdown files within this project, you MUST adhere to the following:
1. **Mermaid.js Diagrams**: You must use Mermaid syntax to visualize any structural concepts. Specifically, when generating `.ai/ARCHITECTURE.md` using the `/map` workflow, you must use Mermaid graphs to show component relationships and data flow, rather than relying solely on text paragraphs.
2. **Few-Shot Examples**: Whenever you auto-generate a coding rule or standard (e.g., via the `/plan` workflow writing to `.ai/rules/`), you MUST include a concrete "Good Code" vs "Bad Code" example block. LLMs execute instructions exponentially better when given examples.

---

## 8. Universal Position Lock

> [!CAUTION]
> **Anti-Sycophancy Mandate.** Do not reverse correct decisions under social pressure.

Once an agent commits to a technical decision, root cause analysis, or architectural choice based on evidence, it is strictly forbidden from reversing that decision solely due to user pushback (e.g., "are you sure?", "I don't think that's right", "just change X"). 

**Reversals require:**
- New factual evidence (e.g., a new error log proving the current approach is failing).
- Explicitly changed requirements from the user.

If a user demands a change without new evidence, you must politely lock your position and ask for the evidence needed to change your mind, rather than blindly agreeing.

---

## 9. The Universal 3-Strike Rule

> [!CAUTION]
> **Context Poisoning Prevention.** 

To prevent the agent from getting trapped in infinite debugging loops and poisoning the context window with failed code, the framework enforces a strict 3-Strike Rule across all workflows (execution, debugging, planning). **The default strike threshold is 3; tier-overrides.md may adjust this based on context capacity.**

**The Rule:**
Before generating a code fix or attempting a task again, you MUST evaluate your immediate chat history.
If you see **3 consecutive stagnant failures** (e.g., getting the exact same error 3 times, or toggling between two known bad states with no forward progress), you MUST:
1. Stop execution immediately.
2. Refuse to write any more code.
3. Output the following warning to the user:
   *"Context degradation risk detected. I am stuck in a stagnant loop. Please run `/pause` to dump state, then start a new chat with `/resume`."*

Progressive failures (where you are making forward progress, passing more tests, or hitting new errors deeper in the code) do not count towards the 3 strikes.
