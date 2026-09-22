import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

response = client.chat.completions.create(
    model="openai/gpt-5-mini",
    messages=[{"role": "user", "content": "What is a large language model?"}],
)

print(response.choices[0].message.content)
