
from sqlalchemy import select

from app.core.tokens import create_access_token
from app.models import Conversation, Message, User


def create_other_user(db_session):
    user = User(
        email="otro@example.com",
        hashed_password="hash-de-prueba",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_user_only_sees_own_conversations(
    client_with_db,
    db_session,
    test_user,
    auth_headers,
):
    other_user = create_other_user(db_session)

    own_conversation = Conversation(
        title="Mi conversación",
        user_id=test_user.id,
    )
    foreign_conversation = Conversation(
        title="Conversación ajena",
        user_id=other_user.id,
    )

    db_session.add_all([own_conversation, foreign_conversation])
    db_session.commit()

    response = client_with_db.get(
        "/chat/conversations",
        headers=auth_headers,
    )

    assert response.status_code == 200

    conversations = response.json()

    assert len(conversations) == 1
    assert conversations[0]["title"] == "Mi conversación"


def test_user_cannot_access_another_users_conversation(
    client_with_db,
    db_session,
    auth_headers,
):
    other_user = create_other_user(db_session)

    conversation = Conversation(
        title="Conversación privada",
        user_id=other_user.id,
    )
    db_session.add(conversation)
    db_session.commit()

    response = client_with_db.get(
        f"/chat/conversations/{conversation.id}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "La conversación solicitada no existe."


def test_user_cannot_send_message_to_another_users_conversation(
    client_with_db,
    db_session,
    auth_headers,
):
    other_user = create_other_user(db_session)

    conversation = Conversation(
        title="Conversación privada",
        user_id=other_user.id,
    )
    db_session.add(conversation)
    db_session.commit()

    response = client_with_db.post(
        "/chat/",
        json={
            "message": "Intento acceder a esta conversación",
            "conversation_id": conversation.id,
        },
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "La conversación solicitada no existe."

    messages = db_session.scalars(
        select(Message).where(
            Message.conversation_id == conversation.id
        )
    ).all()

    assert messages == []
