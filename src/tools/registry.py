"""
Tool registry system for automatic tool discovery and registration.
"""
import importlib
import inspect
import pkgutil
import logging
from typing import Callable, Dict, List
from pathlib import Path

from mcp.server import FastMCP

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for automatically discovering and registering MCP tools."""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
    
    def register_tool(self, func: Callable) -> Callable:
        """Decorator to register a tool function."""
        tool_name = func.__name__
        if tool_name in self._tools:
            logger.warning(f"Tool '{tool_name}' is being overridden")
        self._tools[tool_name] = func
        logger.debug(f"Registered tool: {tool_name}")
        return func
    
    def get_tools(self) -> Dict[str, Callable]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def register_all_tools(self, mcp_server: FastMCP) -> None:
        """Register all discovered tools with the MCP server."""
        registered_count = 0
        for tool_name, tool_func in self._tools.items():
            try:
                mcp_server.tool()(tool_func)
                registered_count += 1
                logger.debug(f"Registered tool with MCP server: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to register tool '{tool_name}': {e}")
                raise
        
        logger.info(f"Successfully registered {registered_count} tools with MCP server")
    
    def discover_tools(self, package_name: str = "src.tools") -> None:
        """Automatically discover and import tools from the tools package."""
        discovered_count = 0
        try:
            # Import the package to get its path
            package = importlib.import_module(package_name)
            if not hasattr(package, '__path__'):
                logger.warning(f"Package '{package_name}' has no __path__ attribute")
                return
            
            # Walk through all modules in the package
            for finder, name, ispkg in pkgutil.iter_modules(package.__path__):
                if name in ['registry', '__all__']:  # Skip self and metadata
                    continue
                
                try:
                    # Import the module
                    full_module_name = f"{package_name}.{name}"
                    module = importlib.import_module(full_module_name)
                    logger.debug(f"Imported module: {full_module_name}")
                    
                    # Find functions marked as tools
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (inspect.isfunction(attr) and 
                            hasattr(attr, '_is_mcp_tool') and 
                            attr._is_mcp_tool):
                            if attr.__name__ not in self._tools:
                                self._tools[attr.__name__] = attr
                                discovered_count += 1
                                logger.debug(f"Discovered tool: {attr.__name__}")
                            
                except ImportError as e:
                    logger.warning(f"Could not import {full_module_name}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing module {full_module_name}: {e}")
                    continue
        
        except ImportError as e:
            logger.error(f"Could not import package {package_name}: {e}")
            raise
        
        logger.info(f"Discovered {discovered_count} tools from {package_name}")


# Global registry instance
tool_registry = ToolRegistry()


def mcp_tool(func: Callable) -> Callable:
    """Decorator to mark a function as an MCP tool and register it."""
    func._is_mcp_tool = True
    tool_registry.register_tool(func)
    return func