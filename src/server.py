from mcp.server import FastMCP

from src.prompts import init_prompts
from src.tools import init_tools

server = FastMCP("3xpl_API")
init_tools(server)
init_prompts(server)
