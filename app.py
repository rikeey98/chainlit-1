"""
Chainlit App with MCP Integration
Main application that provides chat UI and integrates with MCP server
"""
import os
import json
from typing import List, Dict, Any
import chainlit as cl
from openai import AsyncOpenAI
from dotenv import load_dotenv
from mcp_client import MCPClient

# Load environment variables
load_dotenv()

# Initialize OpenAI client (compatible with any OpenAI-compatible API)
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

# Initialize MCP client
mcp_client = MCPClient(
    base_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000")
)

# Model settings
MODEL = os.getenv("MODEL_NAME", "gpt-4")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))


@cl.on_chat_start
async def start():
    """Initialize chat session"""
    await cl.Message(
        content="👋 안녕하세요! MCP 파일 에이전트입니다.\n\n"
                "파일을 읽어야 하는 질문을 해주세요. 예를 들어:\n"
                "- 'README.md 파일의 내용을 읽어줘'\n"
                "- '현재 디렉토리의 파일 목록을 보여줘'\n"
                "- 'pyproject.toml에 어떤 의존성이 있어?'"
    ).send()

    # Store message history in session
    cl.user_session.set("message_history", [])

    # Get available tools from MCP server
    tools = mcp_client.get_tools_for_llm()
    cl.user_session.set("tools", tools)

    # Display available tools
    tool_names = [tool["function"]["name"] for tool in tools]
    await cl.Message(
        content=f"🔧 사용 가능한 도구: {', '.join(tool_names) if tool_names else '없음'}"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""

    # Get message history and tools
    message_history: List[Dict] = cl.user_session.get("message_history", [])
    tools = cl.user_session.get("tools", [])

    # Add user message to history
    message_history.append({
        "role": "user",
        "content": message.content
    })

    # Create message for streaming response
    msg = cl.Message(content="")
    await msg.send()

    # Call LLM with tools
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=message_history,
            tools=tools if tools else None,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=True
        )

        function_name = None
        function_args = ""
        content = ""

        async for chunk in response:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # Handle content streaming
            if delta.content:
                content += delta.content
                await msg.stream_token(delta.content)

            # Handle tool calls
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    if tool_call.function.name:
                        function_name = tool_call.function.name
                    if tool_call.function.arguments:
                        function_args += tool_call.function.arguments

        # If there was a tool call, execute it
        if function_name:
            await msg.update()

            # Parse arguments
            try:
                arguments = json.loads(function_args)
            except json.JSONDecodeError:
                arguments = {}

            # Show tool call to user
            await cl.Message(
                content=f"🔧 도구 호출: `{function_name}`\n인자: `{json.dumps(arguments, ensure_ascii=False)}`"
            ).send()

            # Call the MCP tool
            tool_result = mcp_client.call_tool(function_name, arguments)

            # Show tool result
            result_msg = cl.Message(content="")
            await result_msg.send()

            # Add tool call and result to message history
            message_history.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "arguments": json.dumps(arguments)
                    }
                }]
            })

            message_history.append({
                "role": "tool",
                "tool_call_id": "call_1",
                "content": tool_result
            })

            # Get final response from LLM with tool result
            final_response = await client.chat.completions.create(
                model=MODEL,
                messages=message_history,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                stream=True
            )

            final_content = ""
            async for chunk in final_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    final_content += token
                    await result_msg.stream_token(token)

            # Add final response to history
            message_history.append({
                "role": "assistant",
                "content": final_content
            })

            await result_msg.update()

        else:
            # No tool call, just add assistant response to history
            message_history.append({
                "role": "assistant",
                "content": content
            })
            await msg.update()

        # Update message history in session
        cl.user_session.set("message_history", message_history)

    except Exception as e:
        error_msg = f"❌ 오류가 발생했습니다: {str(e)}"
        await cl.Message(content=error_msg).send()
        print(f"Error: {e}")


if __name__ == "__main__":
    # This is for development purposes
    # In production, use: chainlit run app.py
    pass
