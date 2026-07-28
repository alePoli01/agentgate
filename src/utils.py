import os
import logging
from typing import Optional

logger = logging.getLogger("agentgate")

def safe_read(filepath: str, default: str = "") -> str:
    """Safely read a file, returning a default if not found or on error."""
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("Failed to read %s: %s", filepath, e)
        return default

def safe_write(filepath: str, content: str) -> bool:
    """Safely write to a file, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except OSError as e:
        logger.error("Failed to write %s: %s", filepath, e)
        return False

def safe_append(filepath: str, content: str) -> bool:
    """Safely append to a file, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content)
        return True
    except OSError as e:
        logger.error("Failed to append to %s: %s", filepath, e)
        return False

def detect_model_env() -> str:
    """Detect the model environment from .ai/MODEL_ENV.md, defaulting to LOCAL."""
    from config import MANIFEST_PATH # Using MANIFEST_PATH or .ai/MODEL_ENV.md
    env_path = ".ai/MODEL_ENV.md"
    content = safe_read(env_path).strip()
    if content.upper() in ["LOCAL", "CLOUD"]:
        return content.upper()
    return "LOCAL"
