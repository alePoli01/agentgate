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

