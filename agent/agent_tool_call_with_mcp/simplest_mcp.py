from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
def add(a: int, b: int):
    return a + b

if __name__ == "__main__":
    mcp.run()
    

import asyncio
from fastmcp import Client
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

async def main():

    client = Client("server.py")

    async with client:
        tools = await load_mcp_tools(client)

        model = ChatOpenAI(model="gpt-4o-mini")

        agent = create_agent(model, tools)

        response = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": "Add 10 and 20"}
            ]
        })

        print(response["messages"][-1].content)

asyncio.run(main())