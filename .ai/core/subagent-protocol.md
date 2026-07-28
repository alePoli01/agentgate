---
type: "core_rule"
environment_target: "universal"
priority: 0
---
# Subagent Protocol Architecture

## Index
1. [Teamwork Theory (Shared Mental Models)](#1-teamwork-theory-shared-mental-models)
2. [The μACP Strict Vocabulary](#2-the-μacp-strict-vocabulary)
3. [AgentGate Routing Engine](#3-agentgate-routing-engine)

---

> [!WARNING]
> **Subagent Delegation is strictly regulated.** Local models lack the capacity for unstructured, free-form multi-agent conversations. All subagent orchestration MUST follow the rules in this file.

## 1. Teamwork Theory (Shared Mental Models)

Agents do NOT pass massive raw chat transcripts to each other. This causes context collapse. Instead, they communicate via a **Shared Mental Model**, implemented as a digital whiteboard.

- **The Whiteboard (`.ai/SUBAGENT_STATE.md`)**: Whenever a task is delegated, the parent agent writes the current state, constraints, and explicit goal into this whiteboard file.
- **Mutual Monitoring**: Subagents are strictly partitioned. A `Coder` agent writes code, but it cannot finalize the task. An `Auditor` agent must evaluate the output against the whiteboard constraints.
- **State Read/Write**: Subagents load the whiteboard as their primary context. When they finish a task, they update the whiteboard with a succinct summary of their actions, rather than polluting the message history.

---

## 2. The μACP Strict Vocabulary

> [!IMPORTANT]
> **To prevent local models from hallucinating complex tool calls or rambling, all agent-to-agent communication is restricted to four absolute verbs.**

When interacting with the `orchestrator.py` engine or delegating tasks, you must begin your operational intent with one of these verbs:

1. **`ASK`**: Request information, delegate a sub-task, or invoke another agent.
   - *Example*: `ASK [Researcher] -> Find the API rate limit for Semantic Scholar.`
2. **`TELL`**: Provide requested information or return a completed task result.
   - *Example*: `TELL [Orchestrator] -> Task completed. File updated.`
3. **`OBSERVE`**: Read the current shared state or request a file snippet.
   - *Example*: `OBSERVE -> Read .ai/SUBAGENT_STATE.md`
4. **`PING`**: Health check or status update for long-running tasks.
   - *Example*: `PING -> Still compiling binary, 50% complete.`
5. **`FAIL`**: Explicitly signal that the delegated task cannot be completed.
   - *Example*: `FAIL [Orchestrator] -> Missing credentials for API.`

If a local model attempts an action without using this formal calculus, the orchestrator will intercept and reject the output.

---

## 3. AgentGate Routing Engine

Do not try to guess how to format a massive JSON payload to invoke a subagent. We use a **decoupled, 2-stage routing engine** (`src/orchestrator.py`) to guarantee precision.

### Stage 1: Action Decision (Routing Token)
When you decide a task needs a subagent, you output ONLY a routing token representing the target agent.
*Example output:* `ROUTE_TO_RESEARCHER`

### Stage 2: Structural Grounding
The Python `orchestrator.py` engine will intercept your token, validate that the `RESEARCHER` agent exists, and only then prompt you to write the specific `ASK` constraint for that agent. This prevents you from hallucinating agents that don't exist.
