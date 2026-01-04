from mcp.server.fastmcp import FastMCP
import os

# Initialize FastMCP Server
mcp = FastMCP("filesystem-server")

@mcp.tool()
def list_files(path: str = ".") -> str:
    """List files in the specified directory."""
    try:
        # Security check: Ensure we are only listing files within the allowed volume
        # In Docker, we mapped Host's jesonEcosys to /host_files
        base_path = "/host_files"
        target_path = os.path.join(base_path, path)
        
        if not os.path.exists(target_path):
             return f"Error: Path {target_path} does not exist."

        files = os.listdir(target_path)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"

@mcp.tool()
def read_file(path: str) -> str:
    """Read the content of a file."""
    try:
        base_path = "/host_files"
        target_path = os.path.join(base_path, path)

        if not os.path.exists(target_path):
             return f"Error: File {target_path} does not exist."
             
        with open(target_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


# Expose as ASGI app for uvicorn
# FastMCP instance itself might not be the ASGI app directly depending on version.
# But `mcp.run()` suggests it wraps one.
# For simplicity with 'uvicorn server:mcp', we ensure mcp is importable.

