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
    title="SafeAI Lab — Day 2",
    description=(
        "A minimal AI question-answering and evaluation API powered by Google Gemini.\n\n"
        "Endpoints:\n"
        "- **POST /ask** — send a question, get an AI answer.\n"
        "- **POST /evaluate** — send a question + expected answer, get pass/fail."
    ),
    version="0.2.0",
)


# --- Request & Response Models ---
# Pydantic models describe the shape of JSON data.
# FastAPI uses them to validate incoming requests automatically.

class QuestionRequest(BaseModel):
    """The JSON body the user must send to /ask."""
    question: str


class AnswerResponse(BaseModel):
    """The JSON body we send back to the user from /ask."""
    answer: str


class EvaluateRequest(BaseModel):
    """The JSON body the user must send to /evaluate."""
    question: str
    expected_answer: str


class EvaluateResponse(BaseModel):
    """The JSON body we send back from /evaluate."""
    question: str
    expected_answer: str
    ai_answer: str
    passed: bool


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


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(request: EvaluateRequest):
    """
    Send a question to the AI and check whether its answer matches the expected answer.

    - Receives: { "question": "What is 2+2?", "expected_answer": "4" }
    - Returns:  { "question": ..., "expected_answer": ..., "ai_answer": ..., "passed": true/false }

    **Comparison logic (intentionally simple):**
    The AI answer and the expected answer are both stripped of leading/trailing
    whitespace and lowercased, then we check whether the expected answer string
    appears anywhere inside the AI answer string.
    This is deliberately naive — a learning exercise in why simple string
    matching is not enough for real AI evaluation.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if not request.expected_answer.strip():
        raise HTTPException(status_code=400, detail="Expected answer cannot be empty.")

    try:
        ai_answer = get_ai_answer(request.question)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(e)}",
        )

    # --- Simple comparison ---
    # Strip whitespace and lowercase both strings, then check if the
    # expected answer is a substring of the AI answer.
    # Example: expected="4", ai_answer="The answer is 4." → passed=True
    passed = request.expected_answer.strip().lower() in ai_answer.strip().lower()

    return EvaluateResponse(
        question=request.question,
        expected_answer=request.expected_answer,
        ai_answer=ai_answer,
        passed=passed,
    )
