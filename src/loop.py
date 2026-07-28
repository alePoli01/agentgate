import os
import sys
import shlex
import subprocess
import logging
from datetime import datetime
from typing import Optional

from config import LOOP_STATE_PATH
from utils import safe_read, safe_write
from tier import get_tier_config

logger = logging.getLogger("agentgate")

def run_loop_check(cmd: str) -> None:
    """Run the DONE WHEN command and record result in .ai/LOOP_STATE.md."""
    existing = safe_read(LOOP_STATE_PATH)
    
    iteration = 1
    consecutive_fails = 0
    for line in existing.splitlines():
        if line.startswith("- Iteration:"):
            try:
                iteration = int(line.split(":")[1].strip().split("/")[0]) + 1
            except Exception:
                pass
        if line.startswith("- Consecutive fails:"):
            try:
                consecutive_fails = int(line.split(":")[1].strip())
            except Exception:
                pass
                
    tier_config = get_tier_config()
    if iteration > tier_config["max_iterations"]:
        print(f"[MAX_ITERATIONS EXCEEDED] Loop limit of {tier_config['max_iterations']} reached for {tier_config['tier']} tier. Loop aborted.")
        sys.exit(1)

    logger.info("Running loop check: %s", cmd)
    try:
        command = shlex.split(cmd)
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        exit_code = result.returncode
        stdout = result.stdout.strip()[:500]
        stderr = result.stderr.strip()[:200]
    except subprocess.TimeoutExpired:
        exit_code = -1
        stdout = ""
        stderr = "[TIMEOUT] Command exceeded 60 seconds"
    except Exception as e:
        exit_code = -2
        stdout = ""
        stderr = f"[ERROR] {e}"

    status = "PASS" if exit_code == 0 else "FAIL"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    if exit_code == 0:
        consecutive_fails = 0
    else:
        consecutive_fails += 1

    goal_line = "- Goal: (not set)"
    failed_line = "- Failed approaches: (none)"
    model_line = "- Model type: (unknown)"
    max_line = "- Max iterations: (not set)"
    
    for line in existing.splitlines():
        if line.startswith("- Goal:"):
            goal_line = line
        if line.startswith("- Failed approaches:"):
            failed_line = line
        if line.startswith("- Model type:"):
            model_line = line
        if line.startswith("- Max iterations:"):
            max_line = line

    if consecutive_fails >= 3:
        failed_line = failed_line.rstrip()
        failed_line += f"; [{timestamp}] {cmd[:80]}"

    new_state = f"""## /loop State
{goal_line}
{model_line}
{max_line}
- Iteration: {iteration}
- Consecutive fails: {consecutive_fails}
- Last check: {timestamp}
- Last command: {cmd[:120]}
- Last result: {status} (exit code: {exit_code})
- Last stdout: {stdout if stdout else '(empty)'}
- Last stderr: {stderr if stderr else '(none)'}
{failed_line}
"""
    safe_write(LOOP_STATE_PATH, new_state)

    if exit_code == 0:
        logger.info("[LOOP CHECK] PASS -- goal achieved (exit code 0)")
    else:
        logger.info("[LOOP CHECK] FAIL -- goal not yet met (exit code %s)", exit_code)
        if stderr:
            logger.info("[LOOP CHECK] stderr: %s", stderr)

    sys.exit(exit_code)

def print_loop_status() -> None:
    """Print the current loop state from .ai/LOOP_STATE.md."""
    content = safe_read(LOOP_STATE_PATH)
    if not content:
        logger.info("[LOOP STATUS] No active loop. Run /loop to start one.")
        sys.exit(0)
    
    # We still print to stdout because this is output for the user/agent
    print("============================================================")
    print("[AGENTGATE] LOOP STATUS")
    print("============================================================")
    print(content)
    print("============================================================")
    sys.exit(0)
