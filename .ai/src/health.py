import os
import re
import datetime
import logging

from config import MEMORY_PATH, DECISIONS_PATH, STATE_PATH, SPEC_PATH, MANIFEST_PATH
from utils import safe_read, safe_write

logger = logging.getLogger("agentgate")

def run_health_check() -> None:
    """Audit lifecycle files against rules and print health report."""
    LIFECYCLE_FILES = [
        SPEC_PATH,
        MEMORY_PATH,
        STATE_PATH,
        DECISIONS_PATH,
        ".ai/ROADMAP.md",
    ]
    
    print("============================================================")
    print("[AGENTGATE] HEALTH CHECK")
    print("============================================================")
    
    missing = []
    for f in LIFECYCLE_FILES:
        if not os.path.exists(f):
            missing.append(f)
    
    if missing:
        print("[SETUP REQUIRED] The following lifecycle files are missing:")
        for f in missing:
            print(f"  [MISSING] {f}")
        print("Run the /new-project workflow to scaffold them.")
        print("============================================================")
        return
    
    print("[OK] All lifecycle files present.\n")
    
    # Check 2: MEMORY.md
    try:
        memory_content = safe_read(MEMORY_PATH)
        active_section = memory_content.split("## Archive")[0] if "## Archive" in memory_content else memory_content
        todo_count = active_section.count("- [ ]")
        if todo_count > 5:
            print(f"[WARN] MEMORY.md has {todo_count} active TODOs (limit: 5). Archive completed items.")
        else:
            print(f"[OK] MEMORY.md: {todo_count}/5 active TODOs.")
    except Exception as e:
        logger.warning("Could not read %s: %s", MEMORY_PATH, e)
    
    # Check 3: DECISIONS.md
    try:
        decisions_content = safe_read(DECISIONS_PATH)
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", decisions_content)
        if dates:
            last_date_str = sorted(dates)[-1]
            last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d").date()
            today = datetime.date.today()
            days_since = (today - last_date).days
            if days_since > 7:
                print(f"[STALE] DECISIONS.md — last entry: {last_date_str} ({days_since} days ago). Review and update.")
            else:
                print(f"[OK] DECISIONS.md — last entry: {last_date_str} ({days_since} days ago).")
        else:
            print("[WARN] DECISIONS.md — no dated entries found. Add decisions as you work.")
    except Exception as e:
        logger.warning("Could not parse %s: %s", DECISIONS_PATH, e)
    
    # Check 4: STATE.md
    try:
        state_content = safe_read(STATE_PATH)
        if "Phase**: None" in state_content or "Status**: Setup" in state_content:
            print("[WARN] STATE.md — project is not yet started. Complete SPEC.md and run /plan 1.")
        else:
            print("[OK] STATE.md — project in progress.")
    except Exception as e:
        logger.warning("Could not read %s: %s", STATE_PATH, e)
    
    # Check 5: SPEC.md
    try:
        spec_content = safe_read(SPEC_PATH)
        if "FINALIZED" in spec_content:
            print("[OK] SPEC.md — FINALIZED. Planning is unlocked.")
        elif "DRAFT" in spec_content:
            print("[WARN] SPEC.md — still DRAFT. Planning is LOCKED until you finalize the spec.")
        else:
            print("[WARN] SPEC.md — no status found. Add 'Status: FINALIZED' or 'Status: DRAFT'.")
    except Exception as e:
        logger.warning("Could not read %s: %s", SPEC_PATH, e)
    
    print("\n============================================================")
    print("Tip: Run --health-check at the start of every session.")
    print("============================================================")

def scan_project() -> None:
    """Walk the project tree and produce .ai/PROJECT_MANIFEST.md."""
    IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".ai", "venv", ".venv",
                   "dist", "build", ".next", "target", ".cache"}
    LANGUAGE_MAP = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".tsx": "TypeScript/React", ".jsx": "JavaScript/React",
        ".rs": "Rust", ".go": "Go", ".java": "Java",
        ".cpp": "C++", ".c": "C", ".cs": "C#",
        ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
        ".kt": "Kotlin", ".md": "Markdown", ".html": "HTML",
        ".css": "CSS", ".scss": "CSS/SCSS", ".json": "JSON",
        ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
    }
    DOC_PATTERNS = [
        ("README", r"readme", "README file"),
        ("ARCHITECTURE", r"architect", "Architecture doc"),
        ("CHANGELOG", r"changelog", "Changelog"),
        ("SPEC / PRD", r"spec|prd|requirements", "Spec or PRD"),
        ("DECISIONS", r"decisions?|adr", "Decision log"),
        ("API_DOCS", r"api[-_]?docs?|openapi|swagger", "API docs"),
        ("TESTS", r"test|spec", "Test directory"),
        ("DOCKERFILE", r"dockerfile", "Dockerfile"),
        ("CI_CONFIG", r"\.github|\.gitlab-ci|jenkinsfile|\.circleci", "CI config"),
    ]

    lang_counts = {}
    file_count = 0
    tree_lines = []
    detected_docs = []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in sorted(dirs) if d not in IGNORE_DIRS]

        depth = root.replace("\\", "/").count("/")
        indent = "  " * depth
        folder_name = os.path.basename(root) if root != "." else "."
        tree_lines.append(f"{indent}{folder_name}/")

        folder_lower = folder_name.lower()
        for label, pattern, desc in DOC_PATTERNS:
            if re.search(pattern, folder_lower, re.IGNORECASE):
                detected_docs.append(f"- `{root}` — {desc}")

        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()
            file_count += 1

            lang = LANGUAGE_MAP.get(ext, f"Other ({ext})" if ext else "Other (no ext)")
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

            file_indent = "  " * (depth + 1)
            tree_lines.append(f"{file_indent}{filename}")

            fname_lower = filename.lower()
            for label, pattern, desc in DOC_PATTERNS:
                if re.search(pattern, fname_lower, re.IGNORECASE):
                    detected_docs.append(f"- `{filepath}` — {desc}")

    lang_sorted = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)
    lang_block = "\n".join(f"  - {lang}: {count} file(s)" for lang, count in lang_sorted)

    detected_docs = sorted(set(detected_docs))
    docs_block = "\n".join(detected_docs) if detected_docs else "  (none detected)"

    primary_lang = lang_sorted[0][0] if lang_sorted else "Unknown"

    manifest = f"""# PROJECT MANIFEST
> Generated by AgentGate `--scan-project` on {datetime.date.today().isoformat()}
> Use this file as input to the ARCHITECT agent to produce ARCHITECTURE.md.
> Do NOT edit this file manually — re-run --scan-project to refresh.

## Summary
- **Total files scanned**: {file_count}
- **Primary language**: {primary_lang}
- **Scan date**: {datetime.date.today().isoformat()}

## Language Breakdown
{lang_block}

## Detected Existing Documentation
{docs_block}

## Project Tree
```
{chr(10).join(tree_lines)}
```

## Instructions for ARCHITECT Agent
You are the ARCHITECT agent. Read this manifest and produce `.ai/ARCHITECTURE.md`.

Rules:
1. Use only information present in this manifest. Do NOT invent structure.
2. For anything you cannot confidently infer from the file tree, write [UNMAPPED].
3. Identify the likely framework from the file/folder patterns (e.g., `pages/` = Next.js, `src/main.rs` = Rust binary).
4. List the entry points you can identify from the tree.
5. Write a confidence score (0-100%) next to each section you produce.
"""

    safe_write(MANIFEST_PATH, manifest)

    print("============================================================")
    print("[AGENTGATE] PROJECT SCAN COMPLETE")
    print("============================================================")
    print(f"Files scanned : {file_count}")
    print(f"Primary lang  : {primary_lang}")
    print(f"Manifest saved: {MANIFEST_PATH}")
    print("")
    print("NEXT STEP:")
    print("  Run: python orchestrator.py --route ROUTE_TO_ARCHITECT")
    print("  Paste the Briefing Block into a new chat.")
    print(f"  The ARCHITECT will read {MANIFEST_PATH} and produce ARCHITECTURE.md.")
    print("============================================================")
