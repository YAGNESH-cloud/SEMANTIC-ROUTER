# Semantic Cache and Cost-Aware Router

An AI question-answering application that uses semantic caching and cost-aware model routing to reduce repeated AI model calls and improve response time.

## Features

- AI-powered question answering using Groq models
- Semantic caching for similar questions
- Cost-aware AI model routing
- FastAPI backend
- Streamlit user application
- Monitoring dashboard
- SQLite-based cache and request metrics
- Cache-hit, latency, and estimated-cost tracking

## Architecture

```text
User
  |
  v
Streamlit User Application
  |
  v
FastAPI Backend
  |
  v
Semantic Cache
  |
  +---- Cache HIT ----> Reuse Cached Answer
  |
  +---- Cache MISS ---> Model Router
                            |
                            v
                        Groq AI Model
                            |
                            v
                       Generated Answer
  |
  v
Return Answer and Record Metrics
```

## Requirements

- Python 3.10 or compatible version
- pip
- Groq API key

## Setup on Windows

### 1. Clone the repository

```powershell
git clone https://github.com/YAGNESH-cloud/SEMANTIC-ROUTER.git
cd SEMANTIC-ROUTER
```

These commands are for setting up the project on another computer. Do not run them inside your existing project folder.

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure the API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own key. Never upload your actual API key to GitHub.

### 5. Run the backend

```powershell
python -m uvicorn app.main:app --reload
```

- Backend: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs
- Metrics endpoint: http://127.0.0.1:8000/metrics

### 6. Run the user application

Open a second terminal in the project folder:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run user_app.py --server.port 8502
```

User application: http://localhost:8502

### 7. Run the monitoring dashboard

Open a third terminal:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run dashboard.py --server.port 8501
```

Monitoring dashboard: http://localhost:8501

## Testing

Run the available cache and database tests individually:

```powershell
python test_cache.py
python test_cache_lookup.py
python test_database.py
```

Some tests may require dependencies or additional configuration.

## Project Structure

```text
SEMANTIC-ROUTER/
├── app/
│   ├── __init__.py
│   ├── cache.py
│   ├── database.py
│   ├── main.py
│   └── router.py
├── dashboard.py
├── user_app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Security

- Keep `.env` private.
- Never commit API keys or credentials.
- Keep `.venv/` and local database files out of version control.
- Configure secrets securely in the deployment environment.

## Limitations

- AI-generated answers may be inaccurate.
- Cache similarity thresholds affect which answers are reused.
- Displayed API costs are estimates.
- Additional security, testing, and deployment configuration are needed before production use.

## License

Add an appropriate open-source license before distributing this project.