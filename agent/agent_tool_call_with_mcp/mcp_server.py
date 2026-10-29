# pip install mcp

from mcp.server.fastmcp import FastMCP
mcp = FastMCP('support tools')
@mcp.tool()
def get_support_hours()->str:
    return "support avialable on monday 9 am to 5 pm"
if __name__ == '__main__':
    mcp.run(transport='stdio')