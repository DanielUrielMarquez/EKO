from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user: Mapped["User | None"] = relationship(
        back_populates="conversations",
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Nueva conversación",
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    summary_through_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    