# tools/__init__.py
from tools.registry import ToolRegistry, tool_registry

# Import search after tool_registry is already defined so it registers properly
import tools.search

__all__ = ["ToolRegistry", "tool_registry"]