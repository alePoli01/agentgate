---
name: "upgrade"
description: "The Framework Upgrade Workflow. Automatically updates the current project's framework files using the local agentgate install script."
environment_target: "universal"
priority: 2
---
# The Upgrade Workflow

**Trigger**: The user explicitly types `/upgrade` or asks to upgrade the framework.

> [!NOTE]  
> You are acting as the Framework Updater. Your job is to run the local `agentgate` installation script against the current project directory.

## Step 1: Resolve Paths
1. Identify the path to the master `agentgate` repository script: `c:\Users\vitob\Documents\Programmazione\agentgate\install.py`.
2. Identify the path to the current target project (the workspace you are currently operating in).

## Step 2: Execute Upgrade
Use your terminal tool to execute the python script in upgrade mode:
`python c:\Users\vitob\Documents\Programmazione\agentgate\install.py --upgrade [path_to_current_workspace]`

## Step 3: Verification
Capture the output of the terminal command and ensure it reports `Upgrade complete.`
Report to the user exactly how many files were updated, confirming that the framework is now synced with the latest version.
