import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("LLM_API_KEY", "").strip()
base_url = os.getenv("LLM_BASE_URL", "").strip()
model = os.getenv("LLM_MODEL", "openai/gpt-5.2").strip()

print("KEY ADA:", bool(api_key))
print("KEY PREFIX:", api_key[:10])
print("KEY SUFFIX:", api_key[-6:])
print("BASE URL:", base_url)
print("MODEL:", model)

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": "Balas singkat: koneksi berhasil."}
    ],
)

print(response.choices[0].message.content)