
import json
import time

import numpy as np
from sentence_transformers import SentenceTransformer

from app.database import get_connection


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.75
CACHE_TTL_SECONDS = 3600

_embedding_model = None


def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return _embedding_model


def create_embedding(text: str) -> list[float]:
    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


def find_cached_answer(question: str):
    question = question.strip()

    if not question:
        return None

    query_embedding = np.array(
        create_embedding(question),
        dtype=np.float32
    )

    now = time.time()

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM cache_entries WHERE expires_at <= ?",
            (now,)
        )

        rows = connection.execute(
            """
            SELECT id, question, embedding, answer
            FROM cache_entries
            WHERE expires_at > ?
            """,
            (now,)
        ).fetchall()

    best_match = None
    best_similarity = -1.0

    for row in rows:
        stored_embedding = np.array(
            json.loads(row["embedding"]),
            dtype=np.float32
        )

        similarity = float(np.dot(query_embedding, stored_embedding))

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = row

    if best_match and best_similarity >= SIMILARITY_THRESHOLD:
        return {
            "answer": best_match["answer"],
            "matched_question": best_match["question"],
            "similarity": round(best_similarity, 4),
            "cache_hit": True
        }

    return {
        "answer": None,
        "matched_question": None,
        "similarity": round(best_similarity, 4) if best_match else None,
        "cache_hit": False
    }


def save_cached_answer(question: str, answer: str):
    question = question.strip()

    if not question or not answer.strip():
        raise ValueError("Question and answer must not be empty")

    embedding = create_embedding(question)
    now = time.time()

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM cache_entries
            WHERE question = ?
            """,
            (question,)
        )

        connection.execute(
            """
            INSERT INTO cache_entries (
                question, embedding, answer, created_at, expires_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                question,
                json.dumps(embedding),
                answer,
                now,
                now + CACHE_TTL_SECONDS
            )
        )

        connection.commit()
