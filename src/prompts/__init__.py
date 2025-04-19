"""
Module for MCP prompts.
"""
from mcp.server import FastMCP


def init_prompts(mcp_server: FastMCP):
    mcp_server.prompt()(get_blockchain_info)


def get_blockchain_info(query: str):
    """
    Get detailed list of instructions on how to respond to a query about blockchain data.
    query: concise query of user with full context.
    """
    return f"""\
    \rFor this query about getting blockchain information: "{query}" make sure to do the following:
    \r - Call the right tools in sequence, \
    \rusing each tool’s output as input to the next when it adds value to the context.
    \r - Provide only information that answers the query.
    """
