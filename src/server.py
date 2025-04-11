from mcp.server import FastMCP

import prompts  # noqa
import resources  # noqa
import tools  # noqa

server = FastMCP("3xpl_API")


# server tools and stuff declarations

@server.tool()
def stuff():
    return 1
