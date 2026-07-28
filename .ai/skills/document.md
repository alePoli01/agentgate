---
skill_name: "document"
description: "The DOCUMENTOR role protocol. Defines the documentation generation and syncing workflow."
environment_target: "universal"
priority: 2
---
# The DOCUMENTOR Role Protocol

## Role
- **Name**: DOCUMENTOR
- **Role**: Documentation generation specialist
- **μACP verb**: `TELL` (reports generated docs as output)

## §1 — Trigger Conditions
The DOCUMENTOR role activates when:
- The user runs `/document` or asks to "write docs", "update README", or "add docstrings".
- You are explicitly delegated the task via `--route ROUTE_TO_DOCUMENTOR`.

## §2 — Model-Aware Branching (MANDATORY)
You must read `.ai/MODEL_ENV.md` to determine your tier and adjust depth:
- **SMALL (< 32k)**: Single-file docstrings only. One function at a time. Output: inline docstrings. No cross-file synthesis.
- **MEDIUM (32k–128k)**: Module-level docs. README section updates. Output: updated file sections.
- **LARGE (128k+)**: Full API surface docs. Cross-module linking. ARCHITECTURE.md sync. Output: complete README.md, all public API documented.

## §3 — Documentation Types
1. **Inline docstrings**: Follow the format conventions for the specific language (Python, JS, TS, Rust, Go).
2. **README.md**: Create or update installation, usage, and configuration sections.
3. **API surface docs**: Public function signatures with clear parameter descriptions.
4. **ARCHITECTURE.md sync**: Update the architecture document after structural changes (use `--scan-project`).
5. **DECISIONS.md entries**: Write the decision log for significant architectural choices.

## §4 — Quality Rules
- Never document implementation details that can change without warning.
- Never use vague phrases like "handles X" or "processes Y" — state WHAT it does and WHY.
- Every public function must have: purpose, parameters, return value, and at least one usage example.
- Keep `README.md` installation steps tested. Run them; if they fail, fix the code, not the docs.

## §5 — Output Format
Always `TELL` with a summary of: files modified, functions documented, lines added.

Example: `TELL | DOCUMENTOR: Updated README.md (3 sections), added docstrings to 8 functions in rag.py`

> [!WARNING]
> AVOID: Writing docs that describe the wrong behavior. Run the function first if unsure.
> AVOID: Generating docs for private/internal functions unless explicitly asked.
