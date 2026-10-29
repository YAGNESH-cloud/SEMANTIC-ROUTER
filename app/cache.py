
import json
import os
import time

import numpy as np
from sentence_transformers import SentenceTransformer

from app.database import get_connection


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = float(
    os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.82")
)
CACHE_TTL_SECONDS = int(
    os.getenv("CACHE_TTL_SECONDS", "3600")
)

_embedding_model = None


def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return _embedding_model


def create_embedding(text: str) -> list[float]:
    model = get_embedding_model()

    embedding = model.encode(
        text.strip(),
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return embedding.astype(np.float32).tolist()


def find_cached_answer(question: str):
    question = question.strip()

    if not question:
        return None

    now = time.time()

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM cache_entries WHERE expires_at <= ?",
            (now,)
        )

        exact_match = connection.execute(
            """
            SELECT question, answer
            FROM cache_entries
            WHERE lower(trim(question)) = lower(trim(?))
              AND expires_at > ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (question, now)
        ).fetchone()

        if exact_match:
            return {
                "answer": exact_match["answer"],
                "matched_question": exact_match["question"],
                "similarity": 1.0,
                "cache_hit": True
            }

        rows = connection.execute(
            """
            SELECT question, embedding, answer
            FROM cache_entries
            WHERE expires_at > ?
            """,
            (now,)
        ).fetchall()

    if not rows:
        return {
            "answer": None,
            "matched_question": None,
            "similarity": None,
            "cache_hit": False
        }

    query_embedding = np.asarray(
        create_embedding(question),
        dtype=np.float32
    )

    best_match = None
    best_similarity = -1.0

    for row in rows:
        try:
            stored_embedding = np.asarray(
                json.loads(row["embedding"]),
                dtype=np.float32
            )

            if stored_embedding.shape != query_embedding.shape:
                continue

            similarity = float(
                np.dot(query_embedding, stored_embedding)
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = row

        except (ValueError, TypeError, json.JSONDecodeError):
            continue

    if best_match and best_similarity >= SIMILARITY_THRESHOLD:
        return {
            "answer": best_match["answer"],
            "matched_question": best_match["question"],
            "similarity": round(best_similarity, 4),
            "cache_hit": True
        }

    return {
        "answer": None,
        "matched_question": (
            best_match["question"] if best_match else None
        ),
        "similarity": (
            round(best_similarity, 4) if best_match else None
        ),
        "cache_hit": False
    }


def save_cached_answer(question: str, answer: str):
    question = question.strip()
    answer = answer.strip()

    if not question or not answer:
        raise ValueError("Question and answer must not be empty")

    embedding = create_embedding(question)
    now = time.time()

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM cache_entries
            WHERE lower(trim(question)) = lower(trim(?))
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
