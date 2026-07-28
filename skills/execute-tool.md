---
type: "skill"
name: "execute-tool"
description: "Workflow for executing tools using Decoupled Tool Calling and SEARL Tool Graph"
environment_target: "local"
---
# Decoupled Tool Execution

> [!WARNING]
> Local LLMs MUST NOT attempt to format direct JSON payloads to execute orchestrator-mediated tools (file writes, command runs). You will hallucinate and break the execution chain. You MUST use the `orchestrator.py` pipeline for these.
> *(Note: Platform-native tools provided by the IDE host, like `view_file` or `read_file`, can be used directly without the orchestrator).*

## Step 1: SEARL Graph Query
If you do not know the exact name of the tool you need, query the Tool Graph Categories first:
```bash
python .ai/src/orchestrator.py --query-graph FILE_TOOLS
```
Valid categories: `FILE_TOOLS`, `WEB_TOOLS`, `SYSTEM_TOOLS`.

## Step 2: Parameter Submission
Once you know the tool and its required parameters, pass them as sequential text strings to the orchestrator.
```bash
python .ai/src/orchestrator.py --tool read_file --params "/path/to/file.py"
```

The Python orchestrator will safely compile this into JSON and send it to the external API, protecting you from syntax errors.
