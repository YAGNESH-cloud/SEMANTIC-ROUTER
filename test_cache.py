from app.database import initialize_database
from app.cache import find_cached_answer, save_cached_answer

initialize_database()

question1 = "What is machine learning?"
answer1 = "Machine learning is a branch of AI that learns patterns from data."

save_cached_answer(question1, answer1)

question2 = "Explain machine learning to me."

result = find_cached_answer(question2)

print("Original question:", question1)
print("New question:", question2)
print("Cache result:", result)
