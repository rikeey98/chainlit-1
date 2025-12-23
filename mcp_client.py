"""
MCP SSE Client
Connects to the MCP server via SSE and provides methods to call tools
"""
import json
import httpx
from httpx_sse import connect_sse
from typing import Dict, Any, List


class MCPClient:
    """Client for communicating with MCP server via SSE"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the MCP client.

        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url
        self.sse_url = f"{base_url}/sse"
        self.tools_cache = None

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools from the MCP server.

        Returns:
            List of tool definitions
        """
        if self.tools_cache:
            return self.tools_cache

        try:
            # Request to list tools
            request_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }

            with httpx.Client() as client:
                with connect_sse(
                    client,
                    "POST",
                    self.sse_url,
                    json=request_data,
                    timeout=10.0
                ) as event_source:
                    for sse in event_source.iter_sse():
                        if sse.data:
                            response = json.loads(sse.data)
                            if "result" in response:
                                tools = response["result"].get("tools", [])
                                self.tools_cache = tools
                                return tools

        except Exception as e:
            print(f"Error getting tools from MCP server: {e}")
            return []

        return []

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            The result from the tool execution
        """
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            with httpx.Client() as client:
                with connect_sse(
                    client,
                    "POST",
                    self.sse_url,
                    json=request_data,
                    timeout=30.0
                ) as event_source:
                    for sse in event_source.iter_sse():
                        if sse.data:
                            response = json.loads(sse.data)
                            if "result" in response:
                                # Extract the content from the result
                                content = response["result"].get("content", [])
                                if content and len(content) > 0:
                                    return content[0].get("text", "")

        except httpx.TimeoutException:
            return "Error: Request to MCP server timed out"
        except Exception as e:
            return f"Error calling tool: {str(e)}"

        return "No response from MCP server"

    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        Get tools in OpenAI function calling format.

        Returns:
            List of tool definitions in OpenAI format
        """
        mcp_tools = self.get_tools()
        openai_tools = []

        for tool in mcp_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                }
            }
            openai_tools.append(openai_tool)

        return openai_tools


def test_client():
    """Test function to verify MCP client connectivity"""
    client = MCPClient()
    print("Testing MCP Client...")

    # Get available tools
    tools = client.get_tools()
    print(f"Available tools: {[t['name'] for t in tools]}")

    # Test read_file tool
    if tools:
        result = client.call_tool("read_file", {"file_path": "README.md"})
        print(f"Test result: {result[:100]}...")


if __name__ == "__main__":
    test_client()
