
from app.cache import find_cached_answer, save_cached_answer

question = "Explain how semantic caching reduces API costs"
answer = "Semantic caching reuses answers to similar questions, reducing repeated API calls and cost."

save_cached_answer(question, answer)

result = find_cached_answer(question)

print("\n--- CACHE TEST RESULTS ---")
print("Question:", question)
print("Cache hit:", result["cache_hit"])
print("Similarity:", result["similarity"])
print("Matched question:", result["matched_question"])
print("Answer found:", result["answer"] is not None)

assert result["cache_hit"] is True, "Expected a cache hit"
assert result["answer"] == answer, "Cached answer does not match"
assert result["similarity"] >= 0.75, "Similarity is below threshold"

print("PASS: Cached answer was retrieved successfully.")
