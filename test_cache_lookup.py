from app.cache import find_cached_answer

question = "Explain how semantic caching reduces API costs"

result = find_cached_answer(question)

print("\n--- CACHE TEST RESULTS ---")
print("Question:", question)
print("Cache hit:", result["cache_hit"])
print("Similarity:", result["similarity"])
print("Matched question:", result["matched_question"])
print("Answer found:", result["answer"] is not None)
