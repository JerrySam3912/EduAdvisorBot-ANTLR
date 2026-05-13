from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="User natural language message")
    session_id: str | None = Field(default=None, description="Optional session identifier")
    student_id: str | None = Field(default=None, description="Optional student identifier")
    user_id: str | None = Field(default=None, description="Deprecated; use student_id or session_id")


class ChatResponse(BaseModel):
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    reply: str
    message: str | None = None
    slots: dict = Field(default_factory=dict)
    missing_slots: list[str] = Field(default_factory=list)
    follow_up_question: str | None = None
    data: dict | None = None
