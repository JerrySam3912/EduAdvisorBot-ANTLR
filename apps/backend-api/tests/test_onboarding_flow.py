from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService


def test_onboarding_asks_for_mssv_or_cohort_when_missing():
    """xin chào is a greeting (GREETING), bot responds with onboarding request."""
    service = ChatService()
    result = service.handle_message(ChatRequest(message="xin chào", session_id="onboard-1"))

    # "xin chào" should be classified as GREETING
    assert result.intent == "GREETING"
    # Bot should request identity info
    assert "student_id_or_cohort_and_major" in result.missing_slots


def test_onboarding_stores_cohort_and_reuses_it():
    """When user provides identity info (cohort + major), bot acknowledges it."""
    service = ChatService()
    session_id = "onboard-2"

    # First message: user says they study K23 CS
    first = service.handle_message(ChatRequest(message="mình học K23 ngành CS", session_id=session_id))
    # Should acknowledge identity since both cohort and major are provided
    assert first.intent == "IDENTITY_ACKNOWLEDGED"
    # Cohort and major should be stored
    assert first.slots.get("cohort") == "k23"
    assert first.slots.get("major") == "cs"

    # Second message: user asks about course requirements
    second = service.handle_message(ChatRequest(message="IT094IU cần học gì trước?", session_id=session_id))
    assert second.intent == "ASK_PREVIOUS_ONLY"
    # Cohort from first message should be reused
    assert second.slots.get("cohort") == "k23"
    assert second.slots.get("course_code") == "IT094IU"


def test_mssv_only_triggers_onboarding_asking_for_major():
    """When user provides only MSSV (no major), bot should ask for the major."""
    service = ChatService()
    session_id = "onboard-3"

    # User provides only MSSV — should get ONBOARDING asking for major
    result = service.handle_message(ChatRequest(message="2401036", session_id=session_id))
    assert result.intent == "ONBOARDING"
    # Bot should ask for major (identity incomplete: 7-digit MSSV gives cohort but not major)
    assert "cohort_and_major" in result.missing_slots or result.missing_slots == ["cohort_and_major"]


def test_major_only_asks_for_cohort_not_course():
    """When user provides only major (no cohort), bot asks for cohort, NOT course code."""
    service = ChatService()
    session_id = "onboard-5"

    result = service.handle_message(ChatRequest(message="mình học ngành CS", session_id=session_id))
    assert result.intent == "ONBOARDING"
    assert result.slots.get("major") == "cs"
    assert result.slots.get("cohort") is None
    # Must ask for cohort, NOT course code
    assert "khóa" in result.reply.lower() or "k21" in result.reply.lower() or "k22" in result.reply.lower()
    # Should NOT ask for course code
    assert "mã môn" not in result.reply.lower()
    assert "môn học" not in result.reply.lower() or "khóa" in result.reply.lower()


def test_standalone_cs_major_not_treated_as_course_code():
    """'mình học CS' (no ngành prefix) should extract CS as major, not course_code.
    Bot should ask for cohort, NOT say 'no data for môn CS'."""
    service = ChatService()
    session_id = "standalone-major-1"

    result = service.handle_message(ChatRequest(message="mình học CS", session_id=session_id))
    assert result.intent == "ONBOARDING"
    assert result.slots.get("major") == "cs"
    assert result.slots.get("cohort") is None
    # Must NOT produce misleading "course not found" error
    assert "mình chưa tìm thấy dữ liệu cho môn" not in result.reply.lower()
    assert "khóa" in result.reply.lower()


def test_standalone_ne_major_extracted():
    """'mình học NE' should extract NE as major."""
    service = ChatService()
    result = service.handle_message(ChatRequest(message="mình học NE", session_id="standalone-major-2"))
    assert result.intent == "ONBOARDING"
    assert result.slots.get("major") == "ne"
    assert result.slots.get("cohort") is None
    assert "khóa" in result.reply.lower()


def test_cs_major_with_explicit_knowledge_still_asks_cohort():
    """'mình học CS, cho mình hỏi về OOP' should ask for cohort, not answer the course question."""
    service = ChatService()
    session_id = "standalone-major-3"

    result = service.handle_message(
        ChatRequest(message="mình học CS, cho mình hỏi về OOP", session_id=session_id)
    )
    assert result.intent == "ONBOARDING"
    assert result.slots.get("major") == "cs"
    assert result.slots.get("cohort") is None
    assert "khóa" in result.reply.lower()


def test_major_only_asking_about_course_still_asks_for_cohort():
    """When user provides only major AND asks about a course, bot must ask for cohort first."""
    service = ChatService()
    session_id = "onboard-6"

    # User says they study CS AND asks about a course
    result = service.handle_message(
        ChatRequest(message="mình học ngành CS, mình muốn hỏi về OOP", session_id=session_id)
    )
    # Bot must ask for cohort first before answering course question
    assert result.intent == "ONBOARDING"
    assert result.slots.get("major") == "cs"
    assert result.slots.get("cohort") is None
    # Must ask for cohort, NOT try to answer the course question
    assert "khóa" in result.reply.lower() or "k21" in result.reply.lower() or "k22" in result.reply.lower()
    assert "mã môn" not in result.reply.lower()


def test_complete_identity_acknowledged_then_ask_course():
    """Complete identity (cohort + major) → IDENTITY_ACKNOWLEDGED → then ask course → answered."""
    service = ChatService()
    session_id = "onboard-4"

    # Complete identity
    ack = service.handle_message(ChatRequest(message="mình học K23 ngành CS", session_id=session_id))
    assert ack.intent == "IDENTITY_ACKNOWLEDGED"
    assert ack.slots.get("cohort") == "k23"
    assert ack.slots.get("major") == "cs"

    # Ask about course — should be answered
    course = service.handle_message(ChatRequest(message="tiên quyết IT017IU là gì?", session_id=session_id))
    assert course.intent == "ASK_PREREQUISITE_ONLY"
    assert course.slots.get("course_code") == "IT017IU"

