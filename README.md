# SafeAI Lab — Day 1: Minimal AI API

A minimal FastAPI application that answers user questions using **Google Gemini**.

## 📁 Project Structure

```
SafeAI_Lab/
├── app/
│   ├── __init__.py   ← Makes app/ a Python package
│   ├── main.py       ← FastAPI routes & request handling
│   └── ai.py         ← Gemini AI interaction (isolated)
├── tests/
│   └── test_ask.py   ← Endpoint tests (no real API calls needed)
├── .env              ← Your secrets (never commit this!)
├── .env.example      ← Template for required env vars
├── .gitignore        ← Keeps secrets and .venv out of git
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

## 🚀 Setup & Run

### 1. Get a Gemini API Key
Go to https://aistudio.google.com/app/apikey and create a free API key.

### 2. Create your `.env` file
```bash
copy .env.example .env
```
Then open `.env` and replace `your_gemini_api_key_here` with your real key.

### 3. Activate your virtual environment
```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

The API is now running at: **http://127.0.0.1:8000**

### 6. Try it out

**Option A — Interactive Docs (recommended for beginners)**

Open your browser: http://127.0.0.1:8000/docs

**Option B — curl**
```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'
```

**Expected response:**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence..."
}
```

## 🧪 Run Tests

```bash
pytest tests/ -v
```

Tests use mocking so they run **without a real API key** and **without the server running**.

## 🔄 Request Flow

```
POST /ask  {"question": "..."}
      │
      ▼
app/main.py   ← validates input with Pydantic
      │
      ▼
app/ai.py     ← calls Gemini, returns answer text
      │
      ▼
{"answer": "..."}
```

## 📚 What You Learned (Day 1)

| Concept | Where |
|---------|-------|
| FastAPI route definition | `app/main.py` |
| Pydantic request/response models | `app/main.py` |
| Separation of concerns | `app/ai.py` vs `app/main.py` |
| Loading secrets from `.env` | `app/ai.py` with `python-dotenv` |
| Basic error handling (HTTP status codes) | `app/main.py` |
| Mocking in tests | `tests/test_ask.py` |
