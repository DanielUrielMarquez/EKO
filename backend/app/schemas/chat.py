from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="Mensaje enviado por el usuario",
    )


class ChatResponse(BaseModel):
    response: str
    assistant: str = "EKO"