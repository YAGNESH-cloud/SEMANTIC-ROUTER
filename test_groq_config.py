import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if api_key and api_key != "PASTE_YOUR_ACTUAL_API_KEY_HERE":
    print("SUCCESS: Groq API key loaded.")
else:
    print("ERROR: Groq API key is missing. Check your .env file.")
