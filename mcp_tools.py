"""
MCP Tools - File Reading Tools
Direct tool implementations for use in Chainlit app
"""
import os
from pathlib import Path
from typing import Dict, Any, List


def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read (absolute or relative)

    Returns:
        The contents of the file as a string
    """
    try:
        # Convert to Path object for better handling
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return f"Error: File not found: {file_path}"

        # Check if it's actually a file (not a directory)
        if not path.is_file():
            return f"Error: Path is not a file: {file_path}"

        # Read the file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content

    except PermissionError:
        return f"Error: Permission denied to read file: {file_path}"
    except UnicodeDecodeError:
        return f"Error: File is not a text file or uses unsupported encoding: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def list_files(directory_path: str = ".") -> str:
    """
    List files in a directory.

    Args:
        directory_path: Path to the directory to list (default: current directory)

    Returns:
        A list of files and directories as a formatted string
    """
    try:
        path = Path(directory_path)

        if not path.exists():
            return f"Error: Directory not found: {directory_path}"

        if not path.is_dir():
            return f"Error: Path is not a directory: {directory_path}"

        items = []
        for item in sorted(path.iterdir()):
            item_type = "DIR" if item.is_dir() else "FILE"
            size = ""
            if item.is_file():
                try:
                    size = f" ({item.stat().st_size} bytes)"
                except:
                    pass
            items.append(f"[{item_type}] {item.name}{size}")

        return "\n".join(items) if items else "Directory is empty"

    except Exception as e:
        return f"Error listing directory: {str(e)}"


# Tool registry for easy access
TOOLS = {
    "read_file": {
        "function": read_file,
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read (absolute or relative)"
                }
            },
            "required": ["file_path"]
        }
    },
    "list_files": {
        "function": list_files,
        "description": "List files and directories in a given path",
        "parameters": {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "Path to the directory to list (default: current directory)"
                }
            },
            "required": []
        }
    }
}


def get_tools_for_llm() -> List[Dict[str, Any]]:
    """
    Get tools in OpenAI function calling format.

    Returns:
        List of tool definitions in OpenAI format
    """
    openai_tools = []

    for name, tool_def in TOOLS.items():
        openai_tool = {
            "type": "function",
            "function": {
                "name": name,
                "description": tool_def["description"],
                "parameters": tool_def["parameters"]
            }
        }
        openai_tools.append(openai_tool)

    return openai_tools


def call_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Call a tool by name with given arguments.

    Args:
        tool_name: Name of the tool to call
        arguments: Arguments to pass to the tool

    Returns:
        The result from the tool execution
    """
    if tool_name not in TOOLS:
        return f"Error: Unknown tool: {tool_name}"

    try:
        tool_function = TOOLS[tool_name]["function"]
        result = tool_function(**arguments)
        return result
    except TypeError as e:
        return f"Error: Invalid arguments for {tool_name}: {str(e)}"
    except Exception as e:
        return f"Error calling {tool_name}: {str(e)}"
