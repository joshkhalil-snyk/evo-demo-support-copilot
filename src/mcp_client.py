"""Pulls extra capabilities in from the internal MCP toolbox server."""

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

TOOLBOX = StdioServerParameters(
    command="node",
    args=["../evo-demo-mcp-toolbox/dist/server.js"],
    env=None,
)


async def list_remote_tools() -> list[str]:
    async with stdio_client(TOOLBOX) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return [t.name for t in tools.tools]


async def call_remote_tool(name: str, arguments: dict):
    async with stdio_client(TOOLBOX) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool(name, arguments=arguments)


if __name__ == "__main__":
    print(asyncio.run(list_remote_tools()))
