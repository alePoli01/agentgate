import sys
import os
import shutil
import json
import argparse

def install():
    parser = argparse.ArgumentParser(description="AgentGate Installer")
    parser.add_argument("target_dir", type=str, help="Target directory for installation")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade existing installation")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall AgentGate")
    parser.add_argument("--yes", action="store_true", help="Confirm uninstall without prompting")
    args = parser.parse_args()

    target_dir = args.target_dir
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ai_dir = os.path.join(target_dir, ".ai")

    if args.uninstall:
        if not os.path.exists(ai_dir):
            print("AgentGate is not installed here.")
            sys.exit(0)
        
        # Self-protection guard
        if os.path.abspath(target_dir) == os.path.abspath(base_dir):
            print("ERROR: Refusing to uninstall the development repository.")
            sys.exit(1)
            
        if not args.yes:
            print(f"WARNING: This will delete {ai_dir} and all its contents.")
            print("Pass --yes to confirm.")
            sys.exit(0)
            
        try:
            shutil.rmtree(ai_dir)
            print("AgentGate uninstalled.")
            sys.exit(0)
        except OSError as e:
            print(f"Error during uninstall: {e}")
            sys.exit(1)

    if args.upgrade:
        if not os.path.exists(ai_dir):
            print("Not installed. Run without --upgrade to install fresh.")
            sys.exit(1)
            
        current_version = "unknown"
        v_file = os.path.join(ai_dir, "VERSION.md")
        if os.path.exists(v_file):
            try:
                with open(v_file, "r", encoding="utf-8") as f:
                    current_version = f.read().strip()
            except OSError:
                pass
                
        new_version = "unknown"
        nv_file = os.path.join(base_dir, "VERSION.md")
        if os.path.exists(nv_file):
            try:
                with open(nv_file, "r", encoding="utf-8") as f:
                    new_version = f.read().strip()
            except OSError:
                pass
                
        print(f"Upgrading from {current_version} to {new_version}")

    try:
        if not os.path.exists(target_dir):
            print(f"Error: Target directory '{target_dir}' does not exist.")
            sys.exit(1)
            
        os.makedirs(ai_dir, exist_ok=True)
    except FileNotFoundError:
        print(f"Error: Could not access target directory path '{target_dir}'.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied when accessing '{target_dir}'.")
        sys.exit(1)
    
    # 1. Copy directories (src/, core/, rules-templates/) to .ai/
    dirs_to_copy_ai = ["src", "core", "rules-templates"]
    files_updated = 0
    for d in dirs_to_copy_ai:
        source_dir = os.path.join(base_dir, d)
        target_dir_path = os.path.join(ai_dir, d)
        if os.path.exists(source_dir):
            try:
                shutil.copytree(source_dir, target_dir_path, dirs_exist_ok=True)
                print(f"Copied {d}/ to {target_dir_path}")
                files_updated += sum(len(files) for _, _, files in os.walk(source_dir))
            except Exception as e:
                print(f"Error copying {d}/: {e}")
                
    # 1.1. Copy skills/ to .agents/skills/
    agents_skills_dir = os.path.join(target_dir, ".agents", "skills")
    source_skills_dir = os.path.join(base_dir, "skills")
    if os.path.exists(source_skills_dir):
        try:
            shutil.copytree(source_skills_dir, agents_skills_dir, dirs_exist_ok=True)
            print(f"Copied skills/ to {agents_skills_dir}")
            files_updated += sum(len(files) for _, _, files in os.walk(source_skills_dir))
        except Exception as e:
            print(f"Error copying skills/: {e}")
                
    # 1.5. Clean up legacy root files from .ai/ directory
    legacy_files = ["FRAMEWORK_BOOTSTRAP.md", "VERSION.md"]
    for legacy_f in legacy_files:
        legacy_path = os.path.join(ai_dir, legacy_f)
        if os.path.exists(legacy_path):
            try:
                os.remove(legacy_path)
                print(f"Cleaned up legacy file: {legacy_path}")
            except OSError as e:
                print(f"Warning: Could not remove legacy file {legacy_path}: {e}")

    # 2. Copy root files (FRAMEWORK_BOOTSTRAP.md, VERSION.md)
    files_to_copy = ["FRAMEWORK_BOOTSTRAP.md", "VERSION.md"]
    for f_name in files_to_copy:
        source_file = os.path.join(base_dir, f_name)
        target_file = os.path.join(target_dir, f_name)
        if os.path.exists(source_file):
            try:
                shutil.copy2(source_file, target_file)
                print(f"Copied {f_name} to {target_file}")
                files_updated += 1
            except Exception as e:
                print(f"Error copying {f_name}: {e}")
        
    # 3. Safely merge registry.json
    registry_target = os.path.join(ai_dir, "registry.json")
    default_registry = {"valid_agents": ["RESEARCHER", "CODER", "AUDITOR", "ARCHITECT", "INVESTIGATOR"]}
    if not os.path.exists(registry_target):
        with open(registry_target, "w", encoding="utf-8") as f:
            json.dump(default_registry, f, indent=2)
        print("Created default registry.json.")
    else:
        print("registry.json already exists. Skipping to preserve custom configuration.")
        
    # 4. Inject .gitignore
    gitignore_path = os.path.join(target_dir, ".gitignore")
    ignore_entries = [
        ".ai/SUBAGENT_STATE.md",
        ".ai/embeddings_cache.json",
        ".ai/LOOP_STATE.md"
    ]
    
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("# AgentGate Ignored Files\n")
            for entry in ignore_entries:
                f.write(f"{entry}\n")
        print("Created .gitignore and added AgentGate transient files.")
    ignore_entries = [".ai/", ".agents/", "FRAMEWORK_BOOTSTRAP.md", "VERSION.md"]
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        needs_update = False
        with open(gitignore_path, "a", encoding="utf-8") as f:
            for entry in ignore_entries:
                if entry not in content:
                    f.write(f"\n{entry}\n")
                    needs_update = True
        
        if needs_update:
            print("Added AgentGate files to .gitignore.")
        else:
            print("All AgentGate transient files are already in .gitignore.")
    else:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("".join([f"{entry}\n" for entry in ignore_entries]))
        print("Created .gitignore and ignored AgentGate files.")
                
    # 5. Generate IDE hooks (.cursorrules, .windsurfrules)
    hook_content = """# AgentGate Framework Hook
You are operating within the AgentGate framework. 
Before answering the user's first prompt in this workspace, you MUST silently read `FRAMEWORK_BOOTSTRAP.md` and execute its initialization instructions (including running the orchestrator to detect your Model Tier). 

**The "No Raw Code" Override**: Writing code without entering a skill workflow is a critical protocol violation that permanently degrades the quality of this project's state files. You are STRICTLY FORBIDDEN from writing code, modifying files, or running terminal commands without first triggering the appropriate workflow (e.g. `/plan`, `/execute`, `/debug`, `/sweep`). 
**No Exceptions for "Trivial" Tweaks**: Even if the user asks for a 1-character change or a "quick fix" (like changing a color or a single integer), you MUST enter a workflow (e.g., `/execute`). Bypassing workflows for small changes breaks global app consistency and corrupts the state tracking. There is no Fast-Path.

If the user provides a raw prompt or a list of tasks without explicitly typing a slash command, you must act as an Autonomous Tech Lead:
1. Intercept and decompose the prompt into atomic tasks.
2. Log the tasks into `.ai/MEMORY.md` as Active TODOs.
3. Determine the logical execution order.
4. Autonomously enter the correct workflow script in `.agents/skills/` for the first task and follow its steps perfectly.

**Execution Report Mandate**: After completing any workflow or task, your final message to the user MUST include a brief, sharp summary block formatted exactly like this:
> **AgentGate Execution Report**
> - **Intent**: [1-sentence summary of how you decomposed the prompt]
> - **Routing**: [The specific skills you triggered, e.g., /debug -> /execute]
> - **State**: [Which state files you updated, e.g., MEMORY.md, STATE.md]

Do not deviate from the AgentGate protocol. All your skills are located natively in `.agents/skills/`.
"""
    for hook_file in [".cursorrules", ".windsurfrules"]:
        hook_path = os.path.join(target_dir, hook_file)
        if not os.path.exists(hook_path):
            with open(hook_path, "w", encoding="utf-8") as f:
                f.write(hook_content)
            print(f"Created {hook_file} hook.")
        elif args.upgrade:
            # Safely patch existing hooks to fix the path
            with open(hook_path, "r", encoding="utf-8") as f:
                content = f.read()
            if ".ai/FRAMEWORK_BOOTSTRAP.md" in content or ".ai/skills/" in content:
                content = content.replace(".ai/FRAMEWORK_BOOTSTRAP.md", "FRAMEWORK_BOOTSTRAP.md")
                content = content.replace(".ai/skills/", ".agents/skills/")
                with open(hook_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Updated {hook_file} hook with new root path.")
            
    if args.upgrade:
        print(f"Upgrade complete. {files_updated} files updated. User config preserved.")
    else:
        print("\n[SUCCESS] AgentGate installed successfully!")

if __name__ == "__main__":
    install()
