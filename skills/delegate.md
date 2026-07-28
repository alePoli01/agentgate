---
type: "skill"
name: "delegate"
description: "Workflow for delegating tasks to subagents via the AgentGate Orchestrator"
environment_target: "universal"
---
# The Delegate Workflow (`/delegate`)

> [!NOTE]
> Check your orchestrator tier banner (`[TIER: X]`). This determines your capability for parallel subagent dispatch.

When a task requires a subagent, you MUST use this workflow. Do NOT guess subagent structures or hallucinate direct message payloads.

## Step 1: AgentGate Stage 1 (Decision)
You must first decide which agent to route to. Run the Python orchestrator with the routing token.
```bash
python .ai/src/orchestrator.py --route ROUTE_TO_<AGENT_NAME>
```
Valid agents are `RESEARCHER`, `CODER`, `AUDITOR`, `ARCHITECT`, `INVESTIGATOR`.

## Step 2: AgentGate Stage 2 (Grounding)
If Stage 1 is successful, the orchestrator will give you permission to proceed. You must construct your payload using the strict μACP vocabulary (`ASK`, `TELL`, `OBSERVE`, `PING`). 
```bash
python .ai/src/orchestrator.py --verb ASK --payload "Verify the logic in auth.py against the constraints."
```

## Step 3: Wait for Completion
Once the orchestrator successfully writes to the Shared Mental Model (`.ai/SUBAGENT_STATE.md`), you must stop your execution and wait for the subagent to report back. Do not assume the subagent has finished until you see a `TELL` or `FAIL` response on the whiteboard.

## Step 4: Parallel Dispatch (Tier-Aware)
If you need to delegate multiple tasks to different subagents:
- **[TIER: SMALL]**: You MUST dispatch and wait sequentially. Parallel dispatch is forbidden.
- **[TIER: MEDIUM] or [TIER: LARGE]**: Check `MODEL_ENV.md`. If `parallel_subagents: true`, you may execute multiple `--route` and `--verb ASK` commands in a single turn before waiting. If `false`, you must dispatch sequentially.
