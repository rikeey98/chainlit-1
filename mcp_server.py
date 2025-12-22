#!/usr/bin/env python3
"""
MCP Server with File Reading Tool
Exposes file reading functionality via FastMCP SSE
"""
import os
from pathlib import Path
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("File Reader MCP Server")


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read (absolute or relative)

    Returns:
        The contents of the file as a string

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read
    """
    try:
        # Convert to Path object for better handling
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check if it's actually a file (not a directory)
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Read the file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content

    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except PermissionError:
        return f"Error: Permission denied to read file: {file_path}"
    except UnicodeDecodeError:
        return f"Error: File is not a text file or uses unsupported encoding: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
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
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")

        items = []
        for item in sorted(path.iterdir()):
            item_type = "DIR" if item.is_dir() else "FILE"
            items.append(f"[{item_type}] {item.name}")

        return "\n".join(items) if items else "Directory is empty"

    except Exception as e:
        return f"Error listing directory: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server with SSE transport
    # The server will be available at http://localhost:8000/sse
    mcp.run(transport="sse")
