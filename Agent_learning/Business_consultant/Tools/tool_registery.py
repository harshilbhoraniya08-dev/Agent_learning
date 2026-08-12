from typing import Callable, Dict,List

#=============
# Regiestry storage
# ============

TOOL_SCHEMAS: List[dict] = []
TOOL_FUNCTIONS: Dict[str, Callable] = {}


# ===========
# Register Tool
# ===========

def register_tool(schema: dict, function: Callable):
    tool_name= schema['function']['name']
    if tool_name in TOOL_FUNCTIONS:
        raise ValueError(f"Tool '{tool_name}' already exists")
    TOOL_SCHEMAS.append(schema)
    TOOL_FUNCTIONS[tool_name] = function

#===============
# Get all Tool Schemas
# ==============
    
def get_tool_schemas() -> List[dict]:

    return TOOL_SCHEMAS

#===============
# Get tool Function
#===============

def get_tool_function(tool_name:str):
    """
    Return the python function for a tool
    """

    if tool_name not in TOOL_FUNCTIONS:
        raise ValueError(f"Tool '{tool_name}' not found.")
    return TOOL_FUNCTIONS[tool_name]

#==============
# Check tool
#==============

def tool_exists(tool_name:str)->bool:
    return tool_name in TOOL_FUNCTIONS


#=============
# List Registered Tools
#=============

def list_tools()->List[str]:
    """
    Return Registered tool names.
    """
    return list(TOOL_FUNCTIONS.keys())