FROM python:3.10-slim

WORKDIR /app

# Install MCP SDK and uvicorn
RUN pip install "mcp[cli]" uvicorn

# Set environment variable to disable MCP host validation for Docker networking
ENV MCP_SKIP_HOST_CHECK=1
ENV FASTMCP_SKIP_HOST_CHECK=1

COPY server.py .

# Expose port for SSE
EXPOSE 8000

# Run the server using uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
