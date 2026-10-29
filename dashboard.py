
import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

st.set_page_config(
    page_title="Semantic Router Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Semantic Caching & Cost-Aware Routing")
st.caption("Monitor API requests, cache performance, model routing, and costs.")

if st.button("Refresh metrics"):
    st.rerun()

try:
    response = requests.get(
        f"{API_URL}/metrics",
        timeout=15
    )
    response.raise_for_status()
    data = response.json()

except requests.RequestException as exc:
    st.error(f"Could not connect to the backend: {exc}")
    st.info("Start the FastAPI server and refresh this page.")
    st.stop()

total = data["total_requests"]
hits = data["cache_hits"]
misses = data["cache_misses"]
hit_rate = data["cache_hit_rate_percent"]
total_cost = data["total_cost_usd"]
avg_latency = data["average_latency_ms"]

col1, col2, col3 = st.columns(3)
col1.metric("Total Requests", total)
col2.metric("Cache Hits", hits)
col3.metric("Cache Hit Rate", f"{hit_rate:.2f}%")

col4, col5, col6 = st.columns(3)
col4.metric("Cache Misses", misses)
col5.metric("Total Recorded Cost", f"${total_cost:.6f}")
col6.metric("Average Latency", f"{avg_latency:.2f} ms")

st.divider()

st.subheader("Model Usage")

records = data.get("requests", [])
df = pd.DataFrame(records)

if df.empty:
    st.info("No requests have been recorded yet.")

else:
    model_counts = df["model_name"].value_counts()
    st.bar_chart(model_counts)

    st.subheader("Request History")

    display_columns = [
        "id",
        "question",
        "cache_hit",
        "model_name",
        "cost_usd",
        "latency_ms",
        "status"
    ]

    st.dataframe(
        df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Request Latency")

    latency_df = df[["id", "latency_ms"]].sort_values("id")
    st.line_chart(
        latency_df.set_index("id")
    )

st.caption(
    "Demo mode: model selection is simulated, and recorded costs "
    "may include earlier test data. Real AI costs require provider integration."
)
