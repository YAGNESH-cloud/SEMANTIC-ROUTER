from app.database import initialize_database, record_request, get_metrics

initialize_database()

record_request(
    question="What is machine learning?",
    cache_hit=False,
    model_name="demo-small",
    input_tokens=10,
    output_tokens=20,
    cost_usd=0.0001,
    latency_ms=120,
    status="success"
)

metrics = get_metrics()

print("Database initialized successfully")
print("Total recorded requests:", len(metrics))

if metrics:
    print("Latest request:", metrics[0])
