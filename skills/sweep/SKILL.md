---
name: "sweep"
description: "The Sweep Workflow. Hunts for 'refuses' (dead code, orphaned imports, TODOs, legacy patterns) across the codebase using subagent delegation."
environment_target: "universal"
priority: 3
---
# The Sweep Workflow (`/sweep`)

**Trigger**: The user explicitly types `/sweep` or requests a codebase cleanup for dead code and leftover artifacts.

> [!NOTE]
> Check your orchestrator tier banner (`[TIER: X]`). This determines your dispatch strategy during the sweep.

## Index
1. [Pre-Flight Scan](#step-1-pre-flight-scan)
2. [The Refuse Checklist](#step-2-the-refuse-checklist)
3. [Machine-Verifiable Checks](#step-3-machine-verifiable-checks-mandatory)
4. [Subagent Dispatch](#step-4-subagent-dispatch-tier-aware)
5. [SWEEP_REPORT.md](#step-5-compile-sweep_reportmd)

---

## Step 1: Pre-Flight Scan
Before dispatching auditors, establish the target scope:
1. Run `python .ai/src/orchestrator.py --scan-project` (or read the existing `PROJECT_MANIFEST.md`) to get a structural overview.
2. Group files by component or directory (e.g., `src/`, `core/`, `skills/`, `tests/`).
3. Each group becomes one auditor task. Keep groups small enough that a subagent can review them within a single context window.

**Maximum group size:** ~10 files or ~2000 lines per group. Split larger components.

---

## Step 2: The Refuse Checklist
Every `AUDITOR` subagent dispatched MUST check for ALL of the following:

| Category | What to Look For | Machine-Verifiable? |
|----------|-----------------|---------------------|
| **Dead Code** | Unreachable branches, unused functions, orphaned imports | Partial (linters) |
| **Leftover Comments** | `TODO`, `FIXME`, `HACK`, `XXX` comments | ✅ Yes (grep) |
| **Placeholders** | `pass`, `return None`, `NotImplementedError` in active logic | ✅ Yes (grep) |
| **Stale References** | References to deleted files, functions, or renamed APIs | Partial (grep + context) |
| **Doc ↔ Code Drift** | Contradictions between docstrings/comments and actual implementation | ❌ No (requires reasoning) |
| **Frankenstein Code** | Mixed architectural patterns (legacy + modern in same file) | ❌ No (requires reasoning) |
| **Orphaned Config** | Config keys, env vars, or constants no longer referenced | Partial (grep) |

The subagent briefing MUST include this checklist verbatim so it knows exactly what to look for.

---

## Step 3: Machine-Verifiable Checks (MANDATORY)
Before dispatching subagents (or in parallel on MEDIUM/LARGE tiers), the orchestrator MUST run automated checks using the terminal:

```bash
# Hunt leftover comments
grep -rnw . -e "TODO" -e "FIXME" -e "HACK" -e "XXX" --include="*.py" --include="*.ts" --include="*.js" --include="*.md"

# Hunt placeholders (Python)
grep -rn "pass$\|return None$\|NotImplementedError" --include="*.py" .

# Run linter for unused imports/variables (if available)
# Python: ruff check . --select F401,F841
# TypeScript: npx eslint . --rule 'no-unused-vars: error'
```

Record ALL findings — these go directly into the report without subagent overhead.

---

## Step 4: Subagent Dispatch (Tier-Aware)

### Tier Dispatch Strategy

> [!NOTE]
> The key tier difference is in dispatch concurrency. The actual review depth per subagent is identical across all tiers — each auditor reviews one component group against the full refuse checklist.

| Tier | Dispatch Mode | Rationale |
|------|--------------|-----------|
| **SMALL** | Sequential (one at a time) | Parallel dispatch is forbidden per `tier-overrides.md` |
| **MEDIUM** | Sequential by default. Parallel if `parallel_subagents: true` in MODEL_ENV.md | Respects user configuration |
| **LARGE** | Parallel if `parallel_subagents: true`, sequential otherwise | Same as MEDIUM |

### Dispatch Protocol
For each component group, follow the standard subagent handshake:

```bash
# 1. Register the task
python .ai/src/orchestrator.py --verb ASK --payload "SWEEP [GROUP_PATH]: Review all files for refuses using the standard Refuse Checklist. Check for: dead code, orphaned imports, TODO/FIXME/HACK comments, placeholder implementations, stale references, doc-code inconsistencies, and mixed architectural patterns. Output findings in structured format."

# 2. Route to auditor
python .ai/src/orchestrator.py --route ROUTE_TO_AUDITOR --task-id <TASK_ID>

# 3. [Sequential only] Wait for TELL/FAIL on whiteboard before dispatching next group
python .ai/src/orchestrator.py --collect --task-id <TASK_ID>
```

### [TIER: SMALL] — Sequential Sweep
1. Dispatch auditor for Group 1, wait for completion.
2. Collect result. Dispatch auditor for Group 2, wait.
3. Repeat until all groups are reviewed.
4. Between dispatches, flush the collected results to `SWEEP_REPORT.md` to avoid holding them in context.

### [TIER: MEDIUM/LARGE] — Parallel Sweep (if enabled)
1. Dispatch auditors for ALL groups in a single turn.
2. Wait for all to complete (check whiteboard periodically).
3. Collect all results and compile the report.

---

## Step 5: Compile SWEEP_REPORT.md
Once all subagents have reported and machine checks are done, compile into `.ai/SWEEP_REPORT.md`:

```markdown
# Codebase Sweep Report
> Generated on [DATE] by `/sweep`

## 🤖 Machine-Verifiable Findings
### Leftover Comments
- `src/whiteboard.py:131` — TODO: "Fallback to T-0000 if legacy"
- `src/tools.py:108` — Placeholder: "native execution not implemented"

### Unused Imports / Dead Code
- `src/config.py:2` — `json` imported but unused in module scope
- ...

## 🕵️ Auditor Findings

### Component: `src/`
| Category | Finding | Severity |
|----------|---------|----------|
| Frankenstein Code | `tools.py` mixes native execution with JSON payload fallback | 🟡 Medium |
| Doc ↔ Code Drift | `ARCHITECTURE.md` claims caching not implemented; `rag.py` has it | 🔴 High |

### Component: `skills/`
| Category | Finding | Severity |
|----------|---------|----------|
| ... | ... | ... |

## 📊 Summary
- **Total refuses found:** N
- **Machine-verifiable:** M (auto-fixable)
- **Requires reasoning:** K (manual review)

## 🚀 Recommended Actions
1. [AUTO-FIX] Remove unused imports with `ruff check --fix`
2. [MANUAL] Sync ARCHITECTURE.md with actual rag.py caching implementation
3. [MANUAL] Resolve placeholder tools in tools.py (implement or remove)
```
