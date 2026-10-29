
import time
import traceback

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.cache import find_cached_answer, save_cached_answer
from app.database import initialize_database, record_request, get_metrics
from app.router import choose_model, generate_answer

app = FastAPI(
    title="Semantic Cache and Cost-Aware Router",
    description="Real AI with semantic caching and request metrics.",
    version="1.3.0"
)

initialize_database()

MODEL_PRICES = {
    "openai/gpt-oss-20b": {"input": 0.075, "output": 0.30},
    "openai/gpt-oss-120b": {"input": 0.15, "output": 0.60}
}


def calculate_cost_usd(model_name, input_tokens, output_tokens):
    prices = MODEL_PRICES.get(model_name)

    if prices is None:
        raise ValueError(f"Pricing is not configured for model: {model_name}")

    input_cost = input_tokens * prices["input"] / 1_000_000
    output_cost = output_tokens * prices["output"] / 1_000_000

    return round(input_cost + output_cost, 10)


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)


class AnswerResponse(BaseModel):
    question: str
    answer: str
    cache_hit: bool
    similarity: float | None
    model_name: str
    latency_ms: float
    status: str
    finish_reason: str | None = None


@app.get("/")
def home():
    return {
        "message": "Semantic Router API is running",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metrics")
def metrics():
    records = get_metrics()
    total_requests = len(records)
    cache_hits = sum(1 for record in records if record["cache_hit"] == 1)
    total_cost = sum(record["cost_usd"] for record in records)

    average_latency = (
        sum(record["latency_ms"] for record in records) / total_requests
        if total_requests else 0
    )

    return {
        "total_requests": total_requests,
        "cache_hits": cache_hits,
        "cache_misses": total_requests - cache_hits,
        "cache_hit_rate_percent": round(cache_hits / total_requests * 100, 2)
        if total_requests else 0,
        "total_cost_usd": round(total_cost, 10),
        "average_latency_ms": round(average_latency, 2),
        "requests": records
    }


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    start_time = time.perf_counter()
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        cached = find_cached_answer(question)

        if cached and cached["cache_hit"]:
            answer = cached["answer"]
            cache_hit = True
            similarity = cached["similarity"]
            model_name = "semantic-cache"
            input_tokens = 0
            output_tokens = 0
            cost_usd = 0.0
            finish_reason = None

        else:
            selected_model = choose_model(question)
            result = generate_answer(question, selected_model)

            answer = result["answer"]
            model_name = result["model_name"]
            input_tokens = result["input_tokens"]
            output_tokens = result["output_tokens"]
            finish_reason = result.get("finish_reason")

            if not answer or not answer.strip():
                raise RuntimeError("The AI returned an empty answer")

            cache_hit = False
            similarity = cached["similarity"] if cached else None

            cost_usd = calculate_cost_usd(
                model_name, input_tokens, output_tokens
            )

            save_cached_answer(question, answer)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        record_request(
            question=question,
            cache_hit=cache_hit,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            status="success"
        )

        return AnswerResponse(
            question=question,
            answer=answer,
            cache_hit=cache_hit,
            similarity=similarity,
            model_name=model_name,
            latency_ms=latency_ms,
            status="success",
            finish_reason=finish_reason
        )

    except HTTPException:
        raise

    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Request processing failed: {type(exc).__name__}: {exc}"
        ) from exc
