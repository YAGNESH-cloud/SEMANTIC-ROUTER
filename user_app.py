
import time
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="Semantic AI | Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, #20265a 0%, transparent 40%),
        radial-gradient(ellipse at 90% 20%, #183b52 0%, transparent 38%),
        #080d19;
    color: #f4f7ff;
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1100px;
    padding: 2rem 1.5rem 4rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 12px #7c6cff22; }
    50% { box-shadow: 0 0 28px #7c6cff66; }
}

@keyframes pulse {
    0%, 100% { opacity: .65; }
    50% { opacity: 1; }
}

.hero {
    text-align: center;
    padding: 3rem 0 2rem;
    animation: fadeUp .8s ease both;
}

.logo {
    display: inline-block;
    padding: 10px 18px;
    border: 1px solid #6675d855;
    border-radius: 40px;
    background: #171d39;
    color: #b8c2ff;
    font-size: 13px;
    letter-spacing: 2px;
    font-weight: 700;
    animation: glow 3s ease-in-out infinite;
}

.hero h1 {
    color: #ffffff;
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -2px;
    margin: 1.4rem 0 .8rem;
}

.gradient-text {
    background: linear-gradient(90deg, #9c9cff, #65e5ed, #b4a0ff);
    background-size: 200% auto;
    color: #a9b4ff;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientMove 5s linear infinite;
}

@keyframes gradientMove {
    to { background-position: 200% center; }
}

.hero p {
    color: #aab6d1;
    font-size: 1.05rem;
    line-height: 1.8;
}

.feature-row {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 1.4rem;
}

.feature {
    color: #c9d2f5;
    background: #141c30;
    border: 1px solid #2c3858;
    border-radius: 30px;
    padding: 8px 13px;
    font-size: 12px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, #141c30, #0f1728);
    border: 1px solid #344365;
    border-radius: 22px;
    animation: fadeUp .7s ease both;
}

.stApp textarea {
    background: #0c1425 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 1px solid #3a4b73 !important;
    border-radius: 14px !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
}

.stApp textarea::placeholder {
    color: #8492b1 !important;
    -webkit-text-fill-color: #8492b1 !important;
    opacity: 1 !important;
}

.stApp label,
.stApp [data-testid="stWidgetLabel"] p {
    color: #e3eaff !important;
}

div.stButton > button,
div.stFormSubmitButton > button {
    background: linear-gradient(100deg, #8d83ff, #62dce9);
    color: #080d19 !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    min-height: 44px;
    transition: transform .2s ease, filter .2s ease;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    transform: translateY(-2px);
    filter: brightness(1.12);
}

div.stButton > button:active,
div.stFormSubmitButton > button:active {
    transform: scale(.98);
}

[data-testid="stMetric"] {
    background: #111b30;
    border: 1px solid #2e3d60;
    border-radius: 15px;
    padding: 17px;
    animation: fadeUp .6s ease both;
}

[data-testid="stMetricLabel"] {
    color: #aab8d7 !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

.answer-panel {
    background: linear-gradient(145deg, #151f36, #101829);
    border: 1px solid #3a4a70;
    border-left: 4px solid #7f94ff;
    border-radius: 16px;
    padding: 22px;
    animation: fadeUp .5s ease both;
}

.answer-label {
    color: #aab8ff;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border-color: #293754 !important;
}

.stCaption, [data-testid="stCaptionContainer"] {
    color: #8998b8 !important;
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if "request_error" not in st.session_state:
    st.session_state.request_error = None


def ask_question(question):
    question = question.strip()

    if not question:
        st.session_state.request_error = "Please type a question first."
        return

    st.session_state.request_error = None

    try:
        with st.spinner("✦ Processing your question..."):
            response = requests.post(
                API_URL,
                json={"question": question},
                timeout=120
            )

        if response.status_code != 200:
            st.session_state.request_error = (
                f"Backend returned HTTP {response.status_code}."
            )
            try:
                st.session_state.request_error += (
                    " " + str(response.json().get("detail", response.text))
                )
            except ValueError:
                st.session_state.request_error += " " + response.text[:300]
            return

        data = response.json()

        if not isinstance(data, dict):
            st.session_state.request_error = "Unexpected response from the backend."
            return

        st.session_state.last_result = data
        st.session_state.last_question = question

        if not data.get("answer"):
            st.session_state.request_error = (
                "The backend responded, but no answer was returned."
            )

    except requests.Timeout:
        st.session_state.request_error = (
            "The request timed out. Try again or check the backend logs."
        )
    except requests.ConnectionError:
        st.session_state.request_error = (
            "Cannot connect to FastAPI. Start the backend on port 8000."
        )
    except requests.RequestException as error:
        st.session_state.request_error = f"Request failed: {error}"
    except ValueError:
        st.session_state.request_error = (
            "The backend did not return valid JSON."
        )


st.markdown("""
<div class="hero">
    <div class="logo">✦ SEMANTIC AI</div>
    <h1>Ask anything.<br><span class="gradient-text">Think smarter.</span></h1>
    <p>Your intelligent question assistant, powered by AI,<br>
    semantic caching and cost-aware routing.</p>
    <div class="feature-row">
        <span class="feature">✦ AI-Powered Answers</span>
        <span class="feature">◈ Semantic Cache</span>
        <span class="feature">⚡ Faster Responses</span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("### ✦ What would you like to know?")
    st.caption("Enter a question below to get started.")

    with st.form("question_form", clear_on_submit=False):
        question = st.text_area(
            "Your question",
            placeholder="Example: How does semantic caching reduce API costs?",
            height=135,
            key="question_input",
            label_visibility="collapsed"
        )

        submitted = st.form_submit_button(
            "✦  Generate Answer",
            use_container_width=True
        )

    if submitted:
        ask_question(question)

    st.markdown("**Need an idea? Try one of these:**")

    example_columns = st.columns(3)

    examples = [
        "What is semantic caching?",
        "Explain machine learning simply.",
        "How can AI routing reduce costs?"
    ]

    for index, example in enumerate(examples):
        with example_columns[index]:
            if st.button(
                example,
                key=f"example_{index}",
                use_container_width=True
            ):
                ask_question(example)

if st.session_state.request_error:
    st.error(st.session_state.request_error)

data = st.session_state.last_result

if data is not None:
    st.write("")
    st.markdown("## ✦ Your Answer")

    answer = data.get("answer")

    if answer:
        with st.container(border=True):
            st.markdown(
                '<div class="answer-label">AI RESPONSE</div>',
                unsafe_allow_html=True
            )
            st.markdown(str(answer))

    st.write("")
    st.markdown("### Request Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        cache_hit = data.get("cache_hit")
        cache_label = (
            "HIT" if cache_hit is True
            else "MISS" if cache_hit is False
            else "N/A"
        )
        st.metric("Cache Status", cache_label)

    with col2:
        latency = data.get("latency_ms")
        st.metric(
            "Response Time",
            f"{latency:.2f} ms"
            if isinstance(latency, (int, float))
            else "N/A"
        )

    with col3:
        similarity = data.get("similarity")
        st.metric(
            "Similarity Score",
            f"{similarity:.4f}"
            if isinstance(similarity, (int, float))
            else "N/A"
        )

    with st.expander("View technical details"):
        st.write("**Question:**", data.get("question", st.session_state.last_question))
        st.write("**Model:**", data.get("model_name", "Not provided"))
        st.write("**Status:**", data.get("status", "Not provided"))
        st.json(data)

st.divider()

st.markdown("""
<div style="text-align:center; padding: 14px 0 25px; color:#7e8dad;">
    <div style="font-size:14px; font-weight:700; letter-spacing:2px;">
        ✦ SEMANTIC AI
    </div>
    <div style="font-size:12px; margin-top:8px;">
        Intelligent answers · Semantic caching · Cost-aware routing
    </div>
</div>
""", unsafe_allow_html=True)
