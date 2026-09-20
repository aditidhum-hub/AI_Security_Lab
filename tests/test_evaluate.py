import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_evaluate_passes_when_answer_matches():
    with patch('app.main.get_ai_answer', return_value='The capital of France is Paris.'):
        response = client.post(
            '/evaluate',
            json={'question': 'What is the capital of France?', 'expected_answer': 'Paris'},
        )
    assert response.status_code == 200
    data = response.json()
    assert data['passed'] is True
    assert data['question'] == 'What is the capital of France?'
    assert data['expected_answer'] == 'Paris'
    assert data['ai_answer'] == 'The capital of France is Paris.'


def test_evaluate_fails_when_answer_does_not_match():
    with patch('app.main.get_ai_answer', return_value='The capital of France is Lyon.'):
        response = client.post(
            '/evaluate',
            json={'question': 'What is the capital of France?', 'expected_answer': 'Paris'},
        )
    assert response.status_code == 200
    assert response.json()['passed'] is False


def test_evaluate_comparison_is_case_insensitive():
    with patch('app.main.get_ai_answer', return_value='Paris is the capital.'):
        response = client.post(
            '/evaluate',
            json={'question': 'Capital of France?', 'expected_answer': 'PARIS'},
        )
    assert response.status_code == 200
    assert response.json()['passed'] is True


def test_evaluate_rejects_empty_question():
    response = client.post(
        '/evaluate',
        json={'question': '   ', 'expected_answer': 'Paris'},
    )
    assert response.status_code == 400
    assert 'empty' in response.json()['detail'].lower()


def test_evaluate_rejects_empty_expected_answer():
    response = client.post(
        '/evaluate',
        json={'question': 'What is the capital of France?', 'expected_answer': '   '},
    )
    assert response.status_code == 400
    assert 'empty' in response.json()['detail'].lower()


def test_evaluate_missing_fields():
    response = client.post('/evaluate', json={'question': 'Who?'})
    assert response.status_code == 422


def test_evaluate_handles_ai_error():
    with patch('app.main.get_ai_answer', side_effect=Exception('Gemini is down')):
        response = client.post(
            '/evaluate',
            json={'question': 'What is 2+2?', 'expected_answer': '4'},
        )
    assert response.status_code == 502
    assert 'AI service error' in response.json()['detail']