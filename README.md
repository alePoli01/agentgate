<div align="center">
  <h1>🛡️ AgentGate</h1>
  <p><strong>The Zero-Dependency, Tier-Aware LLM Orchestration Framework</strong></p>
</div>

Most AI coding frameworks assume you have endless context windows and limitless API budgets, relying on massive JSON schemas and bloated OOP hierarchies that crash local models.

**AgentGate** flips the script. Designed for maximum efficiency, it uses the **μACP (Micro Agent Communication Protocol)** and **Shared Mental Models** to keep AI agents perfectly synchronized without crushing their context window.

## 🌟 Why AgentGate?

- **Zero Dependencies:** Built entirely on Python standard libraries. No heavy dependencies (no PyTorch, no `requests`, no bloat). It installs cleanly into any project.
- **Context Budget Awareness:** Explicitly tracks token degradation. The built-in Tier System (Small/Medium/Large) adjusts agent behavior, limits loop iterations, and enforces context pauses before quality degrades.
- **DARRMS (Dynamic Attention Radius):** Aggressively collapses large files down to their AST signatures (imports and definitions) to save tokens, only expanding what the model needs to edit.
- **Zero-Trust Verification:** The `/verify` workflow forbids agents from using phrases like "looks correct" and enforces hard evidence gates requiring raw terminal output.

---

## 🚀 The Execution Pipeline

AgentGate isn't just an API wrapper; it's a rigorous workflow engine mimicking a high-performing engineering team.

| Command | Purpose |
|---------|---------|
| `/new-project` | Scaffolds the `.ai/` directory and bootstraps `ROADMAP.md`, `SPEC.md`, and `STATE.md`. |
| `/plan` | Triggers the **Discovery Protocol**, analyzes dependencies, and generates atomic, execution-ready XML `<task>` blocks. |
| `/execute` | Runs the plans. Features **UI Pre-Flight checks** and strictly enforces language rules. |
| `/verify` | The Auditor. Acts independently to verify actual codebase behavior (running tests and builds) and auto-generates gap closure plans if requirements fail. |
| `/sweep` | Dispatches subagents via μACP to perform codebase-wide refactoring and cleanup in parallel. |
| `/loop` | Autonomous goal-oriented execution with safe, model-aware iteration limits. |

---

## 🧠 Advanced Features

### μACP (Micro Agent Communication Protocol)
AgentGate does not make HTTP calls to external LLM APIs. Subagents are entirely decoupled and communicate via a shared whiteboard (`.ai/SUBAGENT_STATE.md`) using strict verbs (`ASK`, `TELL`, `OBSERVE`, `PING`). This allows you to spawn multiple agents locally (or via your native IDE chat) without complex API setups.

### Auto-Injected Language Rules
When generating code, AgentGate automatically routes to `src/lang_rules.py`, checking for project-specific overrides in `.ai/rules/` before falling back to its own strict, framework-level templates (Python, TypeScript, Go, Rust, Java, C#). It ensures idiomatic patterns are always followed.

### The UI Interrogator Protocol
Before writing any frontend code, the framework enforces a mandatory UI Pre-Flight check, classifying the target platform (Web/iOS/Android/Cross) and prompting the user for specific design systems to prevent generic, low-quality aesthetics.

---

## 🛠️ Installation

AgentGate can be injected into any existing project using the cross-platform installer.

```bash
# Clone the repository
git clone https://github.com/yourusername/agentgate.git

# Run the installer targeting your project directory
python agentgate/install.py /path/to/your/project
```

The installer will copy the AgentGate runtime into your project's `.ai/` directory, inject language rule templates, and automatically configure your `.gitignore`.

### Prerequisites
- Python 3.8+ (Standard Library only)
- An Agentic IDE, CLI, or Chat Client (Antigravity IDE/CLI, Cursor, Windsurf, Aider, Cline, Claude Desktop, etc.)

---

## 💻 CLI Usage

AgentGate ships with a powerful local orchestrator (`orchestrator.py`) to manage its state and tools.

**Collapse a large file to signatures only (DARRMS):**
```bash
python .ai/src/orchestrator.py --focus src/large_file.py
```

**Auto-load language coding standards:**
```bash
python .ai/src/orchestrator.py --rules-for src/api.ts
```

**Zero-Dependency Semantic Search (RAG):**
```bash
python .ai/src/orchestrator.py --query "authentication middleware"
```

**Generate a Subagent Briefing Block:**
```bash
python .ai/src/orchestrator.py --route ROUTE_TO_RESEARCHER
```

---

## 📖 Configuration
The framework adapts to your hardware via `.ai/MODEL_ENV.md` and `.ai/registry.json`. Modify the environment file to set your model tier (`SMALL`, `MEDIUM`, or `LARGE`), and the framework will automatically scale its delegation thresholds and pause gates.
