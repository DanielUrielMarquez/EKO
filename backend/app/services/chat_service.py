from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation, Message
from app.services.groq_client import generate_response


def process_message(
    db: Session,
    message: str,
    conversation_id: int | None = None,
) -> tuple[str, int]:
    normalized_message = message.strip()

    if not normalized_message:
        raise ValueError("El mensaje no puede estar vacío.")

    try:
        # Buscar una conversación existente o crear una nueva.
        if conversation_id is not None:
            conversation = db.get(Conversation, conversation_id)

            if conversation is None:
                raise HTTPException(
                    status_code=404,
                    detail="La conversación solicitada no existe.",)
        else:
            conversation = Conversation(
                title=normalized_message[:100],
            )
            db.add(conversation)
            db.flush()

        # Recuperar el historial anterior.
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at, Message.id)
        )

        previous_messages = db.scalars(statement).all()

        history = [
            {
                "role": item.role,
                "content": item.content,
            }
            for item in previous_messages
        ]

        # Incorporar el mensaje actual para enviarlo a Groq.
        history.append({
            "role": "user",
            "content": normalized_message,
        })

        response = generate_response(history)

        # Guardar ambos mensajes.
        db.add_all([
            Message(
                conversation_id=conversation.id,
                role="user",
                content=normalized_message,
            ),
            Message(
                conversation_id=conversation.id,
                role="assistant",
                content=response,
            ),
        ])

        # Actualizar la fecha de modificación.
        from datetime import datetime, timezone

        conversation.updated_at = datetime.now(timezone.utc)

        db.commit()

        return response, conversation.id

    except Exception:
        db.rollback()
        raise
