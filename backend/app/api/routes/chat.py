from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_message


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    response, conversation_id = process_message(
        db=db,
        message=request.message,
        conversation_id=request.conversation_id,
    )

    return ChatResponse(
        response=response,
        conversation_id=conversation_id,
    )
