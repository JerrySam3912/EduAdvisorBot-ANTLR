from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService


router = APIRouter()
chat_service = ChatService()


@router.post("/message", response_model=ChatResponse)
def handle_chat_message(payload: ChatRequest) -> ChatResponse:
    return chat_service.handle_message(payload)
