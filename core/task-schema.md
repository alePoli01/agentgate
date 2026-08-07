---
type: "core_rule"
environment_target: "universal"
priority: 0
---
# Structured Task Schema

## Index
1. [The Mandatory XML Schema](#1-the-mandatory-xml-schema)
2. [Node Definitions](#2-node-definitions)
3. [The Evidence Gate Requirement](#3-the-evidence-gate-requirement)
4. [The Checkpoint Requirement](#4-the-checkpoint-requirement)

---

## 1. The Mandatory XML Schema

> [!IMPORTANT]
> **Enforced Task Structure**
> All execution and planning workflows MUST output task definitions using this exact XML structure.

```xml
<task type="auto|manual" effort="low|medium|high" skill="execute|debug|verify|refactor|test|review|security">
  <name>Clear descriptive name</name>
  <depends_on>T-xxx</depends_on>
  <priority>high|normal|low</priority>
  <files>exact/path/to/file.ts</files>
  <action>
    Specific implementation instructions.
  </action>
  <self-critique>
    [Cloud-Only] Did I actually meet the requirements? Are there edge cases?
  </self-critique>
  <verify>executable command that proves completion</verify>
  <evidence>curl output | test output | MANUAL_VERIFICATION_REQUIRED</evidence>
  <checkpoint>
    - Update .ai/DECISIONS.md if an architectural decision was made (append entry with today's date and rationale)
    - Update .ai/STATE.md Current Position to reflect this task is done
    - Update .ai/MEMORY.md to clear this task from Active TODOs
    - Run: git add -A && git commit -m "checkpoint: [task name]"
    - If no decision was made, write: NO_DECISION — [one-line summary of what was done]
  </checkpoint>
  <done>measurable acceptance criteria</done>
</task>
```

---

## 2. Node Definitions

- `type`: "auto" for tasks the agent can do itself, "manual" for tasks requiring user action (e.g., creating a cloud account).
- `effort`: "low" (simple edits), "medium" (multi-file or logical changes), "high" (architectural refactor).
- `skill`: **(NEW)** The AgentGate skill to use when executing this task. Defaults to `execute` if omitted. When the agent picks up this task, it MUST read and follow the corresponding `skills/<skill>/SKILL.md` file. Common values: `execute` (build features), `debug` (diagnose and fix bugs), `verify` (validate behavior), `refactor` (restructure without changing behavior), `test` (write tests), `review` (code review), `security` (security audit).
- `<depends_on>`: (Optional) Task ID that must be COMPLETE before this task can be routed.
- `<priority>`: (Optional) "high", "normal", or "low" to guide the orchestrator's queue.
- `<files>`: Comma-separated list of files this task targets.
- `<action>`: The precise, step-by-step instructions of what to build or change.
- `<self-critique>`: **MANDATORY for Cloud models.** The model must pause and evaluate its own proposed code against the prompt before continuing to `<evidence>`. (Local models may omit this to save tokens).
- `<verify>`: The exact terminal command (e.g., `npm test`, `curl`) the agent will run to prove the code works.
- `<evidence>`: The raw output of the verify command.
- `<checkpoint>`: **MANDATORY for all tasks.** Lists the lifecycle maintenance steps the agent must complete before marking this task COMPLETE. Must include:
  1. A DECISIONS.md entry (or explicit NO_DECISION statement)
  2. A STATE.md update
  3. A MEMORY.md update
  4. A git commit
  An agent MUST NOT mark a task COMPLETE if this block is absent, empty, or contains only placeholder text.
- `<done>`: What constitutes a successful completion of this task.

---

## 3. The Evidence Gate Requirement

> [!CAUTION]
> **No "Trust Me" Approvals.**

You are strictly forbidden from placing conversational filler (e.g., "The code is complete and looks correct", "I have verified the changes") inside the `<evidence>` block.
The `<evidence>` block MUST contain:
1. The raw `stdout`/`stderr` from the terminal (e.g., test results, compiler output).
2. Or, if the task is purely visual or un-testable via terminal, the exact string: `MANUAL_VERIFICATION_REQUIRED`.

If an agent outputs a task completion without empirical evidence, it immediately fails the Evidence Gate.
