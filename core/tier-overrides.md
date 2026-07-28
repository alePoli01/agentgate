---
type: "core_override"
environment_target: "universal"
priority: 1
---
# Tier-Based Overrides

> [!TIP]
> **CONTEXT TIER ARCHITECTURE**
> You are operating within the Tier-based context management system. Your behaviour, context constraints, and subagent delegation rules scale dynamically based on the current Context Window size defined in `.ai/MODEL_ENV.md`.

## Index
1. [Subagent Delegation Thresholds](#1-subagent-delegation-thresholds)
2. [Context Management & Hygiene](#2-context-management--hygiene)
3. [Token Efficiency & DARRMS](#3-token-efficiency--darrms)
4. [Advanced Reasoning (Medium/Large Tiers)](#4-advanced-reasoning-mediumlarge-tiers)
5. [Loop Overrides](#5-loop-overrides)

---

## 1. Subagent Delegation Thresholds

| Tier | Delegation Threshold | Parallel Dispatch |
|---|---|---|
| **SMALL** (<32k) | **Mandatory** if reading >3 files | Forbidden |
| **MEDIUM** (32k-128k) | **Discretionary** if reading >5 files | Allowed (if enabled) |
| **LARGE** (128k+) | **Discretionary** if reading >8 files | Allowed (if enabled) |

**Rule**: If your task exceeds the delegation threshold for your Tier, you MUST spawn a subagent via the `/delegate` workflow or explicit `--route` command. Do not attempt to load massive architectures into a constrained context window.

---

## 2. Context Management & Hygiene

### The Quality Degradation Curve
Context is a finite and degrading resource. Do NOT attempt to push through heavy context loads. As your context fills up, your performance degrades mathematically.
| Context Usage | Quality | State |
|---------------|---------|-------|
| 0-30% | PEAK | Thorough, comprehensive, creative |
| 30-50% | GOOD | Confident, solid work |
| 50-70% | DEGRADING | Efficiency mode begins, details drop |
| 70%+ | POOR | Rushed, minimal, error-prone |

### Tier Thresholds
| Tier | Peak Quality | Warning Gate | Critical / Pause Gate | 3-Strike Rule Adjustment |
|---|---|---|---|---|
| **SMALL** | 0-20% | 30% | 40% (Mandatory Sprint Protocol) | 2 stagnant failures |
| **MEDIUM** | 0-40% | 50% | 55% | 3 stagnant failures |
| **LARGE** | 0-50% | 70% | 70% | 4 stagnant failures |

### The Sprint Protocol (SMALL Tiers Only)
Because you have a constrained context window, operate in **Sprints**:
1. **Read**: Check `MEMORY.md`. Treat it as your absolute source of truth.
2. **Execute**: Perform your task concisely.
3. **Save**: Flush progress to `MEMORY.md` immediately.
4. **Slide**: Let the older context slide away. Never attempt continuous, unbounded planning sessions.

---

## 3. Token Efficiency & DARRMS

**Dynamic Attention Radius (DARRMS):**
`python .ai/src/orchestrator.py --focus /path/to/file`

| Tier | DARRMS Rule |
|---|---|
| **SMALL** | **MANDATORY** before attempting to read any file > 50 lines. |
| **MEDIUM** | **MANDATORY** for files > 200 lines. |
| **LARGE** | **OPTIONAL**. You may read full files, but DARRMS is recommended for 1000+ line monoliths. |

**MASK Arbiter (Semantic Gating)**:
Regardless of tier, before attempting a blind `read_file` on a large document, you MUST use `--query` (semantic search) first. The Arbiter will block access to irrelevant files.

---

## 4. Advanced Reasoning (Medium/Large Tiers)

If you are operating on a **MEDIUM** or **LARGE** tier, you possess sufficient reasoning capacity to employ the following protocols:

1. **Uncertainty Estimation**: When planning (`/discuss`, `/plan`, Architect role), explicitly estimate your confidence (1-5). If confidence is ≤ 3, flag the assumption as unverified and demand evidence before writing code.
2. **Self-Critique Gate**: Before declaring a task "done" or committing code, explicitly self-critique: "Does this code actually meet the task requirements, and have I verified it via the terminal?" Check for API Era Consistency (avoid mixing legacy and modern paradigms).
3. **Lost-in-the-Middle Mitigation**: For LARGE tiers, actively recall and re-state key constraints from `.ai/ARCHITECTURE.md` or `.ai/rules/` before generating a long output to pull them to the front of your attention.

---

## 5. Loop Overrides

When running `/loop`, your tier dictates your iteration safety limits. Do NOT bypass these limits.

| Setting | SMALL | MEDIUM | LARGE |
|---|---|---|---|
| MAX_ITERATIONS | 3 | 6 | 10 |
| Max complexity per iteration | 1-2 steps | 2-3 steps | 3-5 steps |

**Loop Abort Triggers:**
- Reaching your tier's strike threshold (e.g., 2 consecutive stagnant failures for SMALL).
- Reaching your tier's Critical/Pause Gate context threshold.
- Missing dependencies that cannot be resolved without user intervention.
