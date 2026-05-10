from app.nlp.parser import parse_command
from app.nlp.processor import CommandProcessor
from app.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    def __init__(self):
        self.processor = CommandProcessor()

    def handle_message(self, payload: ChatRequest) -> ChatResponse:
        parsed = parse_command(payload.message, student_id=payload.student_id)
        result = self.processor.process(parsed)
        return ChatResponse(**result)
