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
    
    # 1. Copy directories (src/, skills/, core/, rules-templates/)
    dirs_to_copy = ["src", "skills", "core", "rules-templates"]
    files_updated = 0
    for d in dirs_to_copy:
        source_dir = os.path.join(base_dir, d)
        target_dir_path = os.path.join(ai_dir, d)
        if os.path.exists(source_dir):
            try:
                shutil.copytree(source_dir, target_dir_path, dirs_exist_ok=True)
                print(f"Copied {d}/ to {target_dir_path}")
                files_updated += sum(len(files) for _, _, files in os.walk(source_dir))
            except Exception as e:
                print(f"Error copying {d}/: {e}")
                
    # 2. Copy root files (ARCHITECTURE.md, FRAMEWORK_BOOTSTRAP.md, VERSION.md)
    files_to_copy = ["ARCHITECTURE.md", "FRAMEWORK_BOOTSTRAP.md", "VERSION.md"]
    for f_name in files_to_copy:
        source_file = os.path.join(base_dir, f_name)
        target_file = os.path.join(ai_dir, f_name)
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
    else:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        with open(gitignore_path, "a", encoding="utf-8") as f:
            added = False
            for entry in ignore_entries:
                if entry not in content:
                    if not added:
                        f.write("\n# AgentGate Ignored Files\n")
                        added = True
                    f.write(f"{entry}\n")
            if added:
                print("Appended new AgentGate transient files to existing .gitignore.")
            else:
                print("All AgentGate transient files are already in .gitignore.")
            
    if args.upgrade:
        print(f"Upgrade complete. {files_updated} files updated. User config preserved.")
    else:
        print("\n[SUCCESS] AgentGate installed successfully!")

if __name__ == "__main__":
    install()
