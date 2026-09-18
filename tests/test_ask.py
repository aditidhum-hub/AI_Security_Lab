"""
tests/test_ask.py — Basic tests for the /ask endpoint
-------------------------------------------------------
We use FastAPI's TestClient (backed by httpx) which lets us
send real HTTP requests to our app WITHOUT starting a server.
This makes tests fast and self-contained.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

# Create a test client that talks directly to our FastAPI app in-memory.
client = TestClient(app)


def test_root_endpoint():
    """The GET / health-check should return 200 OK."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_returns_answer():
    """
    POST /ask with a valid question should return a 200 with an 'answer' field.

    We mock get_ai_answer so the test never calls the real Gemini API.
    This means:
    - Tests run instantly (no network call).
    - Tests work even without a GEMINI_API_KEY.
    - We are testing OUR code (routing, validation), not Google's servers.
    """
    fake_answer = "Artificial Intelligence is the simulation of human intelligence by machines."

    # patch() temporarily replaces get_ai_answer with a function that
    # returns our fake_answer string instead of calling Gemini.
    with patch("app.main.get_ai_answer", return_value=fake_answer):
        response = client.post("/ask", json={"question": "What is AI?"})

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] == fake_answer


def test_ask_rejects_empty_question():
    """POST /ask with an empty question should return 400 Bad Request."""
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_ask_missing_field():
    """POST /ask with no 'question' field should return 422 Unprocessable Entity."""
    response = client.post("/ask", json={})
    assert response.status_code == 422


def test_ask_handles_ai_error():
    """If the AI layer raises an exception, we should get 502, not a server crash."""
    with patch("app.main.get_ai_answer", side_effect=Exception("Gemini is down")):
        response = client.post("/ask", json={"question": "Hello?"})

    assert response.status_code == 502
    assert "AI service error" in response.json()["detail"]
