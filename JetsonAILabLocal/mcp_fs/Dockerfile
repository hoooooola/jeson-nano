FROM python:3.10-slim

WORKDIR /app

# Install MCP SDK
RUN pip install "mcp[cli]" uvicorn

COPY server.py .

# Expose port for SSE
EXPOSE 8000

# Run the server using FastMCP's inspector to serve via SSE/HTTP
# Note: In a real prod environment we might use 'uvicorn server:app' if FastMCP exposes an ASGI app
CMD ["uvicorn", "server:mcp", "--host", "0.0.0.0", "--port", "8000"]
