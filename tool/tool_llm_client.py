""" 
File: tool_llm_client.py
Location: tool/ folder imported by all.
Owner: Shared
Function:Centralizes OpenRouter API connection. All agents and tasks import
          get_model() from here instead of setting up their own connection. """


from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

def get_model():
    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )
    return client
