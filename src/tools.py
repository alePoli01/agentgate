import os
import sys
import json
import shlex
import pathlib
import subprocess
import logging
from typing import List

from searl import TOOL_GRAPH
from tier import get_tier_config
from config import FOCUSED_FILES_PATH
from utils import safe_read

logger = logging.getLogger("agentgate")

def query_tool_graph(category: str) -> None:
    """Print the available tools in a category."""
    category = category.upper()
    if category not in TOOL_GRAPH:
        print(f"[ERROR] Category {category} not found. Available categories: {list(TOOL_GRAPH.keys())}")
        sys.exit(1)
        
    print(f"Category: {category}")
    print(f"Description: {TOOL_GRAPH[category]['description']}")
    print("Available Tools:")
    for tool_name, tool_data in TOOL_GRAPH[category]["tools"].items():
        print(f"  - {tool_name} (Requires params: {', '.join(tool_data['params'])})")
    print("\nTo use a tool, run: python orchestrator.py --tool <tool_name> --params <param1> <param2> ...")
    sys.exit(0)

def execute_tool(tool: str, params: List[str]) -> None:
    """Execute a tool natively if supported, or output JSON payload."""
    tool_schema = None
    for cat in TOOL_GRAPH.values():
        if tool in cat["tools"]:
            tool_schema = cat["tools"][tool]
            break
            
    if not tool_schema:
        print(f"[ERROR] Tool {tool} not found in the Tool Graph.")
        sys.exit(1)
        
    required_params = tool_schema["params"]
    provided_params = params or []
    
    if len(provided_params) != len(required_params):
        print(f"[ERROR] Tool {tool} requires {len(required_params)} parameters: {required_params}")
        print(f"You provided {len(provided_params)} parameters.")
        sys.exit(1)
        
    json_payload = {"tool": tool, "arguments": {}}
    for i, param_name in enumerate(required_params):
        json_payload["arguments"][param_name] = provided_params[i]
        
    print(f"[TOOL START] Executing {tool}...")
    
    try:
        if tool == "read_file":
            filepath = json_payload["arguments"]["filepath"]
            p = pathlib.Path(filepath).resolve()
            if not p.is_relative_to(pathlib.Path.cwd().resolve()):
                print(f"[ERROR] Path traversal detected: {filepath} is outside project root")
                sys.exit(1)
            
            if not p.exists():
                print(f"[ERROR] File not found: {filepath}")
                sys.exit(1)
                
            tier_config = get_tier_config()
            if tier_config.get("darrms_mandatory", False):
                focused = safe_read(FOCUSED_FILES_PATH).splitlines()
                if str(p) not in focused:
                    print(f"[DARRMS REQUIRED] You must run --focus {filepath} before reading this file on {tier_config['tier']} tier.")
                    sys.exit(1)
                    
            with open(filepath, "r", encoding="utf-8") as f:
                print(f.read())
                
        elif tool == "write_file":
            filepath = json_payload["arguments"]["filepath"]
            p = pathlib.Path(filepath).resolve()
            if not p.is_relative_to(pathlib.Path.cwd().resolve()):
                print(f"[ERROR] Path traversal detected: {filepath} is outside project root")
                sys.exit(1)
                
            content = json_payload["arguments"]["content"]
            dir_path = os.path.dirname(p)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[SUCCESS] Wrote to {filepath}")
            
        elif tool == "run_command":
            command_str = json_payload["arguments"]["command"]
            print(f"Running: {command_str}\n---")
            command = shlex.split(command_str)
            result = subprocess.run(command, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, file=sys.stderr, end="")
            print("---")
            print(f"Exit code: {result.returncode}")
            
        else:
            print(f"[SUCCESS] Tool JSON payload built (native execution not implemented for {tool}):")
            print(json.dumps(json_payload, indent=2))
            
    except Exception as e:
        print(f"[ERROR] Tool execution failed: {e}")
        sys.exit(1)
        
    sys.exit(0)
