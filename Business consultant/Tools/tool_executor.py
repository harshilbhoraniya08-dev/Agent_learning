import inspect
import logging
from typing import Any, Dict
from Tools.tool_registery import get_tool_function, tool_exists

logger = logging.getLogger(__name__)

async def execute_tool(tool_name:str, tool_input:Dict[str, Any])-> Any:

    if not tool_exists(tool_name):
        error_message = f"Execution Error: Tool '{tool_name}' does not exits in the system"
        logger.error(error_message)
        return {"error": error_message}
    
    try:
        func = get_tool_function(tool_name)

        if inspect.iscoroutinefunction(func):
            result = await func(**tool_input)
        else:
            result = func(**tool_input)
        
        return result
    
    except TypeError as e:
        error_msg = f"Argument Signature Error for '{tool_name}': {str(e)}. Please review the cool the tool schema"
        logger.warning(error_msg)
        return {"error":error_msg}
    
    except Exception as e:
        error_msg = f"Runtime Exception while running tool '{tool_name}': {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}