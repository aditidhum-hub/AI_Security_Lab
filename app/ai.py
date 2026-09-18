"""
app/ai.py — AI interaction layer
---------------------------------
This file is the ONLY place that knows about Google Gemini.
If you ever switch to OpenAI or another provider, you only
change THIS file. The rest of the app stays the same.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from the .env file into the environment.
# This must happen before we try to read GEMINI_API_KEY.
load_dotenv()


def get_ai_answer(question: str) -> str:
    """
    Send a question to Google Gemini and return its text answer.

    Args:
        question: The user's plain-text question.

    Returns:
        The model's answer as a string.

    Raises:
        ValueError: If the GEMINI_API_KEY environment variable is not set.
        Exception:  If the Gemini API call fails for any reason.
    """
    # 1. Read the API key from the environment (loaded from .env above).
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Copy .env.example to .env and add your key."
        )

    # 2. Configure the Gemini client with our API key.
    genai.configure(api_key=api_key)

    # 3. Choose the model. gemini-2.0-flash is fast and free-tier friendly.
    model = genai.GenerativeModel("gemini-3.6-flash")

    # 4. Send the question and get a response.
    response = model.generate_content(question)

    # 5. Return only the text part of the response.
    return response.text
