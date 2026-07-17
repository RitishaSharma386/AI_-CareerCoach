"""
File: tests/debug_empty_response.py
Owner: Member 4 — Shraddha Tyagi
Function: Diagnostic script — inspects the FULL response object on repeated
          calls to understand why empty responses occur.
"""
from tool.tool_llm_client import get_model

client = get_model()

for i in range(1, 6):
    print(f"\n{'='*60}\nCALL {i}\n{'='*60}")
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        temperature=0,
        messages=[{"role": "user", "content": "Say hello in 5 words."}]
    )
    print("Finish reason:", response.choices[0].finish_reason)
    print("Content:", repr(response.choices[0].message.content))
    print("Full response object:", response)