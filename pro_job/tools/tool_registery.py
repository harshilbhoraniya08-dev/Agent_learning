TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_tool",
            "description": "Search for the latest news and information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "max_result": {
                        "type": "integer",
                        "description": "Maximum number of results"
                    }
                },
                "required": ["query"]
            }
        }
    }
]