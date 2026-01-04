# Jetson AI Lab (Local LLM + MCP Architecture)

## Overview
This project implements an AI Assistant for the Jetson Nano that combines a cloud/local LLM capable "Brain" with tool-using capabilities via the Model Context Protocol (MCP).

## Architecture
- **Host**: Flask Application (`app_core`) serving as the central nervous system.
- **Brain**: 
  - **Cloud**: Google Gemini Pro (requires API Key).
  - **Local**: `dustynv/text-generation-webui` (or Ollama) running in a container.
- **Hands**: MCP Servers (starting with direct filesystem access) to perform tasks.

## Setup

1. **Prerequisites**:
   - Jetson Nano with JetPack 4.6+ (or 5.x/6.x if upgraded).
   - Docker & Docker Compose installed.

2. **Configuration**:
   - Create a `.env` file in `app_core/` or export environment variables:
     ```bash
     export GEMINI_API_KEY="your_api_key_here"
     ```

3. **Running the Stack**:
   ```bash
   cd JetsonAILabLocal
   docker-compose up --build
   ```

4. **Usage**:
   - Access the Web UI at `http://[JETSON_IP]:5000`.
   - Interact with the chat bot.
   - Use the "Force Local" toggle to disconnect from Cloud API and use the local LLM.

## Directory Structure
- `app_core/`: Python Flask host code.
- `app_data/`: Persistent data for the app.
- `models/`: Storage for Local LLM models (mapped to container).
- `docker-compose.yml`: Service orchestration.

## Notes
- Ensure your Jetson Nano is in 10W mode (`sudo nvpmodel -m 0`) for best performance with local models.
- Local LLM startup can take several minutes.
