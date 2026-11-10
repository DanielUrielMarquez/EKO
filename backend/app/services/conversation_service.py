from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload


from app.models import Conversation, message


def list_conversations(db: Session) -> list[Conversation]:
    statement = (
        select(Conversation)
        .order_by(
            Conversation.updated_at.desc(),
            Conversation.id.desc(),
        )
    )

    return db.scalars(statement).all()


def get_conversation(
    db: Session,
    conversation_id: int,
) -> Conversation | None:
    statement = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )

    conversation = db.scalars(statement).first()

    if conversation is not None:
        conversation.messages.sort(key=lambda message: message.id)

    return conversation