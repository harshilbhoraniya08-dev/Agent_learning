import json

from tools.search_tools import search_tool
from model import SearchInput


AVAILABLE_TOOLS = {
    "search_tool": search_tool
}
TOOL_SCHEMAS = {
    "search_tool":SearchInput
}


async def execute_tool(tool_call):
    tool_name = tool_call.function.name

    try:
        arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        print("\nInvalid tool arguments:")
        print(tool_call.function.arguments)
        raise e

    tool = AVAILABLE_TOOLS.get(tool_name)

    if tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    schema = TOOL_SCHEMAS.get(tool_name)

    if schema :
        validated_arguments = SearchInput(**arguments)
    else:
        validated_arguments = arguments

    result = await tool(validated_arguments)

    return result