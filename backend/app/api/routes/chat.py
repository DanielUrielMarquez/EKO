from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationListItem,
)
from app.services.chat_service import process_message
from app.services.conversation_service import (
    get_conversation,
    list_conversations,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    response, conversation_id = process_message(
        db=db,
        message=request.message,
        user_id=current_user.id,
        conversation_id=request.conversation_id,
    )

    return ChatResponse(
        response=response,
        conversation_id=conversation_id,
    )


@router.get(
    "/conversations",
    response_model=list[ConversationListItem],
)
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_conversations(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetail,
)
def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="La conversación solicitada no existe.",
        )

    return conversation