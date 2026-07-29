# /new-project Workflow

## Objective
Scaffold all lifecycle files for a new project using AgentGate.
Run this ONCE at the start of any new project before using /plan, /execute, or any other workflow.

## Process

### Step 1 — Gather Project Info
Ask the user for:
- **Project name** (used in all file headers)
- **Project type** (Web App / CLI Tool / Library / API / Other)
- **Model Tier** (Small, Medium, Large) — Small for local models (enables strict memory-saving rules). Large for powerful cloud models (enables deep context execution).
- **One-sentence goal** (the core "done" for this project)

Do NOT proceed until all four are answered.

### Step 2 — Create Scaffold Files

Create the following files. If any already exist, do NOT overwrite — print a warning and skip that file.

#### `.ai/SPEC.md`
```markdown
# SPEC — {Project Name}
> **Status**: `DRAFT` ← Change to `FINALIZED` only when you are 100% committed to this scope.

## Goal
{One-sentence goal from user}

## Project Type
{Project Type}

## Requirements
- REQ-01: {First requirement — fill this in}
- REQ-02: {Second requirement — fill this in}

## Out of Scope
- {List things explicitly NOT being built}

## Finalization Checklist
- [ ] All requirements are specific and testable
- [ ] Out of scope is explicitly listed
- [ ] Status changed to FINALIZED
```

#### `.ai/MEMORY.md`
```markdown
# MEMORY — {Project Name}
> **Rule**: Max 5 active TODOs. Max 3 active Decisions. Archive everything else.

## Active TODOs (max 5)
*(empty — add tasks here as you work)*

## Active Decisions (max 3)
*(empty — log architectural decisions here)*

## Archive
*(completed items move here)*
```

#### `.ai/STATE.md`
```markdown
# STATE — {Project Name}

## Current Position
- **Phase**: None (project just initialized)
- **Task**: Complete SPEC.md, then run /plan 1
- **Status**: Setup

## Last Session Summary
Project initialized via /new-project on {today's date}.
```

#### `.ai/DECISIONS.md`
```markdown
# DECISIONS — {Project Name}

> This file is the persistent architectural memory of the project.
> It MUST be updated whenever an architectural decision is made.
> Future agents read this to understand WHY the system is built the way it is.

## Decision Log

### Project Init — {today's date}
- **Decision**: Project initialized with AgentGate framework.
- **Model Tier**: {Small, Medium, or Large}
- **Rationale**: Starting fresh with framework scaffolding.
```

#### `.ai/ROADMAP.md`
```markdown
# ROADMAP — {Project Name}

> **Current Phase**: None → 1 next

## Must-Haves (from SPEC)
- [ ] {Copy REQ-01 here}
- [ ] {Copy REQ-02 here}

## Phases

### Phase 1: {First Phase Name}
**Status**: ⬜ Not Started
**Objective**: {Describe what this phase delivers}
**Depends on**: None

**Tasks**:
- [ ] TBD (run /plan 1 to create)

**Verification**:
- TBD
```

### Step 3 — Write MODEL_ENV.md
Based on the user's model type answer, write `.ai/MODEL_ENV.md`:
```yaml
mcp_tools:
  browser: false
  filesystem: true
  git: false
model_tier: Large  # or: Small/Medium
```

### Step 3b — Copy Rule Templates
After determining the project's primary language(s) (from `--scan-project` output or user input):
1. Create `.ai/rules/` directory if it does not exist.
2. Copy the relevant `<language>-standards.md` files from `.ai/rules-templates/` to `.ai/rules/`.
3. Inform the user that these are editable defaults they can customize.

Example:
```bash
cp .ai/rules-templates/python-standards.md .ai/rules/python-standards.md
cp .ai/rules-templates/typescript-standards.md .ai/rules/typescript-standards.md
```

### Step 4 — Print Summary
After all files are created, print:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 AgentGate ► PROJECT INITIALIZED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files created:
  ✓ .ai/SPEC.md        ← Fill in requirements, then FINALIZE
  ✓ .ai/MEMORY.md      ← Active TODOs and decisions
  ✓ .ai/STATE.md       ← Session position tracker
  ✓ .ai/DECISIONS.md   ← Persistent architectural log
  ✓ .ai/ROADMAP.md     ← Phase tracking

▶ NEXT STEP
1. Open .ai/SPEC.md and complete all requirements
2. Change Status from DRAFT to FINALIZED
3. Run /plan 1 to create your first phase execution plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Constraints
- Do NOT overwrite any existing file. Print `[SKIP] {filename} already exists` for each skipped file.
- Replace ALL {placeholder} tokens with actual values from the user's answers.
- Use today's actual date in all timestamps.

## Mid-Project Installation (Existing Codebases)

If you are installing AgentGate into a project that is **already in progress**
(existing code, existing decisions, existing architecture), do NOT run `/new-project` alone.
It will create blank lifecycle files that contradict your existing work.

Instead, run the two-phase adoption flow:

### Phase A — Automated Discovery
```bash
python .ai/src/orchestrator.py --scan-project
```
This scans the project tree and writes `.ai/PROJECT_MANIFEST.md` — a structured
inventory of files, languages, and detected existing docs.
It does NOT read file contents. It is purely structural.

### Phase B — Architect Mapping
```bash
python .ai/src/orchestrator.py --route ROUTE_TO_ARCHITECT
```
Paste the Briefing Block into a new chat. The ARCHITECT agent reads `PROJECT_MANIFEST.md`
and produces `ARCHITECTURE.md` with `[UNMAPPED]` tags for anything uncertain.

### Then: Run /new-project
After the ARCHITECT produces `ARCHITECTURE.md`, run `/new-project` to scaffold the
remaining lifecycle files (SPEC, MEMORY, STATE, DECISIONS, ROADMAP).
When filling in the SPEC, import decisions from `ARCHITECTURE.md` into `DECISIONS.md`
to preserve existing architectural context.
