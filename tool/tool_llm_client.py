""" 
File: tool_llm_client.py
Location: tool/ folder imported by all 
Owner: Shared
Function:Centralizes Gemini API connection. All agents and tasks import
          get_model() from here instead of setting up their own connection. """

import openai as openai
import os
from dotenv import load_dotenv

load_dotenv()

def get_model():
    openai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return openai.GenerativeModel("gemini-2.0-flash-lite")

