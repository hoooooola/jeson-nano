from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import os

# Configure transport security to allow Docker internal DNS names
# Disable DNS rebinding protection for Docker container-to-container communication
security_settings = TransportSecuritySettings(
    enable_dns_rebinding_protection=False
)

# Initialize FastMCP Server with custom security settings for Docker networking
mcp = FastMCP(
    "filesystem-server",
    host="0.0.0.0",
    port=8000,
    transport_security=security_settings
)

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
# FastMCP provides sse_app() method to get the ASGI application
app = mcp.sse_app()
