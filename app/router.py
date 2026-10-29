
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing from your .env file")

client = Groq(api_key=API_KEY)

SMALL_MODEL = "openai/gpt-oss-20b"
LARGE_MODEL = "openai/gpt-oss-120b"


def choose_model(question: str) -> str:
    question_lower = question.lower()

    complex_keywords = [
        "compare", "advantages", "disadvantages", "architecture",
        "detailed", "explain", "examples", "use cases",
        "difference", "differences", "analyze", "analysis",
        "step by step"
    ]

    if len(question.split()) > 12 or any(
        keyword in question_lower for keyword in complex_keywords
    ):
        return LARGE_MODEL

    return SMALL_MODEL


def generate_answer(question: str, model_name: str) -> dict:
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful technical assistant. Answer the entire "
                    "question accurately. Include requested examples, advantages, "
                    "disadvantages, and use cases. Use clear headings and concise "
                    "explanations. Complete your answer and conclusion before stopping."
                ),
            },
            {"role": "user", "content": question},
        ],
        max_tokens=6900,
    )

    choice = response.choices[0]

    return {
        "answer": choice.message.content or "",
        "model_name": model_name,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "finish_reason": choice.finish_reason,
    }
