import inspect
from typing import Dict,Callable,Any,List,get_type_hints,Optional


# Mapping the python type to json

TYPE_MAP: Dict[type,str] = {
    str:"string",
    int:"integer",
    dict:"object",
    bool:"boolean",
    float:"number",
    list:"array"
}


def function_to_json_schema(func: Callable) -> Dict[str, Any]:
    """Inspect the python function to automatically generate the appropriate """

    sig = inspect.signature(func)
    type_hint = get_type_hints(func)
    doc = inspect.getdoc(func) or "No description provided."

    properties: Dict[str, Any] = {}
    required: List[str] = []

    for param_name, param in sig.parameters.items():
        param_type = type_hint.get(param_name, str)
        json_type = TYPE_MAP.get(param_type, "string")

        properties[param_name] = {
            "type": json_type,
            "description":f"Parameter: {param_name}"
        }

        #If a parameter has no default value it is required
        if param.default is inspect.Parameter.empty:
            required.append(param_name)
    return {
        "type":"function",
        "function": {
            "name": func.__name__,
            "description":doc,
            "parameters":{
                "type":"object",
                "properties":properties,
                "required": required,
            },
        },
    }

class ToolRegistry:

    """Central catalog for registering , exporting schemas and running agent tools"""
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}

    def register(self, func:Callable) -> Callable:
        "Decorator to rgister a python fucntion into the registery"
        name = func.__name__
        self._tools[name] = func
        self._schemas[name] = function_to_json_schema(func)
        return func

    def get_schemas(self, tool_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Returns JSON schemas for all registered tools or a filtered list."""
        if tool_names is None:
            return list(self._schemas.values())
        return [self._schemas[name] for name in tool_names if name in self._schemas]

    def execute(self, tool_name:str, **kwargs) -> Any:
        """
        Execute a registed tool by name
        catch and store run time error for self improvments for agent.
        """

        if tool_name not in self._tools:
            return f"Error : tool '{tool_name}' is not registered"

        try:
            return self._tools[tool_name](**kwargs)
        except Exception as e:
                return f"Error executing tool '{tool_name}':{str(e)}"


tool_registry = ToolRegistry()