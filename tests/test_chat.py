from unittest.mock import patch

import pytest
from sqlalchemy import select

from app.models import Conversation, Message


@pytest.mark.parametrize(
    ("message", "expected_response"),
    [
        ("Hola", "¡Hola! Soy EKO."),
        ("¿Qué puedes hacer?", "Puedo ayudarte con muchas tareas."),
    ],
)
def test_chat_success(client_with_db, db_session, message, expected_response):
    expected_history = [
        {"role": "user", "content": message},
    ]

    with patch(
        "app.services.chat_service.generate_response",
        return_value=expected_response,
    ) as mock_generate:
        response = client_with_db.post(
            "/chat/",
            json={"message": message},
        )

    assert response.status_code == 200
    assert response.json()["assistant"] == "EKO"
    assert response.json()["response"] == expected_response
    assert response.json()["conversation_id"] > 0

    mock_generate.assert_called_once_with(expected_history)

    conversation = db_session.get(
        Conversation,
        response.json()["conversation_id"],
    )

    assert conversation is not None
    assert conversation.title == message[:100]

    messages = db_session.scalars(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.id)
    ).all()

    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == message
    assert messages[1].role == "assistant"
    assert messages[1].content == expected_response


def test_chat_empty_message(client_with_db):
    response = client_with_db.post(
        "/chat/",
        json={"message": ""},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"][0]["field"] == "message"
    assert response.json()["details"][0]["message"] == "El mensaje no puede estar vacío."
    assert "input" not in response.text


def test_chat_whitespace_message(client_with_db):
    response = client_with_db.post(
        "/chat/",
        json={"message": "   "},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"][0]["field"] == "message"
    assert response.json()["details"][0]["message"] == "El mensaje no puede estar vacío."


def test_chat_missing_message(client_with_db):
    response = client_with_db.post(
        "/chat/",
        json={},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"][0]["field"] == "message"
    assert response.json()["details"][0]["message"] == "El campo es obligatorio."


def test_chat_message_too_long(client_with_db):
    response = client_with_db.post(
        "/chat/",
        json={"message": "a" * 2001},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"][0]["field"] == "message"
    assert response.json()["details"][0]["message"] == "El mensaje supera el máximo de 2000 caracteres."


def test_chat_conversation_history(client_with_db):
    with patch(
        "app.services.chat_service.generate_response",
        side_effect=[
            "¡Mucho gusto, Uriel!",
            "Te llamás Uriel.",
        ],
    ) as mock_generate:

        first_response = client_with_db.post(
            "/chat/",
            json={"message": "Me llamo Uriel"},
        )

        conversation_id = first_response.json()["conversation_id"]

        second_response = client_with_db.post(
            "/chat/",
            json={
                "message": "¿Cómo me llamo?",
                "conversation_id": conversation_id,
            },
        )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert second_response.json()["response"] == "Te llamás Uriel."
    assert second_response.json()["conversation_id"] == conversation_id

    expected_history = [
        {"role": "user", "content": "Me llamo Uriel"},
        {"role": "assistant", "content": "¡Mucho gusto, Uriel!"},
        {"role": "user", "content": "¿Cómo me llamo?"},
    ]

    assert mock_generate.call_count == 2
    assert mock_generate.call_args_list[1].args[0] == expected_history


def test_chat_rollback_when_groq_fails(db_session):
    from app.services.chat_service import process_message

    with patch(
        "app.services.chat_service.generate_response",
        side_effect=RuntimeError("Error simulado de Groq"),
    ):
        with pytest.raises(RuntimeError):
            process_message(
                db=db_session,
                message="Hola",
            )

    conversations = db_session.scalars(
        select(Conversation)
    ).all()

    assert conversations == []

def test_chat_conversation_not_found(client_with_db):
    response = client_with_db.post(
        "/chat/",
        json={
            "message": "Hola",
            "conversation_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "La conversación solicitada no existe."
    )