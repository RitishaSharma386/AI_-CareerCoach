from tool.tool_llm_client import get_model

client = get_model()

response = client.chat.completions.create(
    model="openrouter/free",
    messages=[{"role": "user", "content": "Say hello in 5 words."}]
)

print(response.choices[0].message.content)

