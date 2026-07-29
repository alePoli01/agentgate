---
name: "map"
description: "The Architect Workflow. Scans the codebase to generate and maintain a semantic structural map for blast radius coordination."
environment_target: "universal"
priority: 3
---
# The Architect Workflow

**Trigger**: The user explicitly types `/map` or the AI determines the architecture document is severely outdated.

## Step 1: Codebase Audit
You MUST analyze the current state of the codebase. You do not need to read every single line of code, but you must use file listing (`ls`) and fast search (`grep`) tools to understand:
1. The high-level folder structure.
2. What the core modules are (e.g., Auth, Database, UI).
3. How data flows between these modules.

## Step 2: Document Generation
You MUST write your findings to `.ai/ARCHITECTURE.md`. This file acts as the permanent source of truth for the project's structural map.

The `.ai/ARCHITECTURE.md` file MUST include:
- **Folder Structure**: A visual tree of the codebase.
- **Component Relationships (Sensitivities)**: Which modules depend on which, AND a natural language explanation of *why* they depend on each other (e.g., "The Auth module is highly sensitive to the Database module because it relies on the `users` table schema"). This helps the AI calculate the "blast radius" during execution.
- **Data Flow**: A brief explanation of how state/data moves through the app.

> [!CAUTION]
> Do not put coding rules or best practices in `.ai/ARCHITECTURE.md`. Coding standards belong in the `.ai/rules/` directory.

## Step 3: Handoff
Once the architecture map is synced, explicitly inform the user that the map is updated and the project is ready for further implementation.
