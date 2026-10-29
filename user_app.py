import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="AI Question Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("AI Question Assistant")
st.write("Ask a question and get an AI-generated answer.")

with st.form("question_form"):
    question = st.text_area(
        "Enter your question",
        placeholder="Example: What is semantic caching?",
        height=120
    )
    submitted = st.form_submit_button(
        "Ask AI",
        use_container_width=True
    )

if submitted:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Generating your answer..."):
                response = requests.post(
                    API_URL,
                    json={"question": question.strip()},
                    timeout=120
                )

            if response.status_code == 200:
                data = response.json()

                st.subheader("Answer")
                st.write(data.get("answer", "No answer received."))

                st.divider()
                st.subheader("Request Details")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Cache Status",
                        "HIT" if data.get("cache_hit") else "MISS"
                    )

                with col2:
                    latency = data.get("latency_ms")
                    st.metric(
                        "Response Time",
                        f"{latency:.2f} ms"
                        if isinstance(latency, (int, float))
                        else "N/A"
                    )

                st.write(
                    "**Selected Model:**",
                    data.get("model_name", "Not available")
                )
            else:
                st.error(f"Request failed: HTTP {response.status_code}")
                st.code(response.text[:1000])

        except requests.RequestException:
            st.error(
                "Cannot connect to the backend. "
                "Make sure FastAPI is running at http://127.0.0.1:8000."
            )
