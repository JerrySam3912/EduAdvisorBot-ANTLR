from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService


def test_session_memory_reuses_last_course_code():
    service = ChatService()
    session_id = "session-test-1"

    first = service.handle_message(ChatRequest(message="IT094IU cần học gì trước?", session_id=session_id, student_id="ITCSIU22001"))
    second = service.handle_message(ChatRequest(message="môn này có học được không", session_id=session_id, student_id="ITCSIU22001"))

    assert first.intent == "ASK_PREVIOUS_ONLY"
    assert second.intent == "ASK_COURSE_ELIGIBILITY"
    assert second.slots.get("course_code") == "IT094IU"
