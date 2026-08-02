# 0.4.0-alpha

**Date:** 2026-08-02

## Summary
The "Framework Hardening" Update. Major improvements to planning, skill routing, design consistency, and host IDE overrides.

## What Changed
- **Skill-Per-Task Routing (Smart Dispatcher)**: `/execute` now automatically routes XML tasks to alternative skills (e.g., `skill="debug"`) if specified in the plan, eliminating the need to manually invoke different workflows for a single phase.
- **Auto-Include Policies**: Minor skills (`ui-designer`, `security`, `review`) are now automatically loaded as mandatory pre-flight checks in major workflows based on file-detection (e.g., modifying `*Screen.kt` auto-loads `ui-designer`).
- **UI Token Registry**: `/ui-designer` now mandates the creation and strict adherence to `.ai/UI_TOKENS.md`. UI decisions (padding, colors, typography) are now actively recorded and persisted across context slides.
- **Native IDE Override Mandate**: Added a strict rule to `core-rules.md` and `plan/SKILL.md` to aggressively block host IDEs (like Antigravity or Cursor) from injecting their own native planning artifacts (`implementation_plan.md`, `task.md`), forcing reliance on `.ai/STATE.md` and XML plans.

## Previous Version
0.3.0-alpha — Autonomous Loop Execution.

---

# 0.3.0-alpha

**Date:** 2026-07-10

## Summary
Phase 26 — Autonomous Loop Execution. `/loop` is now a machine-verifiable autonomous execution system with model-aware guardrails.

## What Changed
- `orchestrator.py --loop-check "<cmd>"`: Runs the DONE WHEN shell command, writes structured result to `.ai/LOOP_STATE.md`, exits with same code. Termination is now exit-code based, not trust-based.
- `orchestrator.py --loop-status`: Reads and prints the current loop state (goal, iteration, last result, failed approaches).
- `llm-framework/skills/loop.md`: Full rewrite. Model-aware branching via `MODEL_ENV.md`. Local models: MAX_ITERATIONS=3, 40% context gate, mandatory DARRMS per iteration, 2-strike rule. Cloud models: MAX_ITERATIONS=10, 70% context gate, 3-strike rule.
- `llm-framework/core/loop-overrides.md`: New dedicated override file for local model loop rules (iteration budget, context gates, DARRMS protocol, memory discipline, abort conditions).

## Architecture
The loop system is a three-layer design:
1. **Skill** (`loop.md`) — the workflow agent reads and executes
2. **Runtime** (`orchestrator.py --loop-check`) — the machine that verifies termination
3. **State** (`.ai/LOOP_STATE.md`) — persistent across iterations, survives context slides

## Previous Version
0.2.0-alpha — Real Orchestration Runtime (Phase 23).

