---
name: "plan"
description: "The Planning Workflow. Gathers requirements, defines technical standards, and creates implementation plans."
environment_target: "universal"
priority: 1
---
# The Planning Workflow

**Trigger**: The user wants to start a new phase, build a new feature, or explicitly typed `/plan`.

> [!NOTE]
> Check your orchestrator tier banner (`[TIER: X]`). This determines your planning granularity and cognitive load management.

## Step 0: Planning Lock & Roadmap Gate

Before doing ANYTHING else, run these two checks:

**Check A — Spec Lock:**
Read `.ai/SPEC.md`. If it does not contain the exact string `Status: FINALIZED`, STOP immediately and respond:
> "PLANNING LOCKED: `.ai/SPEC.md` is not finalized. Complete and finalize the spec before any planning begins."
Do not proceed past this point.

**Check B — Dependency Gate:**
Read `.ai/ROADMAP.md`. Find the current phase entry. Locate its `Depends on:` field.
For each phase listed as a dependency, verify its **Status** line reads `✅ Complete`.
If any dependency is NOT complete, STOP and respond with a list of the blocking phases.

## Step 0.5: Discovery Protocol (Context Budgeting)

Discovery is MANDATORY unless you can prove the necessary context already exists. You must classify the required research into one of these levels:

**Level 0 — Skip** (pure internal work)
- ALL work follows established codebase patterns
- No new external dependencies
- Pure internal refactoring or feature extension

**Level 1 — Quick Verification** (2-5 min)
- Single known library, confirming syntax/version
- Low-risk decision (easily changed later)
- Action: Quick web search, no RESEARCH.md needed

**Level 1.5 — Discovery** (5-15 min)
- Quick library/option comparison (A vs B)
- Low-to-medium risk, focused question
- Action: Create `DISCOVERY.md`

**Level 2 — Standard Research** (15-30 min)
- Choosing between 2-3 options
- New external integration (API, service)
- Medium-risk decision
- Action: Create `RESEARCH.md` with findings

**Level 3 — Deep Dive** (1+ hour)
- Architectural decision with long-term impact
- Novel problem without clear patterns
- High-risk, hard to change later
- Action: Full research with `RESEARCH.md`

---

## Step 1: Intent Check
Discuss the feature with the user. Ensure you understand the scope, boundaries, and exactly what needs to be built.

## Step 2: Needs Assessment
List out the specific technologies, languages, and architectural layers required to build this feature (e.g., React frontend, Python backend, PostgreSQL database).

## Step 3: The Interrogation (Standards Check)
You must establish the rules before execution. Ask the user:
*"Do you have specific coding standards, project structures, or rules you want to adopt for [Tech A] and [Tech B]?"*

## Step 4: Auto-Generation of Standards (Library Freshness Protocol)
For any technology where the user does NOT provide explicit rules, you MUST define the industry best practices.

**Web-First Resolution:** Your internal training data is outdated. Before writing rules for a library/framework, you MUST:
1. Use web search tools (if available) or `curl` to query the official documentation/registry to find the latest stable version and recommended paradigms.
2. If you do not have web-search capabilities, you MUST explicitly warn the user about your training cutoff and ask them to paste the latest official documentation or version numbers before you generate the rules.
3. Only after securing the latest context, generate the standard markdown file (e.g., `.ai/rules/react-standards.md`) and save it.

> [!IMPORTANT]
> By generating this file, you are creating the permanent source of truth for how this technology should be written in this project. You will be strictly graded against these files during execution.

## Step 5: Adaptive Routing (XML Task Generation)
You must break down the implementation into `<task>` XML blocks (defined in `task-schema.md`).

**Formatting Rule**: You MUST pretty-print and indent all `<task>` XML blocks (including nested tags and content) so they are clean and easy for the user to read.

**The Token Tax Mitigation Rule**:
- **Low Effort Tasks (1-2 steps)**: Generate the `<task>` blocks inline within the main conversation and proceed to execute them directly.
- **Medium/High Effort Tasks**: Do NOT generate massive XML blocks in the main conversation. You MUST delegate to a `planner` subagent. Instruct the subagent to reason through the steps and write the resulting XML `<task>` blocks to a plan file (e.g., `.ai/phases/N/1-PLAN.md`). 

## Step 6: Handoff
Once the plan is generated (either inline or via file) and all language-specific `.ai/rules/` files exist, explicitly inform the user that the planning phase is complete and prompt them to run the Execution workflow (`/execute`).

---

## Step 7: Plan Checker Logic (Self-Validation)

For each plan generated, you MUST verify:
- [ ] All files specified exist or will be created
- [ ] Actions are specific (no "implement X")
- [ ] Verify commands are executable
- [ ] Done criteria are measurable
- [ ] Context references exist
- [ ] Tests are meaningful (see Test Quality Rules below)

**If issues are found:** Fix and re-verify (max 3 iterations).

### Test Quality Rules
Tests must verify real behavior, not just pass. Reject plans with tests that:

| Anti-pattern | Example | Fix |
|-------------|---------|-----|
| **Mock everything** | Mocking the DB then asserting the mock was called | Use real DB or integration test |
| **Tautological assert** | `assert mock.called` with no behavior check | Assert actual output or side effect |
| **Always-pass test** | `assert True` or `assert response is not None` | Assert specific expected values |
| **Testing the framework** | Asserting that Express returns 200 on a stub | Test your logic, not the framework |
| **No negative cases** | Only testing the happy path | Include at least one failure/edge case |

**Rule:** Every `<verify>` command must test the *actual behavior* of the code, not just that it runs without errors. If a test would still pass with the implementation deleted, it is not a valid test.

---

## Wave vs. Plan Rules

These two concepts are distinct and must not be confused:

**Plans** manage cognitive load.
- If **[TIER: SMALL]**: Maximum 1-2 tasks per plan file. You MUST aggressively break down work to prevent yourself from losing track during execution.
- If **[TIER: MEDIUM]**: Maximum 2-3 tasks per plan file.
- If **[TIER: LARGE]**: Maximum 4-5 tasks per plan file.
- If a phase requires more tasks than your tier allows per plan, you MUST split it into multiple plan files (e.g., `19-1-PLAN.md`, `19-2-PLAN.md`).
- Plans in the same wave do NOT depend on each other's output.

**Waves** manage temporal dependencies.
- Wave 1: Plans with no dependency on other plans' output.
- Wave 2+: Plans that require a previous wave's files or decisions to exist first.
- A Wave 2 plan MUST NOT start until all Wave 1 plans have been executed AND verified.

**Sequential Execution Mandate:**
Even within the same wave, plans are executed strictly one at a time.
Parallel execution is FORBIDDEN for any task that writes files or modifies code.
The only exception: read-only research tasks (e.g., two subagents researching different topics simultaneously with no shared write target).
