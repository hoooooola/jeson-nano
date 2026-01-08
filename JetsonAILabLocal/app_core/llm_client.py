import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.local_llm_url = os.getenv("LOCAL_LLM_URL", "http://local-llm:5000/v1")
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.gemini_model = None
            print("Warning: GEMINI_API_KEY not found. Cloud fallback unavailable.")

    def generate_text(self, prompt, use_local=False):
        """
        Generates text using either Local LLM or Gemini.
        """
        if use_local:
            print(f"Using Local LLM for prompt: {prompt[:20]}...")
            return self._call_local_llm(prompt)
        
        # Explicitly check for Gemini model availability
        if self.gemini_model:
            print(f"Using Gemini API for prompt: {prompt[:20]}...")
            return self._call_gemini(prompt)
        else:
            return "Error: Gemini API Key not configured and use_local=False."

    def _call_gemini(self, prompt):
        try:
            response = self.gemini_model.generate_content(prompt)
            print("Gemini response received.")
            return response.text
        except Exception as e:
            error_msg = f"Gemini API Error: {str(e)}"
            print(error_msg)
            return error_msg

    def _call_local_llm(self, prompt):
        """
        Calls the Local LLM via OpenAI-compatible API or simple text generation API.
        Adjust payload based on target Local LLM (Ollama/Text-Gen UI).
        """
        try:
            # Example payload for OpenAI-compatible endpoint
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "mode": "chat",
                "character": "Assistant"
            }
            # Note: The specific URL endpoint might vary (/v1/chat/completions or /api/v1/generate)
            # Text-Generation-WebUI usually supports /v1/chat/completions
            url = f"{self.local_llm_url}/chat/completions"
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            # Parse response (assuming OpenAI format)
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            return f"Error calling Local LLM: {str(e)}"
