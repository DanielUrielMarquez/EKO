from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Conversation


def list_conversations(
    db: Session,
    user_id: int,
) -> list[Conversation]:
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(
            Conversation.updated_at.desc(),
            Conversation.id.desc(),
        )
    )

    return db.scalars(statement).all()


def get_conversation(
    db: Session,
    conversation_id: int,
    user_id: int,
) -> Conversation | None:
    statement = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )

    conversation = db.scalars(statement).first()

    if conversation is not None:
        conversation.messages.sort(key=lambda message: message.id)

    return conversation