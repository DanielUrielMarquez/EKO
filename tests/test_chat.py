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