---
name: "verify"
description: "The Verification Workflow. Validates implemented work against spec requirements using empirical evidence, and creates gap closure plans for failed tasks."
environment_target: "universal"
priority: 3
---
# The Verification Workflow (The Evidence Gate)

**Trigger**: The user asks to verify a phase/task, or the `/execute` workflow completes a milestone.

**Core principle**: No "trust me, it works." Every verification produces proof directly from the codebase.

## Step 1: Read the Execution Summary and Plan
Read `.ai/SPEC.md`, `.ai/ROADMAP.md` (to identify the phase's must-haves), and the actual execution `SUMMARY.md` or `.ai/phases/{N}/*-PLAN.md` files.

## Step 2: Extract Must-Haves
From the phase definition and plan, identify **must-haves** — requirements that MUST be true for the phase to be complete.

## Step 3: Direct Codebase Verification
For every task that is marked as "done", you MUST independently verify it. Do NOT blindly trust the `<evidence>` block from execution. 

1. **Terminal Verification**: Run the verification command yourself (e.g., `npm test`, `pytest`, `curl`). 
2. **Filesystem Check**: If a file was supposed to be created, verify it exists.
3. **Forbidden Phrases**: If relying on prior execution logs, reject any claims like "The code looks correct," "This should work," "I've made similar changes before." The ONLY acceptable evidence is raw `stdout`/`stderr` or `MANUAL_VERIFICATION_REQUIRED`.

## Step 4: Issue Structured Verification Report
Write the results to `.ai/phases/{N}/VERIFICATION.md`:

```markdown
---
phase: {N}
verified_at: {timestamp}
verdict: PASS | FAIL | PARTIAL
---

# Phase {N} Verification Report

## Summary
{X}/{Y} must-haves verified

## Must-Haves
### ✅ {Must-have 1}
**Status:** PASS
**Evidence:** 
`\``
{command output or description}
`\``

### ❌ {Must-have 2}
**Status:** FAIL
**Reason:** {why it failed}
**Expected:** {what should happen}
**Actual:** {what happened}

## Verdict
{PASS | FAIL | PARTIAL}
```

## Step 5: Gap Closure (If FAIL)
If the verdict is FAIL or PARTIAL, you must immediately spin up Gap Closure plans.
For each failed must-have, create a fix plan in `.ai/phases/{N}/`:

```markdown
---
phase: {N}
plan: fix-{issue}
wave: 1
gap_closure: true
---

# Fix Plan: {Issue Name}

## Problem
{What failed and why}

## Tasks
<task type="auto">
  <name>Fix {issue}</name>
  <files>{files to modify}</files>
  <action>{specific fix instructions}</action>
  <verify>{how to verify the fix}</verify>
  <done>{acceptance criteria}</done>
</task>
```

After generating the Gap Closure plans, explicitly prompt the user to run `/execute {N} --gaps-only` to implement the fixes.
