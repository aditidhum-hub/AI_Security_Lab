"""
app/main.py — FastAPI application
----------------------------------
This is the entry point of the web application.
It defines the API routes (endpoints) and handles
HTTP requests and responses.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.ai import get_ai_answer

# Create the FastAPI app instance.
# FastAPI automatically generates interactive API docs at /docs
app = FastAPI(
    title="SafeAI Lab — Day 1",
    description="A minimal AI question-answering API powered by Google Gemini.",
    version="0.1.0",
)


# --- Request & Response Models ---
# Pydantic models describe the shape of JSON data.
# FastAPI uses them to validate incoming requests automatically.

class QuestionRequest(BaseModel):
    """The JSON body the user must send to /ask."""
    question: str


class AnswerResponse(BaseModel):
    """The JSON body we send back to the user."""
    answer: str


# --- Endpoints ---

@app.get("/")
def root():
    """Health-check endpoint. Confirms the server is running."""
    return {"status": "ok", "message": "SafeAI Lab API is running. POST to /ask"}


@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    """
    Accept a question and return an AI-generated answer.

    - Receives: { "question": "What is machine learning?" }
    - Returns:  { "answer": "Machine learning is..." }
    """
    # Guard: reject empty questions before hitting the AI API.
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        answer = get_ai_answer(request.question)
        return AnswerResponse(answer=answer)

    except ValueError as e:
        # Missing API key — a configuration error (500 Internal Server Error).
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        # Any other error from the Gemini API.
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(e)}",
        )
