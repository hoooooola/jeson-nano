import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.types import CallToolResult, ListToolsResult

class MCPClientManager:
    def __init__(self):
        self.servers = {} # {name: session}
        self.exit_stack = AsyncExitStack()
        self.tools = {}   # {tool_name: (server_name, tool_metadata)}
        self.loop = None  # Capture the loop where connections are made

    async def connect_to_server(self, name, url):
        """
        Connects to an MCP Server via SSE (HTTP).
        """
        self.loop = asyncio.get_running_loop()
        try:
            print(f"Connecting to MCP Server {name} at {url}...")
            # Use AsyncExitStack to manage the connection context persistently
            streams = await self.exit_stack.enter_async_context(sse_client(url))
            session = await self.exit_stack.enter_async_context(ClientSession(streams[0], streams[1]))
            
            await session.initialize()
            self.servers[name] = session
            print(f"Connected to {name}")
            
            # Auto-refresh tools upon successful connection
            await self.refresh_tools(name)
            return True
        except Exception as e:
            print(f"Failed to connect to {name}: {e}")
            return False

    async def refresh_tools(self, server_name):
        """
        Fetches available tools from the server.
        """
        session = self.servers.get(server_name)
        if not session:
            print(f"Server {server_name} not connected.")
            return
        
        try:
            result: ListToolsResult = await session.list_tools()
            for tool in result.tools:
                self.tools[tool.name] = (server_name, tool)
            print(f"Refreshed tools for {server_name}: {[t.name for t in result.tools]}")
        except Exception as e:
            print(f"Error listing tools for {server_name}: {e}")

    async def call_tool(self, tool_name, arguments):
        """
        Executes a tool on the appropriate server. Handles cross-thread loop execution.
        """
        # Check if we need to bridge to the background loop
        if self.loop and self.loop != asyncio.get_running_loop():
            future = asyncio.run_coroutine_threadsafe(
                self._call_tool_impl(tool_name, arguments), self.loop
            )
            return await asyncio.wrap_future(future)
            
        return await self._call_tool_impl(tool_name, arguments)

    async def _call_tool_impl(self, tool_name, arguments):
        if tool_name not in self.tools:
            return f"Error: Tool {tool_name} not found."
            
        server_name, _ = self.tools[tool_name]
        session = self.servers.get(server_name)
        
        if not session:
             return f"Error: Server {server_name} disconnected."

        try:
            result: CallToolResult = await session.call_tool(tool_name, arguments)
            
            # Combine content from result
            output = []
            for content in result.content:
                if content.type == 'text':
                    output.append(content.text)
                # Handle other types (image, resource) if needed in future
            return "\n".join(output)
        except Exception as e:
            return f"Tool execution error: {e}"

    def get_available_tools(self):
        # Helper to format tool list for frontend/LLM
        return [{"name": k, "description": v[1].description if hasattr(v[1], 'description') else "No description"} for k, v in self.tools.items()]

    async def cleanup(self):
        """
        Closes all connections.
        """
        await self.exit_stack.aclose()
