TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_tool",
            "description": """Search for the External information. 
            Use this tool when you need:
            - latest news
            - latest events
            - current information
            - facts that may required external sources

            Do not use this tool for general reasoning or information already available""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to find information"
                    },
                    "max_result": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default":5
                    }
                },
                "required": ["query"],
                "additionalProperties":False
            }
        }
    }
]