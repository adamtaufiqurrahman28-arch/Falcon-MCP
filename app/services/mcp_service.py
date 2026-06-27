import json
from typing import Any, Dict, List

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.core.config import settings


class MCPService:
    """
    Service layer untuk komunikasi dengan remote MCP Server.

    Layer ini sengaja dipisah agar:
    - API route tetap bersih
    - Transport MCP mudah diganti
    - Bisa dimock ketika unit testing
    """

    def __init__(self, server_url: str | None = None):
        self.server_url = server_url or settings.mcp_server_url

    async def list_tools(self) -> List[Dict[str, Any]]:
        async with streamable_http_client(self.server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()

                return [
                    {
                        "name": tool.name,
                        "description": tool.description or "-",
                        "input_schema": getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", None),
                    }
                    for tool in tools.tools
                ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        async with streamable_http_client(self.server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)

                return {
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": self._parse_result(result),
                }

    def _parse_result(self, result: Any) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []

        for content in result.content:
            if hasattr(content, "text"):
                text = content.text
                try:
                    parsed = json.loads(text)
                    rows.append({"type": "json", "data": parsed})
                except Exception:
                    rows.append({"type": "text", "data": text})
            else:
                rows.append({"type": "raw", "data": str(content)})

        return rows
