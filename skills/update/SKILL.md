---
name: "update"
description: "The Framework Update Workflow. Automatically updates the current project's framework files by downloading the latest release from GitHub."
environment_target: "universal"
priority: 2
---
# The Update Workflow

**Trigger**: The user explicitly types `/update` or asks to update the framework.

> [!NOTE]  
> You are acting as the Framework Updater. Your job is to fetch the latest AgentGate installation script directly from GitHub and run it against the current project directory. This ensures the project remains independent from any local framework source folders.

## Step 1: Execute Remote Update
Use your terminal tool to download and execute the python script in update mode. Run these commands sequentially in the current project root:

For Windows/PowerShell:
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/alePoli01/agentgate/main/install.py" -OutFile "install.py"
python install.py --update .
Remove-Item install.py
```

For Mac/Linux:
```bash
curl -O https://raw.githubusercontent.com/alePoli01/agentgate/main/install.py
python3 install.py --update .
rm install.py
```

## Step 2: Verification
Capture the output of the terminal command and ensure it reports `Update complete.`
Report to the user exactly how many files were updated, confirming that the framework is now synced with the latest version from GitHub.
