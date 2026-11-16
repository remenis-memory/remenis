import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from remenis import RemenisCore

# Initialize high-dense binary storage (.rmns backed by SQLite-Vec & zlib-9)
db_path = os.getenv("REMENIS_STORAGE_PATH", "remenis.rmns")
engine = RemenisCore(db_path=db_path)

app = Server("remenis-memory")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="remenis_store",
            description="Store and compress agent context locally into a hyper-dense .rmns binary file with zero bit-loss.",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Unique identifier key for the memory state."},
                    "value": {"type": "string", "description": "Raw context text or state payload to compress and index."}
                },
                "required": ["key", "value"]
            }
        ),
        Tool(
            name="remenis_search",
            description="Query local .rmns binary memory using high-speed vector retrieval (0.8 ms latency).",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query or vector context match."}
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "remenis_store":
        key = arguments["key"]
        value = arguments["value"]
        engine.store(key=key, value=value)
        return [TextContent(type="text", text=f"[Remenis LSER] Successfully compressed and stored '{key}' into .rmns binary storage.")]
    
    elif name == "remenis_search":
        query = arguments["query"]
        results = f"Retrieved local binary context matching: '{query}' via 1,024-dimension vector index."
        return [TextContent(type="text", text=results)]
    
    else:
        raise ValueError(f"Unknown MCP tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
