# Framework Architecture & Decisions

This file tracks major architectural blueprints and crucial decisions made during the construction of the LLM Framework, ensuring future agents understand *why* the system is structured the way it is.

## Index
1. [The Subagent Protocol Engine (`orchestrator.py`)](#1-the-subagent-protocol-engine-orchestratorpy)
2. [Dynamic Context Management](#2-dynamic-context-management)
3. [RAG Architecture: BM25-Primary Engine (`rag.py`)](#3-rag-architecture-bm25-primary-engine-ragpy)
4. [Real Orchestration Runtime (Phase 23)](#4-real-orchestration-runtime-phase-23)
5. [Loop System (`/loop`) — Phase 26](#5-loop-system-loop--phase-26)

## 1. The Subagent Protocol Engine (`orchestrator.py`)
Because local models struggle with JSON and complex routing, we use a Python orchestrator as a deterministic "Shield".
- **AgentGate Routing:** Validates `ROUTE_TO_X` and $\mu$ACP verbs deterministically.
- **Decoupled Tools:** Local models output simple text flags (`--tool read_file --params app.py`); the Python engine constructs the exact JSON schema.
- **SEARL Tool Graph:** Tools are hidden behind category nodes (e.g., `FILE_TOOLS`). Models must query the graph first, saving massive context tokens.

## 2. Dynamic Context Management
- **DARRMS Attention Radius:** Models use `--focus` to collapse a file's implementations while retaining `import` and `def` signatures (Aider-style).
- **MASK Arbiter (Semantic Gating):** The orchestrator uses `--arbiter` to physically block models from executing `read_file` on documents that have low semantic relevance to the active task, preventing context-window flooding.

## 3. RAG Architecture: BM25-Primary Engine (`rag.py`)
To enable semantic codebase search without bloat, we built a **zero-dependency RAG engine** using Okapi BM25 as the primary path.

**Decision Rationale:** We needed RAG, but forcing users to install `sentence-transformers` (which requires the 2.5GB PyTorch library) violated our core philosophy. We also ruled out making the Ollama API a hard requirement — if the user's local server is off, search must still work. The solution: implement BM25 from scratch using only the Python standard library, then layer Ollama as an *optional enhancement* on top.

**Architecture (as implemented in `rag.py`):**
1. **Primary Engine — Pure BM25 (always available, zero dependencies):** `rag.py` implements Okapi BM25 from scratch using only `math`, `re`, and `os` from the standard library. BM25 is the algorithm behind Elasticsearch and Lucene — for code retrieval it is often *more* precise than embeddings because code uses exact terms, not natural language synonyms.
2. **Optional Enhancement — Ollama via stdlib `urllib`:** If an Ollama server is reachable at `http://localhost:11434/api/embeddings`, `rag.py` uses it for embedding-based cosine similarity ranking instead of BM25. The HTTP call uses Python's built-in `urllib.request` — no `requests` library, no `sentence-transformers`, zero extra installs required.
3. **Caching — Active:** `CACHE_FILE = ".ai/embeddings_cache.json"` is actively used in `rag.py`. It features SHA256-keyed embedding caching for file content hashing, JSON-based persistent storage, and automatic eviction of stale entries to maintain consistency.

## Scope & Altitude
*This section establishes the Context Altitude for this project.*
- **Scope:** Fast, Local, Zero-Bloat Framework.
- **Constraints:** Do NOT use heavy dependencies (e.g., PyTorch, TensorFlow) unless explicitly required as a fallback. Prioritize Python standard libraries.
- **Design Pattern:** Functional, script-based tools over heavily abstracted OOP.

*Date Logged: Phase 14 Completion.*

## 4. Real Orchestration Runtime (Phase 23)

**Research Foundation:**
- **μACP** (arXiv 2601.00219): Formal calculus (ASK/TELL/OBSERVE/PING) for resource-constrained agent communication. Prevents hallucination by restricting free-form agent messaging to 4 strict verbs.
- **TeamMedAgents / Salas et al. Teamwork Theory**: Shared Mental Models outperform raw transcript passing. Agents synchronize via a structured whiteboard (`.ai/SUBAGENT_STATE.md`), not conversation history dumps.

**Architecture Decision: No HTTP Dispatch**
The orchestrator does NOT make HTTP calls to Ollama or any LLM API.
Subagents are new chat sessions — opened manually or via the host platform's native spawn.
Reason: Making an API call per subagent process is not sustainable for solo developers.
The model already running in the parent chat IS the resource. Spawning a new conversation reuses it.

### The Full Handshake Pipeline

```
Parent Agent (current chat session)
     |
     | 1. python orchestrator.py --verb ASK --payload "task"
     v
.ai/SUBAGENT_STATE.md          ← PENDING row written
     |
     | 2. python orchestrator.py --route ROUTE_TO_<AGENT>
     v
Briefing Block printed to stdout
(copy-pasteable prompt: role + bootstrap ref + whiteboard ref + task + TELL protocol)
     |
     | 3. Human (or platform native spawn) opens new chat,
     |    pastes Briefing Block
     v
Subagent Chat Session
- Reads FRAMEWORK_BOOTSTRAP.md (detects it is a subagent via "BRIEFING BLOCK" signal)
- Reads .ai/SUBAGENT_STATE.md (OBSERVE)
- Executes task
- Appends TELL row to .ai/SUBAGENT_STATE.md (Status: COMPLETE)
- Outputs full findings to chat
     |
     | 4. python orchestrator.py --collect
     v
Most recent COMPLETE row surfaced to parent chat
```

### Key Design Constraints
- **Zero HTTP**: orchestrator.py uses only Python stdlib. No requests, no httpx, no urllib LLM calls.
- **Blocking by convention**: Parent waits for subagent to complete before calling --collect. Sequential mandate preserved.
- **Whiteboard as message bus**: .ai/SUBAGENT_STATE.md is the ONLY inter-agent communication channel. No direct chat-to-chat passing.
- **Context protection**: Subagent receives only last 10 whiteboard rows + task (from Briefing Block). Not the full parent context.
- **300-char TELL limit**: TELL row payloads are capped at 300 chars in the whiteboard table. Full output goes to the subagent's chat for the human to read.

## 5. Loop System (`/loop`) — Phase 26

The `/loop` workflow provides autonomous goal-oriented execution that persists until a verifiable termination condition is met.

### Three-Layer Design

```
Skill (loop.md)
  - Agent reads this; it governs the iteration cycle and safety gates
  - Model-aware: reads MODEL_ENV.md to branch on local vs. cloud rules
       |
       v
Runtime (orchestrator.py --loop-check "<cmd>")
  - Deterministic exit-code runner
  - Runs the DONE WHEN shell command via subprocess
  - Writes structured result to .ai/LOOP_STATE.md
  - Exits with same code as the shell command
       |
       v
State (.ai/LOOP_STATE.md)
  - Persists across iterations and context slides
  - Tracks: goal, model type, max iterations, iteration count,
    last result, last stdout/stderr, failed approaches
  - Read via: orchestrator.py --loop-status
```

### Model-Aware Guardrails

| Setting | Local | Cloud |
|---------|-------|-------|
| MAX_ITERATIONS (default) | 3 | 10 |
| Context gate (pause at) | 40% | 70% |
| Strike threshold | 2 stagnant | 3 stagnant |
| DARRMS focus check | Mandatory per iteration | Optional |
| Override file | `core/loop-overrides.md` | `loop.md` defaults |

### Key Design Decisions
- **Exit-code based termination**: `--loop-check` makes the `DONE WHEN` condition machine-verifiable. Not prose. Not trust-based. Binary: 0 = done, non-0 = not done.
- **State persistence**: `LOOP_STATE.md` is written after every `--loop-check` call. If context slides mid-loop, the next iteration reads the full state from file — not from context.
- **No spawning**: The loop runs in the current chat session. Each iteration is a step in the same conversation. This preserves the zero-HTTP-dispatch principle from the subagent protocol.
- **UI work requires human gate**: Frontend goals cannot self-certify. `DONE WHEN` must include a lighthouse/screenshot check, or an explicit `checkpoint:human-verify`.

