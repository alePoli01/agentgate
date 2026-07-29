---
name: "loop"
description: "The /loop workflow. Autonomous goal-oriented execution that persists until a verifiable termination condition is met."
environment_target: "universal"
priority: 2
---
# The /loop Workflow

**Trigger**: The user types `/loop` followed by a goal description and a termination condition.

> [!IMPORTANT]
> `/loop` is NOT a way to run indefinitely. It is a structured, goal-anchored execution
> pattern with hard safety gates. It WILL stop — either because the goal is verified
> complete, or because a safety limit is hit.

---

## Step 0 — Model Detection (MANDATORY FIRST STEP)

Before anything else, check your orchestrator tier banner (`[TIER: X]`). The tier determines the following loop constraints:

| Tier | MAX_ITERATIONS | Context Pause at | Strike threshold | DARRMS `--focus` |
|------|----------------|------------------|------------------|------------------|
| SMALL| 3              | 40%              | 2 stagnant       | Mandatory        |
| MED  | 6              | 55%              | 3 stagnant       | Required for >200 lines |
| LRG  | 10             | 70%              | 4 stagnant       | Optional         |

> [!NOTE]
> If you are **[TIER: SMALL]**, refer to the "Condensed Loop Cycle for SMALL TIER" at the bottom of this file to save context while executing.


## Step 1 — Goal Declaration

Extract or ask for the following:

```
GOAL:           [What must be built or fixed — one clear sentence]
DONE WHEN:      [A shell command that returns exit code 0 when the goal is achieved]
MAX ITERATIONS: [Large default: 10. Small default: 3. User can override.]
```

**Example:**
```
GOAL: Add form validation to the login page so empty fields are rejected
DONE WHEN: pytest tests/test_login.py -k "test_empty_field"
MAX ITERATIONS: 5
```

If the user does not provide a `DONE WHEN` command, STOP and ask for one.
Do not start the loop without a verifiable termination condition.
A goal like "make it look better" cannot be verified — refuse it and ask for a concrete criterion.

### Small Tier Warning

If `[TIER: SMALL]`, print this before starting:

```
+----------------------------------------------------------+
|  SMALL TIER LOOP MODE                                    |
|                                                          |
|  You are running /loop on a SMALL context model. The     |
|  following guardrails are AUTOMATICALLY applied:         |
|                                                          |
|  - MAX_ITERATIONS restricted to 3                        |
|  - Loop pauses if context exceeds 40%                    |
|  - DARRMS focus check required before each iteration     |
|  - Failed approach memory is mandatory                   |
|                                                          |
|  To use more iterations, switch to a larger model        |
|  or run /loop again after /pause and a fresh session.    |
+----------------------------------------------------------+
```

---

## Step 2 — Initialise Loop State

Write initial loop state to `.ai/LOOP_STATE.md` by running a harmless check:

```bash
python .ai/src/orchestrator.py --loop-check "echo loop_initialized"
```

Then manually edit `.ai/LOOP_STATE.md` to set the goal line, model type, and max iterations:

```markdown
## /loop State
- Goal: <goal text>
- Model tier: <Small|Medium|Large>
- Max iterations: <N>
- Iteration: 0
- Last check: <timestamp>
- Last command: (initialised)
- Last result: (none)
- Last stdout: (empty)
- Last stderr: (none)
- Failed approaches: (none)
```

---

## Step 3 — The Loop Execution Cycle

Repeat until a termination condition is met. Each iteration follows this exact cycle:

```
[Start of iteration N]
     |
     v
1. CHECK LOOP STATUS
     |
     v
2. [LOCAL ONLY] DARRMS FOCUS — collapse all files you plan to read this iteration
     |
     v
3. [LOCAL ONLY] CONTEXT BUDGET CHECK — if context > 40%, pause immediately
     |
     v
4. READ MEMORY.md — check for failed approaches from prior iterations
     |
     v
5. PLAN — break goal into smallest possible next action (1-2 steps max)
     |
     v
6. EXECUTE — implement the action (sequential, no parallel tool calls)
     |
     v
7. TEST — run static analysis first, then tests (follow test.md)
     |
     v
8. TERMINATION CHECK — run --loop-check
     |
     +-- Exit code 0?  --> GOAL ACHIEVED --> Step 4 (Success Report)
     |
     +-- Exit code non-0? --> increment counter --> check safety gates --> next iteration
```

### Step 3.1 — Check Loop Status
```bash
python .ai/src/orchestrator.py --loop-status
```
Read the output. If `Failed approaches` is non-empty, you MUST NOT attempt any listed approach.

### Step 3.2 — [LOCAL ONLY] DARRMS Focus Check
For every file you plan to read or edit this iteration, run:
```bash
python .ai/src/orchestrator.py --focus <filepath>
```
Load only the collapsed outline into context, not the full file.
Exception: files under 50 lines may be loaded in full.

### Step 3.3 — [LOCAL ONLY] Context Budget Check
Estimate your current context usage. If it exceeds 40%:

```
LOOP PAUSED: Context at {N}%. Local model limit is 40%.
Run /pause to save state. Start a fresh session. Run /loop to resume.
```

Do NOT continue the iteration. Stop immediately.

### Step 3.8 — Termination Check (MANDATORY)
At the end of every iteration, you MUST run:
```bash
python .ai/src/orchestrator.py --loop-check "<DONE WHEN command>"
```
- Exit code **0** — goal achieved. Proceed to Step 4 (Success Report).
- Exit code **non-0** — not done. Increment iteration count. Check safety gates.

---

## Step 4 — Success Report

When `--loop-check` returns exit code 0, print:

```
=====================================================
 /loop GOAL ACHIEVED
=====================================================
Goal:        <goal text>
Iterations:  <N> / <MAX>
Verified by: <DONE WHEN command>

Suggested next step: /verify <phase> to confirm full integration
=====================================================
```

Then delete `.ai/LOOP_STATE.md` to signal loop completion:
```bash
del .ai\LOOP_STATE.md
```

---

## Termination Conditions

The loop exits when ANY of the following are true:

| Condition | Action |
|-----------|--------|
| `--loop-check` returns exit code 0 | SUCCESS — print report, delete LOOP_STATE.md |
| Loop counter reaches MAX ITERATIONS | HARD STOP — max iterations report |
| 3 consecutive identical failures (Large tier) | HARD STOP — 3-strike report, mandate /pause |
| 2 consecutive identical failures (Small tier) | HARD STOP — 2-strike report, mandate /pause |
| [SMALL] Context > 40% | PAUSE — context budget report |
| [LARGE] Context > 70% | PAUSE — context budget report |
| User types STOP | IMMEDIATE STOP |

### Max Iterations Report
```
LOOP ENDED: Reached MAX ITERATIONS (<N>) without achieving the goal.
Last state: <describe what was achieved and what remains>
Run /loop again with the remaining goal, or /debug to investigate the blocker.
```

### 3-Strike Report (Large tier) / 2-Strike Report (Small tier)
```
LOOP HALTED: Stagnant iterations detected. The approach is stuck.
Run /pause to save state. Start a fresh session. Try a different approach.
```

---

## Safety Gates

### The Strike Rule
If consecutive iterations produce the exact same `--loop-check` failure output
(same exit code AND same stderr):
- **Large**: STOP after 3 consecutive stagnant failures.
- **Small/Medium**: STOP after 2 consecutive stagnant failures (lower threshold — smaller models
  degrade faster and a third stagnant attempt wastes significant context budget).

Note: Progressive failures (different errors, forward movement) do NOT count as strikes.

### UI Task Gate
If the goal involves UI/frontend work, the loop CANNOT self-certify completion.
The `DONE WHEN` command must include a lighthouse audit, a screenshot diff, or an
explicit `checkpoint:human-verify` step that pauses for user approval.
The loop is only marked complete after explicit human approval.

### Large Tier Context Gate
Large tier model context threshold: pause at **70%** usage.
```
LOOP PAUSED: Context at {N}%. Large tier safety limit.
Run /pause then start a fresh session to continue.
```

---

## Condensed Loop Cycle for SMALL TIER
If your tier banner reads `[TIER: SMALL]`, follow this stripped-down checklist to save tokens. Do not read the dense sections above unless necessary.

1. **Init**: Run `python orchestrator.py --loop-check "echo loop_initialized"`. Edit `LOOP_STATE.md` with goal and `Max iterations: 3`.
2. **Cycle**:
   - `python orchestrator.py --loop-status` (Check failed approaches)
   - `python orchestrator.py --focus <file>` (MANDATORY before reading)
   - Plan 1-2 small steps.
   - Execute step.
   - `python orchestrator.py --loop-check "<DONE WHEN>"`
3. **End**: If exit code 0, delete `LOOP_STATE.md` and report success. If non-0, check if 2 stagnant strikes or 40% context budget hit. If so, HARD STOP and tell user to `/pause`.
