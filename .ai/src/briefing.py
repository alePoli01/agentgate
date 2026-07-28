import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional

from config import REGISTRY_PATH, SUBAGENT_STATE_PATH
from utils import safe_read

logger = logging.getLogger("agentgate")

def hook_architecture() -> Optional[str]:
    """Extract ## Scope & Altitude from ARCHITECTURE.md to inject into agent prompt.
    
    Searches for ARCHITECTURE.md in standard install locations.
    Returns the Scope & Altitude section text, or None if not found.
    """
    candidates = [
        ".ai/ARCHITECTURE.md",
        "llm-framework/ARCHITECTURE.md",
    ]
    arch_path = None
    for candidate in candidates:
        if os.path.exists(candidate):
            arch_path = candidate
            break

    if arch_path is None:
        return None

    try:
        content = safe_read(arch_path)
        lines = content.splitlines()
        
        in_scope = False
        scope_text = []
        for line in lines:
            if line.startswith("## Scope & Altitude"):
                in_scope = True
                continue
            elif in_scope and line.startswith("## "):
                break
            
            if in_scope:
                scope_text.append(line)
                
        return "\n".join(scope_text).strip() if scope_text else None
    except Exception as e:
        logger.error("Failed to parse ARCHITECTURE.md: %s", e)
        return None

def generate_briefing_block(agent_name: str, pending_payload: str) -> None:
    """Generate the briefing block for a newly routed subagent."""
    system_prompt = "You are a specialized AI agent. Complete the task below."
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                reg = json.load(f)
                if "agents" in reg and agent_name in reg["agents"]:
                    system_prompt = reg["agents"][agent_name].get("system_prompt", system_prompt)
        except Exception:
            logger.warning("Could not parse %s, using generic system prompt.", REGISTRY_PATH)

    scope_altitude = hook_architecture()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("============================================================")
    print("[AGENTGATE] BRIEFING BLOCK — Paste this into a new chat")
    print("============================================================")
    print("\n## Your Role")
    print(system_prompt)
    print("\n## Framework Bootstrap")
    print("Before starting, read the framework rules file:")
    print("`llm-framework/FRAMEWORK_BOOTSTRAP.md`")
    print("(This configures your behavior, memory rules, and token efficiency protocols.)")
    if scope_altitude:
        print("\n## Project Constraints (from ARCHITECTURE.md)")
        print(scope_altitude)
    print("\n## Shared Whiteboard")
    print(f"Read `{SUBAGENT_STATE_PATH}` to see the full task history and current state.")
    print("\n## Your Task (muACP ASK)")
    print(pending_payload)
    print("\n## Completion Protocol")
    print("When your task is complete, you MUST:")
    print(f"1. Update `{SUBAGENT_STATE_PATH}` — append a new row:")
    print(f"   | {timestamp} | TELL | {agent_name}: [your result summary, max 300 chars] | COMPLETE |")
    print("2. Output your full findings to the chat so the user can copy them back.")
    print("3. End your final message with exactly:")
    print("   `TELL [Orchestrator] -> Task complete. Whiteboard updated.`")
    print("\n## Constraints")
    print("- Do NOT read the entire project codebase blindly. Use grep/search tools first.")
    print("- Do NOT write code unless you are the CODER agent.")
    print("- Follow all rules in `llm-framework/core/core-rules.md`.")
    print("============================================================")
    
    print("\n[AGENTGATE] Next steps:")
    print("1. Open a new chat window (or use your platform's native agent spawn).")
    print("2. Paste the briefing block above as your first message.")
    print("3. When the subagent finishes, it will write a TELL row to SUBAGENT_STATE.md.")
    print("4. Run: python orchestrator.py --collect")
    print("   to surface the result back into this session.")
