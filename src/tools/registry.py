"""
Tool registry system for automatic tool discovery and registration.
"""
import importlib
import inspect
import pkgutil
from typing import Callable, Dict, List
from pathlib import Path

from mcp.server import FastMCP


class ToolRegistry:
    """Registry for automatically discovering and registering MCP tools."""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
    
    def register_tool(self, func: Callable) -> Callable:
        """Decorator to register a tool function."""
        self._tools[func.__name__] = func
        return func
    
    def get_tools(self) -> Dict[str, Callable]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def register_all_tools(self, mcp_server: FastMCP) -> None:
        """Register all discovered tools with the MCP server."""
        for tool_name, tool_func in self._tools.items():
            mcp_server.tool()(tool_func)
    
    def discover_tools(self, package_name: str = "src.tools") -> None:
        """Automatically discover and import tools from the tools package."""
        try:
            # Import the package to get its path
            package = importlib.import_module(package_name)
            if not hasattr(package, '__path__'):
                return
            
            # Walk through all modules in the package
            for finder, name, ispkg in pkgutil.iter_modules(package.__path__):
                if name == 'registry':  # Skip self
                    continue
                
                try:
                    # Import the module
                    full_module_name = f"{package_name}.{name}"
                    module = importlib.import_module(full_module_name)
                    
                    # Find functions marked as tools
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (inspect.isfunction(attr) and 
                            hasattr(attr, '_is_mcp_tool') and 
                            attr._is_mcp_tool):
                            self._tools[attr.__name__] = attr
                            
                except ImportError as e:
                    print(f"Warning: Could not import {full_module_name}: {e}")
                    continue
        
        except ImportError as e:
            print(f"Warning: Could not import package {package_name}: {e}")


# Global registry instance
tool_registry = ToolRegistry()


def mcp_tool(func: Callable) -> Callable:
    """Decorator to mark a function as an MCP tool and register it."""
    func._is_mcp_tool = True
    tool_registry.register_tool(func)
    return func