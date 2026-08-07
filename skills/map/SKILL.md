---
name: "map"
description: "The Mapping Workflow. Scans the codebase to generate and maintain a semantic structural map for blast radius coordination."
environment_target: "universal"
priority: 3
---
# The Mapping Workflow

**Trigger**: The user explicitly types `/map` or the AI determines the architecture document is severely outdated.

## Step 1: Read Existing Architecture

Before scanning anything, you MUST read the current `.ai/ARCHITECTURE.md` file in full.

- If the file exists, internalize its contents. Every line was written deliberately — by a human or by a previous `/map` run — and represents accumulated project knowledge.
- If the file does not exist, note that this is a first-time mapping. Proceed to Step 2.

## Step 2: Create Backup

If `.ai/ARCHITECTURE.md` exists, create a timestamped backup before making any changes:

```
cp .ai/ARCHITECTURE.md .ai/ARCHITECTURE.md.bak
```

This is a hard safety net. Even if the merge goes wrong, the user can always recover.

## Step 3: Codebase Audit

Analyze the current state of the codebase. You do not need to read every single line of code, but you must use file listing (`ls`) and fast search (`grep`) tools to understand:
1. The high-level folder structure.
2. What the core modules are (e.g., Auth, Database, UI).
3. How data flows between these modules.

## Step 4: Diff & Present (Conversation Gate)

> [!CAUTION]
> **Do NOT write to `ARCHITECTURE.md` yet.**
> You must present your findings to the user first and wait for explicit approval.

Compare your new findings against the existing document. Present a summary to the user in this format:

```markdown
# 🗺️ Architecture Map — Proposed Changes

## New Sections (not in current document)
- [list what you discovered that isn't documented yet]

## Updated Sections (stale or changed since last mapping)
- [list what has changed in the codebase vs. what's documented]

## Unchanged Sections (preserving as-is)
- [list sections from the existing document you did NOT scan or that are still accurate]

Shall I merge these changes into ARCHITECTURE.md?
```

**You are BLOCKED from writing until the user gives an explicit go-ahead** (e.g., "yes", "merge it", "go ahead", "looks good").

If the user asks questions or provides corrections, answer them and re-present an updated summary.

## Step 5: Additive Merge

Once approved, write to `.ai/ARCHITECTURE.md` using these merge rules:

1. **Add** new sections for anything you discovered that wasn't in the existing document.
2. **Update** sections where the codebase has clearly changed (e.g., a module was renamed, a new API route was added). Preserve the existing prose structure and only modify the specific details that are stale.
3. **Preserve** every section you did not scan or that is still accurate. If the existing document has detailed frontend notes and you only scanned the backend, those frontend notes MUST remain exactly as they were.
4. **Never delete** content unless it is provably wrong (e.g., references a file or module that no longer exists in the codebase). If unsure, keep it.

> [!IMPORTANT]
> `/map` is an **accumulative merge**, not a regeneration. Treat `ARCHITECTURE.md` like a living wiki that grows over time, not a disposable file that gets regenerated from scratch on each run.

The `.ai/ARCHITECTURE.md` file MUST include (adding sections if missing):
- **Folder Structure**: A visual tree of the codebase.
- **Component Relationships (Sensitivities)**: Which modules depend on which, AND a natural language explanation of *why* they depend on each other (e.g., "The Auth module is highly sensitive to the Database module because it relies on the `users` table schema"). This helps the AI calculate the "blast radius" during execution.
- **Data Flow**: A brief explanation of how state/data moves through the app.

> [!CAUTION]
> Do not put coding rules or best practices in `.ai/ARCHITECTURE.md`. Coding standards belong in the `.ai/rules/` directory.

## Step 6: Handoff

Once the architecture map is merged, print:

```markdown
> **AgentGate ► ARCHITECTURE MAP UPDATED**
> ✓ Backup saved to .ai/ARCHITECTURE.md.bak
> ✓ Changes merged into .ai/ARCHITECTURE.md
> 
> New sections added: X
> Sections updated:   Y
> Sections preserved: Z
```

## Workflow Hooks (Conditional Internal Skill Invocations)
These hooks fire automatically at specific points during the mapping workflow when conditions are met.

| Trigger Condition | Invoke | Action |
|---|---|---|
| Step 3 (Codebase Audit) — if the project contains >50 files or >5 top-level directories | `/researcher` | Spawn a read-only `/researcher` subagent via `/delegate` to scan file structures and module boundaries, then report findings back to preserve your main context |

