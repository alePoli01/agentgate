import argparse
import sys
import os
import subprocess

# Ensure we can import from src when run directly
sys.path.insert(0, os.path.dirname(__file__))

from health import run_health_check, scan_project
from loop import run_loop_check, print_loop_status
from whiteboard import collect_subagent_result, route_subagent, process_verb
from tools import query_tool_graph, execute_tool
from darrms import collapse_file_darrrms
from arbiter import run_arbiter
from tier import print_tier_info, get_tier_banner
from lang_rules import get_rules_for_file

def main():
    print(get_tier_banner())
    parser = argparse.ArgumentParser(description="AgentGate Orchestrator Engine")
    
    # Health Check
    parser.add_argument("--health-check", action="store_true", help="Audit all lifecycle files for staleness and print a health report")
    parser.add_argument("--scan-project", action="store_true", help="Scan the current project directory and produce .ai/PROJECT_MANIFEST.md")
    parser.add_argument("--tier-info", action="store_true", help="Resolve the current model tier from MODEL_ENV.md and print config")
    
    # Loop System Arguments
    parser.add_argument("--loop-check", type=str, metavar="CMD",
        help="Run a DONE WHEN shell command and write result to .ai/LOOP_STATE.md")
    parser.add_argument("--loop-status", action="store_true",
        help="Print the current loop state from .ai/LOOP_STATE.md")
    parser.add_argument("--run-tests", action="store_true",
        help="Run the project test suite (tests/) and exit with its exit code.")
    
    # Subagent Protocol Arguments
    parser.add_argument("--route", type=str, help="Routing token (e.g., ROUTE_TO_AUDITOR)")
    parser.add_argument("--verb", type=str, help="muACP Verb (ASK, TELL, OBSERVE, PING)")
    parser.add_argument("--payload", type=str, help="The instruction payload")
    parser.add_argument("--collect", action="store_true", help="Collect the latest completed subagent result from the whiteboard")
    parser.add_argument("--task-id", type=str, help="Specific Task ID to collect, route, or check")
    parser.add_argument("--ping", action="store_true", help="Check status of a running task")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds for --ping to report [TIMEOUT]")
    
    # Tool Execution Arguments
    parser.add_argument("--query-graph", type=str, help="Query a tool category (e.g., FILE_TOOLS)")
    parser.add_argument("--tool", type=str, help="The tool to execute")
    parser.add_argument("--params", type=str, nargs="+", help="Sequential parameters for the tool")
    
    # DARRMS Argument
    parser.add_argument("--focus", type=str, help="Apply Dynamic Attention Radius to a file")
    
    # Language Rules Argument
    parser.add_argument("--rules-for", type=str, metavar="FILEPATH",
        help="Print language-specific coding standards for the given file's language")
    
    # Phase 13 Arguments (RAG & Arbiter)
    parser.add_argument("--query", type=str, help="Perform a semantic search over the codebase")
    parser.add_argument("--arbiter", type=str, nargs=2, metavar=("QUERY", "FILEPATH"), help="Check if a file passes the semantic relevance threshold")
    
    args = parser.parse_args()
    
    if args.health_check:
        run_health_check()
        sys.exit(0)
        
    if args.scan_project:
        scan_project()
        sys.exit(0)

    if args.ping:
        if args.timeout is not None:
            from config import SUBAGENT_STATE_PATH
            import os
            from datetime import datetime
            if os.path.exists(SUBAGENT_STATE_PATH):
                with open(SUBAGENT_STATE_PATH, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for line in reversed(lines):
                    if "| PENDING |" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 6:
                            row_task_id = parts[1]
                            if args.task_id and row_task_id != args.task_id:
                                continue
                            ts_str = parts[2]
                            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                            if (datetime.now() - ts).total_seconds() > args.timeout:
                                print(f"[TIMEOUT] Task {row_task_id} exceeded {args.timeout} seconds.")
                                sys.exit(0)
                            else:
                                print(f"[PING] Task {row_task_id} is still pending.")
                                sys.exit(0)
            print("[PING] No pending task found.")
        else:
            print("[PING] OK")
        sys.exit(0)

    if args.tier_info:
        print_tier_info()
        sys.exit(0)

    if args.loop_check:
        run_loop_check(args.loop_check)

    if args.loop_status:
        print_loop_status()
        
    if args.run_tests:
        import pathlib
        tests_dir = str(pathlib.Path(__file__).parent.parent / "tests")
        print(f"[TEST GATE] Running test suite: python -m unittest discover {tests_dir} -v")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", tests_dir, "-v"],
                capture_output=True, text=True, timeout=120
            )
            output = result.stdout + result.stderr
            lines = output.strip().splitlines()
            print(output)
            summary = next((l for l in reversed(lines) if l.strip()), "")
            if result.returncode == 0:
                print(f"[TEST GATE] PASS — {summary}")
            else:
                print(f"[TEST GATE] FAIL — {summary}")
                if result.stderr:
                    print(f"[TEST GATE] stderr: {result.stderr.strip()[:300]}")
        except subprocess.TimeoutExpired:
            print("[TEST GATE] FAIL — Test suite exceeded 120 second timeout")
            result = type("R", (), {"returncode": -1})()
        except Exception as e:
            print(f"[TEST GATE] FAIL — Could not run test suite: {e}")
            result = type("R", (), {"returncode": -2})()
        sys.exit(result.returncode)

    if args.arbiter:
        query, filepath = args.arbiter
        run_arbiter(query, filepath)
        
    if args.query:
        try:
            import rag
            results = rag.query_codebase(args.query)
            print(f"Semantic Search Results for: '{args.query}'")
            for res in results:
                print(f"  - {res['file']} (Score: {res['score']:.2f})")
        except Exception as e:
            print(f"[ERROR] RAG failed: {e}")
        sys.exit(0)
    
    if args.focus:
        import pathlib
        p = pathlib.Path(args.focus).resolve()
        if not p.is_relative_to(pathlib.Path.cwd().resolve()):
            print(f"[ERROR] Path traversal detected: {args.focus} is outside project root")
            sys.exit(1)
            
        print(f"Applying Dynamic Attention Radius to {args.focus}...")
        print("---")
        print(collapse_file_darrrms(args.focus))
        print("---")
        sys.exit(0)
        
    if args.rules_for:
        get_rules_for_file(args.rules_for)
        sys.exit(0)

    if args.query_graph:
        query_tool_graph(args.query_graph)
        
    if args.tool:
        execute_tool(args.tool, args.params)
    
    if args.collect:
        collect_subagent_result(args.task_id)

    if args.route:
        route_subagent(args.route, args.task_id)
        
    if args.verb:
        process_verb(args.verb, args.payload, args.task_id)
        
    parser.print_help()

if __name__ == "__main__":
    main()
