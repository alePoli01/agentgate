TOOL_GRAPH = {
    "FILE_TOOLS": {
        "description": "Tools for reading and writing files",
        "tools": {
            "read_file": {"params": ["filepath"]},
            "write_file": {"params": ["filepath", "content"]},
            "semantic_search": {"params": ["query"]}
        }
    },
    "WEB_TOOLS": {
        "description": "Tools for searching the internet and extracting web pages",
        "tools": {
            "search_web": {"params": ["query"]},
            "read_url": {"params": ["url"]}
        }
    },
    "SYSTEM_TOOLS": {
        "description": "Tools for running terminal commands",
        "tools": {
            "run_command": {"params": ["command"]}
        }
    }
}
