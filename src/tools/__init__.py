from mcp.server import FastMCP

from .registry import tool_registry


def init_tools(mcp_server: FastMCP):
    """Initialize all tools using auto-discovery."""
    # Import all tool modules to ensure they're loaded
    from . import (
        address, blockchain, block, ens, modules, transaction,
        address_aggregates, block_aggregates, transaction_aggregates
    )
    
    # Discover and register all tools
    tool_registry.discover_tools()
    
    # Register all discovered tools with the MCP server
    tool_registry.register_all_tools(mcp_server)
