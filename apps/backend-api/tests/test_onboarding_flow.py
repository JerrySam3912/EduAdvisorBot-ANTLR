from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService


def test_onboarding_asks_for_mssv_or_cohort_when_missing():
    service = ChatService()
    result = service.handle_message(ChatRequest(message="xin chào", session_id="onboard-1"))

    assert result.intent == "ONBOARDING"
    assert result.missing_slots == ["student_id_or_cohort"]
    assert "mã số sinh viên" in result.reply.lower() or "khóa" in result.reply.lower()


def test_onboarding_stores_cohort_and_reuses_it():
    service = ChatService()
    session_id = "onboard-2"

    first = service.handle_message(ChatRequest(message="mình học K23 ngành CS", session_id=session_id))
    second = service.handle_message(ChatRequest(message="IT094IU cần học gì trước?", session_id=session_id))

    assert first.intent in {"UNKNOWN", "ONBOARDING", "ASK_COURSE_REQUIREMENTS"}
    assert second.intent == "ASK_COURSE_REQUIREMENTS"
    assert second.slots.get("cohort") == "k23"
    assert second.slots.get("course_code") == "IT094IU"
