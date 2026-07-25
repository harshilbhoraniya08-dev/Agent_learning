import json

from tools.search_tools import search_tool
from model import SearchInput


AVAILABEL_TOOLS = {
    "search_tool": search_tool
}

async def execute_tool(tool_call):
    tool_name = tool_call.function.name

    arguments = json.loads(
        tool_call.function.arguments
    )

    tool = AVAILABEL_TOOLS.get(tool_name)

    if tool_name is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    Validated_arguments = SearchInput(**arguments)

    result = await tool(Validated_arguments)

    return result