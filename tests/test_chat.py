from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_greeting():
    response = client.post(
        "/chat/",
        json={"message": "Hola"},
    )

    assert response.status_code == 200
    assert response.json()["assistant"] == "EKO"
    assert "Hola" in response.json()["response"]


def test_chat_general_message():
    response = client.post(
        "/chat/",
        json={"message": "¿Qué puedes hacer?"},
    )

    assert response.status_code == 200
    assert "Todavía estoy aprendiendo" in response.json()["response"]


def test_chat_empty_message():
    response = client.post(
        "/chat/",
        json={"message": ""},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"][0]["field"] == "message"
    assert response.json()["details"][0]["message"] == "El mensaje no puede estar vacío."
    assert "input" not in response.text


def test_chat_whitespace_message():
    response = client.post(
        "/chat/",
        json={"message": "   "},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"][0]["field"] == "message"
    assert response.json()["details"][0]["message"] == "El mensaje no puede estar vacío."

def test_chat_missing_message():
    response = client.post(
        "/chat/",
        json={},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"][0]["field"] == "message"
    assert response.json()["details"][0]["message"] == "El campo es obligatorio."


def test_chat_message_too_long():
    response = client.post(
        "/chat/",
        json={"message": "a" * 2001},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"][0]["field"] == "message"
    assert response.json()["details"][0]["message"] == "El mensaje supera el máximo de 2000 caracteres."
