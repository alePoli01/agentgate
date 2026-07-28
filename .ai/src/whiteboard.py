import os
import sys
import re
import json
import logging
from datetime import datetime
from typing import Optional

from config import SUBAGENT_STATE_PATH, REGISTRY_PATH, VALID_AGENTS, MU_ACP_VERBS
from utils import safe_read, safe_append

logger = logging.getLogger("agentgate")

import random
ROW_PATTERN = re.compile(
    r'^\|\s*(?P<task_id>T-[a-fA-F0-9]+)\s*\|\s*(?P<ts>[^|]+?)\s*\|\s*(?P<verb>TELL|FAIL|ASK)\s*\|\s*(?P<payload>.+?)\s*\|\s*(?P<status>COMPLETE|FAIL)\s*\|',
    re.IGNORECASE
)

def collect_subagent_result(task_id: Optional[str] = None) -> None:
    """Collect the latest completed subagent result from the whiteboard."""
    if not os.path.exists(SUBAGENT_STATE_PATH):
        print("[AGENTGATE] No completed subagent results found. Is the subagent still running?")
        sys.exit(0)
        
    content = safe_read(SUBAGENT_STATE_PATH)
    lines = content.splitlines()
        
    complete_rows = []
    for line in lines:
        if "| COMPLETE |" not in line and "| FAIL |" not in line:
            continue
        m = ROW_PATTERN.match(line.strip())
        if m:
            row_task_id = m.group("task_id").strip()
            if task_id and row_task_id != task_id:
                continue
            complete_rows.append({
                "task_id": row_task_id,
                "ts": m.group("ts").strip(),
                "verb": m.group("verb").strip(),
                "payload": m.group("payload").strip(),
                "status": m.group("status").strip().upper(),
            })
        else:
            logger.warning("Malformed TELL/FAIL row (unexpected format) — skipping:\n  %s", line.strip())

    if not complete_rows:
        print("[AGENTGATE] No completed subagent results found. Is the subagent still running?")
        sys.exit(0)

    if len(complete_rows) > 1:
        if task_id:
            logger.info("%d COMPLETE rows found for %s — collecting the most recent one.", len(complete_rows), task_id)
        else:
            logger.info("%d COMPLETE rows found — collecting the most recent one.", len(complete_rows))

    best = complete_rows[-1]
    payload = best["payload"]
    agent_name = payload.split(":")[0].strip() if ":" in payload else "UNKNOWN"
    status = best["status"]

    print("============================================================")
    print("[AGENTGATE] SUBAGENT RESULT COLLECTED")
    print("============================================================")
    print(f"Task ID: {best['task_id']}")
    print(f"Agent:   {agent_name}")
    print(f"Time:    {best['ts']}")
    print(f"Status:  {status}")
    print("Result:")
    print(payload)
    print("============================================================")
    print("Tip: Copy this result back into your main chat to continue.")
    print("============================================================")
    sys.exit(0)

def route_subagent(route: str, task_id: Optional[str] = None) -> None:
    """Route a subagent request and generate briefing block."""
    agent_name = route.replace("ROUTE_TO_", "").strip().upper()
    if agent_name not in VALID_AGENTS:
        print(f"[AGENTGATE ERROR] Invalid agent: {agent_name}. Valid agents are: {VALID_AGENTS}")
        sys.exit(1)
        
    if not os.path.exists(SUBAGENT_STATE_PATH):
        print("[AGENTGATE ERROR] No PENDING task found on the whiteboard.\nRun: python orchestrator.py --verb ASK --payload \"your task\" first.")
        sys.exit(1)
        
    content = safe_read(SUBAGENT_STATE_PATH)
    lines = content.splitlines()
        
    pending_payload = None
    for line in lines:
        if "| PENDING |" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 6:
                row_task_id = parts[1]
                if task_id and row_task_id != task_id:
                    continue
                pending_payload = parts[4].replace("\\|", "|")
                
    if not pending_payload:
        print("[AGENTGATE ERROR] No matching PENDING task found on the whiteboard.")
        sys.exit(1)
        
    from briefing import generate_briefing_block
    generate_briefing_block(agent_name, pending_payload)
    
    sys.exit(0)

def process_verb(verb: str, payload: str, task_id: Optional[str] = None) -> None:
    verb = verb.upper()
    if verb not in MU_ACP_VERBS:
        print(f"[AGENTGATE ERROR] Invalid verb: {verb}. Must be one of: {MU_ACP_VERBS}")
        sys.exit(1)
        
    if not payload:
        print("[AGENTGATE ERROR] Payload is required during execution stage.")
        sys.exit(1)
        
    if verb in ["TELL", "FAIL"]:
        from tier import get_tier_config
        tier_info = get_tier_config()
        limit = tier_info.get("tell_limit", 300)
        if len(payload) > limit:
            print(f"[AGENTGATE ERROR] {verb} payload exceeds the {limit}-character limit for the current context tier. Keep it concise.")
            sys.exit(1)
        
    if verb == "ASK" and not task_id:
        task_id = f"T-{random.randint(1000, 9999):04x}"
    elif not task_id:
        # For TELL/FAIL without explicit task_id, we should ideally know it. 
        # Fallback to T-0000 if legacy.
        logger.warning("TELL/FAIL called without an explicit task_id. Falling back to legacy T-0000.")
        task_id = "T-0000"

    print(f"[AGENTGATE EXECUTION] Initiating Subagent Protocol with verb {verb} (Task: {task_id}).")
    print(f"Payload: {payload}")
    print(f"Writing to Shared Mental Model ({SUBAGENT_STATE_PATH})...")
    
    os.makedirs(os.path.dirname(SUBAGENT_STATE_PATH), exist_ok=True)
    is_new = not os.path.exists(SUBAGENT_STATE_PATH) or os.path.getsize(SUBAGENT_STATE_PATH) == 0
    with open(SUBAGENT_STATE_PATH, "a", encoding="utf-8") as f:
        if is_new:
            f.write("| TaskID | Timestamp | Verb | Payload | Status |\n")
            f.write("|---|---|---|---|---|\n")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        safe_payload = payload.replace("|", "\\|").replace("\n", " ")
        status = "PENDING"
        if verb == "TELL":
            status = "COMPLETE"
        elif verb == "FAIL":
            status = "FAIL"
        f.write(f"| {task_id} | {timestamp} | {verb} | {safe_payload} | {status} |\n")
        
    print("[AGENTGATE SUCCESS] Subagent state updated. Subagent has been notified.")
    sys.exit(0)
