import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key or api_key == "PASTE_YOUR_ACTUAL_API_KEY_HERE":
    raise SystemExit("ERROR: Check your GROQ_API_KEY in .env")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Explain semantic caching in two simple sentences."
        }
    ],
    max_tokens=150
)

print("REAL AI RESPONSE:")
print(response.choices[0].message.content)
print("MODEL:", response.model)
