import os
import json
import logging

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("agentgate")

# --- Paths ---
REGISTRY_PATH = ".ai/registry.json"
SUBAGENT_STATE_PATH = ".ai/SUBAGENT_STATE.md"
LOOP_STATE_PATH = ".ai/LOOP_STATE.md"
MEMORY_PATH = ".ai/MEMORY.md"
STATE_PATH = ".ai/STATE.md"
ROADMAP_PATH = ".ai/ROADMAP.md"
DECISIONS_PATH = ".ai/DECISIONS.md"
SPEC_PATH = ".ai/SPEC.md"
MANIFEST_PATH = ".ai/PROJECT_MANIFEST.md"
FOCUSED_FILES_PATH = ".ai/FOCUSED_FILES.txt"
ARCHITECTURE_PATH = ".ai/ARCHITECTURE.md"
SEARCH_INDEX_PATH = ".ai/search_index.json"
EMBEDDINGS_CACHE_PATH = ".ai/embeddings_cache.json"

# --- RAG Settings ---
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/embed")
EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")
BM25_K1 = 1.5   # Term frequency saturation
BM25_B = 0.75   # Length normalization
MAX_FILE_SIZE = 1024 * 1024  # 1 MB

IGNORE_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build"}
SCANNABLE_EXTS = {".py", ".md", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go",
                  ".java", ".cpp", ".c", ".cs", ".rb", ".php", ".html", ".css",
                  ".json", ".yaml", ".yml", ".toml"}
SKIP_EXTENSIONS = {".wasm", ".ico", ".svg", ".woff", ".ttf", ".db", ".sqlite", ".png", ".jpg", ".jpeg", ".zip", ".tar", ".gz", ".pdf", ".mp4"}

# --- Constants ---
VALID_AGENTS = ["RESEARCHER", "CODER", "AUDITOR", "ARCHITECT", "INVESTIGATOR"]
MU_ACP_VERBS = ["ASK", "TELL", "OBSERVE", "PING", "FAIL"]

try:
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
            if "valid_agents" in registry:
                VALID_AGENTS = registry["valid_agents"]
except (OSError, json.JSONDecodeError):
    pass
