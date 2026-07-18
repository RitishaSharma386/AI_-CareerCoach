from tool.tool_llm_client import get_model

client = get_model()

response = client.chat.completions.create(
    model="openai/gpt-oss-20b:free",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: Hello"
        }
    ]
)

print(response)
print("CONTENT:", response.choices[0].message.content)