from flask import Flask, jsonify, request, render_template
from llm_client import LLMClient
from mcp_client_manager import MCPClientManager
import asyncio
import threading

app = Flask(__name__)
llm_client = LLMClient()
mcp_manager = MCPClientManager()

# Background thread or startup event to connect to MCP servers
def connect_mcp():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # In a real setup, loop.run_until_complete(mcp_manager.connect_to_server('mcp-fs', 'http://mcp-fs:8000/sse'))
    # For now, we simulate connection to populate tools
    loop.run_until_complete(mcp_manager.connect_to_server('mcp-fs', 'http://mcp-fs:8000/sse'))
    # loop.run_until_complete(mcp_manager.refresh_tools('mcp-fs')) # moved to connect_to_server
    print("MCP Connections initialized. Background loop running.")
    loop.run_forever()

# Start connection in background to not block Flask startup
threading.Thread(target=connect_mcp, daemon=True).start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({
        "status": "online",
        "service": "Jetson AI Lab Host",
        "gemini_configured": bool(llm_client.gemini_model),
        "tools": mcp_manager.get_available_tools()
    })

@app.route('/api/chat', methods=['POST'])
async def chat():
    data = request.json
    prompt = data.get('message', '')
    use_local = data.get('use_local', False)
    
    if not prompt:
        return jsonify({"error": "No message provided"}), 400

    # Simple 1-turn RAG/Tool use check could go here
    # For now, just direct LLM response
    response = llm_client.generate_text(prompt, use_local=use_local)
    return jsonify({"response": response})

@app.route('/api/tools', methods=['GET'])
def list_tools():
    return jsonify({"tools": mcp_manager.get_available_tools()})

@app.route('/api/tool/execute', methods=['POST'])
async def execute_tool():
    data = request.json
    tool_name = data.get('tool_name')
    args = data.get('arguments', {})
    
    if not tool_name:
         return jsonify({"error": "No tool_name provided"}), 400
         
    result = await mcp_manager.call_tool(tool_name, args)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
