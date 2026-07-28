import os
import re
from pathlib import Path
from utils import safe_read, safe_append
from config import FOCUSED_FILES_PATH
def collapse_file_darrrms(filepath: str) -> str:
    """Dynamic Attention Radius: collapse file to imports + signatures only.
    
    Supports: Python, JavaScript, TypeScript, Rust, Go.
    Unknown extensions: returns first 30 lines (safe fallback).
    """
    if not os.path.exists(filepath):
        return f"[ERROR] File not found: {filepath}"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, OSError):
        return f"[BINARY] File {filepath} appears to be binary — skipped by DARRMS."

    ext = os.path.splitext(filepath)[1].lower()

    # --- Language dispatch map ---
    # Each entry: (import_patterns, signature_patterns)
    # Patterns are matched against the stripped line text using re.match
    LANGUAGE_PATTERNS = {
        ".py": (
            [r"^import ", r"^from "],
            [r"^def ", r"^class ", r"^async def "],
        ),
        ".js": (
            [r"^import ", r"^const .+ require\(", r"^var .+ require\(", r"^let .+ require\(", r"^export "],
            [r"^function ", r"^const \w+ = \(", r"^const \w+ = async", r"^class ", r"^async function ", r"^export (default |async )?function ", r"^export (default )?class "],
        ),
        ".ts": (
            [r"^import ", r"^export \{", r"^export \* from"],
            [r"^function ", r"^async function ", r"^export (default |async )?function ", r"^export (default )?class ", r"^class ", r"^const \w+ = \(", r"^const \w+: .+ = \(", r"^interface ", r"^type \w+", r"^export (interface|type) "],
        ),
        ".tsx": (
            [r"^import ", r"^export \{", r"^export \* from"],
            [r"^function ", r"^async function ", r"^export (default |async )?function ", r"^export (default )?class ", r"^class ", r"^const \w+ = \(", r"^const \w+: .+ = \(", r"^interface ", r"^type \w+"],
        ),
        ".jsx": (
            [r"^import ", r"^const .+ require\("],
            [r"^function ", r"^const \w+ = \(", r"^export (default )?function ", r"^class "],
        ),
        ".rs": (
            [r"^use ", r"^extern crate ", r"^pub use ", r"^mod "],
            [r"^pub fn ", r"^fn ", r"^pub async fn ", r"^async fn ", r"^pub struct ", r"^struct ", r"^pub enum ", r"^enum ", r"^pub trait ", r"^trait ", r"^impl "],
        ),
        ".go": (
            [r"^import ", r"^package "],
            [r"^func ", r"^type \w+ struct", r"^type \w+ interface", r"^var ", r"^const "],
        ),
    }

    STUB = "    // ... [collapsed by DARRMS] ..."
    STUB_PY = "    # ... [collapsed by DARRMS] ..."

    patterns = LANGUAGE_PATTERNS.get(ext)

    if patterns is None:
        preview = "".join(lines[:30])
        return f"[DARRMS FALLBACK — {ext or 'no extension'}] First 30 lines:\n{preview}"

    import_patterns, sig_patterns = patterns
    stub = STUB_PY if ext == ".py" else STUB

    output = [f"# DARRMS Collapsed: {filepath} ({ext})"]
    pending_decorator = None
    in_import_block = False

    for line in lines:
        rstripped = line.rstrip()
        stripped = rstripped.strip()

        if ext == ".go":
            if stripped == "import (":
                in_import_block = True
                output.append(rstripped)
                continue
            if in_import_block:
                if stripped == ")":
                    in_import_block = False
                    output.append(rstripped)
                else:
                    output.append(rstripped)
                continue

        if ext in (".py", ".js", ".ts", ".tsx", ".jsx") and stripped.startswith("@"):
            pending_decorator = rstripped
            continue

        matched = False
        for pat in import_patterns:
            if re.match(pat, stripped):
                if pending_decorator:
                    output.append(pending_decorator)
                    pending_decorator = None
                output.append(rstripped)
                matched = True
                break

        if not matched:
            for pat in sig_patterns:
                if re.match(pat, stripped):
                    if pending_decorator:
                        output.append(pending_decorator)
                        pending_decorator = None
                    output.append(rstripped)
                    output.append(stub)
                    matched = True
                    break

        if not matched:
            pending_decorator = None

    if len(output) <= 1:
        preview = "".join(lines[:10])
        return f"[DARRMS: no signatures found in {filepath}] First 10 lines:\n{preview}"

    # Track focused file
    abs_path = str(Path(filepath).resolve())
    safe_append(FOCUSED_FILES_PATH, f"{abs_path}\n")
    
    return "\n".join(output)
