from app.database import initialize_database, get_connection
from app.cache import find_cached_answer, save_cached_answer

initialize_database()


def remove_test_question(question):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM cache_entries WHERE question = ?",
            (question,)
        )


def test_exact_question_cache_hit():
    question = "Unique automated test question 1042"
    answer = "Answer for automated test 1042."

    remove_test_question(question)
    save_cached_answer(question, answer)

    result = find_cached_answer(question)

    assert result["cache_hit"] is True
    assert result["answer"] == answer
    assert result["similarity"] == 1.0


def test_new_question_cache_miss():
    question = "Unique ocean current test question 92751"

    result = find_cached_answer(question)

    assert result["cache_hit"] is False
    assert result["answer"] is None


def test_paraphrased_question_cache_behavior():
    question = "Unique semantic cache cost test 63821"
    answer = "Test answer for semantic cache cost 63821."

    remove_test_question(question)
    save_cached_answer(question, answer)

    result = find_cached_answer(question)

    assert result["cache_hit"] is True
    assert result["answer"] == answer