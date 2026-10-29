
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
        "step by step", "why", "how does", "how do"
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
                    "You are a knowledgeable, clear, and helpful AI assistant. "
                    "Answer the user's actual question directly. "
                    "Do not ask for clarification unless the question is genuinely "
                    "ambiguous or missing essential information. "
                    "Do not invent context or assume the user means something "
                    "they did not mention. "
                    "For a clear question, start with the direct answer, then "
                    "explain it in simple language. "
                    "For technical questions, include a relevant example when useful. "
                    "Use headings and lists when they improve readability. "
                    "If the question is unclear, ask one short, specific "
                    "clarification question. "
                    "Keep simple questions concise and provide more detail for "
                    "complex questions. Finish the answer properly."
                ),
            },
            {
                "role": "user",
                "content": question.strip(),
            },
        ],
        max_tokens=2048,
        temperature=0.3,
    )

    choice = response.choices[0]
    answer = (choice.message.content or "").strip()

    if not answer:
        raise RuntimeError(
            f"The AI model returned an empty answer. "
            f"Finish reason: {choice.finish_reason}"
        )

    usage = response.usage

    return {
        "answer": answer,
        "model_name": model_name,
        "input_tokens": usage.prompt_tokens if usage else 0,
        "output_tokens": usage.completion_tokens if usage else 0,
        "finish_reason": choice.finish_reason,
    }
