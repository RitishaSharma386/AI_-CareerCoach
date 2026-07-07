""" 
File: tool_gemini_client.py
Location: tool/ folder imported by all 
Owner: Shared
Function:Centralizes Gemini API connection. All agents and tasks import
          get_model() from here instead of setting up their own connection. """

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def get_model():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel("gemini-2.0-flash-lite")

