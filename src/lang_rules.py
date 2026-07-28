"""
AgentGate Language Rules Resolver
Maps file extensions to language-specific coding standards.
Lookup order: .ai/rules/<lang>-standards.md → rules-templates/<lang>-standards.md
"""
import sys
import os
import pathlib
import logging

logger = logging.getLogger("agentgate")

# Map extensions to language standard names
EXT_TO_LANG = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".cpp": "cpp",
    ".c": "c",
}

def get_rules_for_file(filepath: str) -> None:
    """Print the language-specific rules for a given file path."""
    ext = pathlib.Path(filepath).suffix.lower()
    lang = EXT_TO_LANG.get(ext)
    
    if not lang:
        print(f"[RULES] No specific rules for extension '{ext}'. Adhere to general best practices.")
        return

    rule_filename = f"{lang}-standards.md"
    
    # Priority 1: Project-specific rules in .ai/rules/
    project_rules_path = pathlib.Path(f".ai/rules/{rule_filename}")
    if project_rules_path.exists():
        with open(project_rules_path, "r", encoding="utf-8") as f:
            print(f"[RULES] Loaded project rules for {lang.capitalize()} ({project_rules_path})")
            print("---")
            print(f.read())
            print("---")
        return

    # Priority 2: Framework templates in rules-templates/
    framework_dir = pathlib.Path(__file__).parent.parent
    template_path = framework_dir / "rules-templates" / rule_filename
    
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            print(f"[RULES] Loaded framework template for {lang.capitalize()} ({template_path})")
            print("---")
            print(f.read())
            print("---")
    else:
        print(f"[RULES] No rules found for {lang.capitalize()}. Adhere to general best practices.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_rules_for_file(sys.argv[1])
    else:
        print("Usage: python lang_rules.py <filepath>")
