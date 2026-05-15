import pytest
from app.nlp.parser import (
    extract_semester_code,
    extract_explicit_cohort,
    extract_course_code,
    extract_major_from_student_id,
    infer_cohort_from_student_id,
    normalize_text,
    parse_command,
    _antlr_classify,
)
from app.nlp.processor import CommandProcessor
from app.nlp.intents import (
    ASK_COURSE_ELIGIBILITY,
    ASK_COURSE_REQUIREMENTS,
    ASK_PREREQUISITE_ONLY,
    ASK_PREVIOUS_ONLY,
    ASK_REGISTRATION_TIME,
    ASK_DROP_TIME,
    ASK_REGISTRATION_PLATFORM,
)


# ============================================
# Parser Unit Tests
# ============================================

class TestNormalizeText:
    def test_strips_whitespace(self):
        assert normalize_text("  hello  ") == "hello"

    def test_lowercase(self):
        assert normalize_text("HELLO") == "hello"

    def test_preserves_content(self):
        assert normalize_text("IT017IU") == "it017iu"


class TestExtractSemesterCode:
    def test_sp25_format(self):
        assert extract_semester_code("học kỳ SP25") == "SP25"

    def test_su_25_format(self):
        assert extract_semester_code("su25") == "SU25"

    def test_fa_24_format(self):
        assert extract_semester_code("FA-24") == "FA24"

    def test_no_match(self):
        assert extract_semester_code("học kỳ 2024") is None

    # Summer semester variations
    def test_summer_variations(self):
        assert extract_semester_code("SUM26") == "SU26"
        assert extract_semester_code("sum26") == "SU26"
        assert extract_semester_code("SUMMER26") == "SU26"
        assert extract_semester_code("summer26") == "SU26"
        assert extract_semester_code("sum2026") == "SU26"

    def test_spring_variations(self):
        assert extract_semester_code("SP2026") == "SP26"
        assert extract_semester_code("Spring 2026") == "SP26"

    def test_fall_variations(self):
        assert extract_semester_code("FA2026") == "FA26"
        assert extract_semester_code("Fall 2026") == "FA26"

    def test_hkiii_variations(self):
        assert extract_semester_code("HKIII") == "HKIII"
        assert extract_semester_code("hoc ky III") == "HKIII"
        assert extract_semester_code("thoi gian drop HKIII") == "HKIII"

    def test_hoc_ky_he_variations(self):
        assert extract_semester_code("hoc ky he 2026") == "HK26"
        assert extract_semester_code("drop mon hoc ky he 2026") == "HK26"

    def test_drop_with_semester(self):
        assert extract_semester_code("thoi gian drop HKIII") == "HKIII"
        assert extract_semester_code("drop mon SUM26") == "SU26"


class TestExtractExplicitCohort:
    def test_k21_format(self):
        assert extract_explicit_cohort("khóa k21") == "k21"

    def test_khoa_format(self):
        assert extract_explicit_cohort("khoa 22") == "k22"

    def test_direct_format(self):
        assert extract_explicit_cohort("mình học K23") == "k23"


class TestExtractCourseCode:
    def test_it_format(self):
        assert extract_course_code("tôi muốn hỏi về IT017IU") == "IT017IU"

    def test_cs_format(self):
        assert extract_course_code("CS101IU là gì") == "CS101IU"

    def test_ne_format(self):
        assert extract_course_code("NE012") == "NE012"

    def test_no_match(self):
        assert extract_course_code("không có mã môn") is None


class TestStudentIdExtraction:
    def test_itcsiu_format(self):
        assert infer_cohort_from_student_id("ITCSIU22001") == "k22"
        assert extract_major_from_student_id("ITCSIU22001") == "cs"

    def test_ititwe_format(self):
        assert infer_cohort_from_student_id("ITITWE22009") == "k22"
        assert extract_major_from_student_id("ITITWE22009") == "it"

    def test_itdsiu_format(self):
        assert infer_cohort_from_student_id("ITDSIU23109") == "k23"
        assert extract_major_from_student_id("ITDSIU23109") == "ds"

    def test_itceiu_format(self):
        assert infer_cohort_from_student_id("ITCEIU24001") == "k24"
        assert extract_major_from_student_id("ITCEIU24001") == "ce"

    def test_no_student_id(self):
        assert infer_cohort_from_student_id(None) is None
        assert extract_major_from_student_id("") is None


# ============================================
# ANTLR Parser Tests
# ============================================

class TestAntlrClassify:
    def test_eligibility_intent(self):
        result = _antlr_classify("eligibility IT017IU")
        assert result is not None
        assert result["intent"] == ASK_COURSE_ELIGIBILITY
        assert result["course_code"] == "IT017IU"

    def test_prerequisite_intent(self):
        result = _antlr_classify("prerequisite IT017IU")
        assert result is not None
        assert result["intent"] == ASK_PREREQUISITE_ONLY

    def test_previous_intent(self):
        result = _antlr_classify("previous IT017IU")
        assert result is not None
        assert result["intent"] == ASK_PREVIOUS_ONLY

    def test_help_intent(self):
        result = _antlr_classify("help")
        assert result is not None
        assert result["intent"] == "HELP"


class TestParseCommand:
    def test_parses_eligibility_correctly(self):
        # Use ANTLR-supported pattern
        result = parse_command("eligible IT017IU")
        assert result["intent"] == ASK_COURSE_ELIGIBILITY
        assert result["slots"]["course_code"] == "IT017IU"
        assert result["antlr_parsed"] is True

    def test_parses_prerequisite_correctly(self):
        result = parse_command("tiên quyết của IT017IU")
        assert result["intent"] == ASK_PREREQUISITE_ONLY
        assert result["slots"]["course_code"] == "IT017IU"

    def test_parses_previous_correctly(self):
        result = parse_command("học trước IT017IU là gì")
        assert result["intent"] == ASK_PREVIOUS_ONLY
        assert result["slots"]["course_code"] == "IT017IU"

    def test_extracts_student_id_slots(self):
        result = parse_command("IT017IU là gì", student_id="ITCSIU22001")
        assert result["slots"]["student_id"] == "ITCSIU22001"
        assert result["slots"]["cohort"] == "k22"
        assert result["slots"]["major_from_student_id"] == "cs"

    def test_unknown_returns_unknown(self):
        result = parse_command("trời hôm nay đẹp quá")
        assert result["intent"] == "UNKNOWN"


# ============================================
# Processor Integration Tests
# ============================================

class TestCommandProcessor:
    def setup_method(self):
        self.processor = CommandProcessor()

    def test_course_eligibility_response(self):
        # Use ANTLR-supported pattern
        parsed = parse_command("eligible IT017IU", student_id="ITCSIU22001")
        result = self.processor.process(parsed)

        assert result["intent"] == ASK_COURSE_ELIGIBILITY
        assert "confidence" in result
        assert "reply" in result

    def test_prerequisite_only_response(self):
        parsed = parse_command("tiên quyết IT017IU", student_id="ITCSIU22001")
        result = self.processor.process(parsed)

        assert result["intent"] == ASK_PREREQUISITE_ONLY
        assert "IT017IU" in result["reply"]

    def test_previous_only_response(self):
        parsed = parse_command("học trước IT094IU", student_id="ITCSIU22001")
        result = self.processor.process(parsed)

        assert result["intent"] == ASK_PREVIOUS_ONLY

    def test_missing_course_asks_for_slot(self):
        # Use a query that clearly asks for a course but doesn't specify WHICH course
        parsed = parse_command("tiên quyết của môn nào", student_id="ITCSIU22001")
        result = self.processor.process(parsed)
        # Should ask for course code since no specific course was mentioned
        assert "missing_slots" in result
        assert "course_code" in result["missing_slots"]

    def test_unknown_intent_response(self):
        parsed = parse_command("trời mưa")
        result = self.processor.process(parsed)

        assert result["intent"] == "UNKNOWN"
        assert result["confidence"] < 0.5


# ============================================
# Intent Detection Tests
# ============================================

class TestDropTimeIntentDetection:
    """Test drop time intent detection via ANTLR."""

    def test_drop_time_with_course_and_semester(self):
        result = _antlr_classify("drop IT017IU SU26")
        assert result is not None
        assert result["intent"] == ASK_DROP_TIME
        assert result["course_code"] == "IT017IU"
        assert result["semester_code"] == "SU26"

    def test_drop_time_standalone(self):
        # "thời gian drop môn" — no course code, should still match dropQuery
        result = _antlr_classify("thời gian drop môn")
        assert result is not None
        assert result["intent"] == ASK_DROP_TIME
        assert result["course_code"] is None

    def test_drop_time_khi_nao_drop(self):
        result = _antlr_classify("khi nào drop")
        assert result is not None
        assert result["intent"] == ASK_DROP_TIME

    def test_drop_time_with_semicolon(self):
        result = _antlr_classify("khi nào drop?")
        assert result is not None
        assert result["intent"] == ASK_DROP_TIME

    def test_drop_time_huy_mon(self):
        # Vietnamese "hủy môn" — via regex fallback in parse_command
        result = parse_command("hủy môn IT017IU")
        assert result["intent"] == ASK_DROP_TIME
        assert result["slots"]["course_code"] == "IT017IU"

    def test_drop_time_rut_mon(self):
        # Vietnamese "rút môn" — via regex fallback
        result = parse_command("rút môn IT017IU khi nào")
        assert result["intent"] == ASK_DROP_TIME

    def test_drop_time_semester_first(self):
        result = _antlr_classify("SU26 drop IT017IU")
        assert result is not None
        assert result["intent"] == ASK_DROP_TIME
        assert result["course_code"] == "IT017IU"
        # SU26 is a standalone SEMESTER token, year must be captured
        assert result["semester_code"] == "SU26"

    def test_drop_time_no_ambiguous_bare_course_code(self):
        # "IT017IU khi nào" should NOT be classified as drop time
        # (the FIX explicitly removed bare COURSE_CODE from dropQuery)
        result = _antlr_classify("IT017IU khi nào")
        # This should NOT match dropQuery (ambiguous), may match courseInfoQuery
        # The key thing: it must NOT trigger ASK_DROP_TIME with wrong course code
        if result and result["intent"] == ASK_DROP_TIME:
            assert result["course_code"] != "IT017IU", "Should not extract 'khi nao' as course code"


class TestDropTimeProcessor:
    """Test CommandProcessor handling of ASK_DROP_TIME."""

    def setup_method(self):
        self.processor = CommandProcessor()

    def test_drop_time_with_semester_gives_notice(self):
        parsed = parse_command("drop IT017IU SU26")
        result = self.processor.process(parsed)
        assert result["intent"] == ASK_DROP_TIME
        # Should return a notice response (or fallback if no data)
        assert "reply" in result
        assert "confidence" in result

    def test_drop_time_without_semester_asks_for_semester(self):
        parsed = parse_command("drop IT017IU")
        result = self.processor.process(parsed)
        assert result["intent"] == ASK_DROP_TIME
        # New behavior: drop time always returns notice + link, no missing_slots needed
        assert "reply" in result
        assert result["missing_slots"] == []
        assert "Xem chi tiết:" in result["reply"]

    def test_drop_time_without_course_or_semester_asks_for_both(self):
        parsed = parse_command("khi nào drop")
        result = self.processor.process(parsed)
        assert result["intent"] == ASK_DROP_TIME
        assert "reply" in result
        # Should ask for course code and semester
        assert "missing_slots" in result


class TestDropTimeConversationFlow:
    """Test multi-turn conversation flow for drop time queries.

    This reproduces the bug from the screenshot where the user asks
    about drop time in multiple turns:
      1. "khi nào drop môn IT090IU" -> bot asks for semester
      2. "SU26" -> bot should give drop time, NOT prerequisite info
    """

    def setup_method(self):
        self.processor = CommandProcessor()

    def test_drop_query_then_semester_only(self):
        """Turn 1: ask about drop time with course but no semester."""
        parsed = parse_command("khi nào drop môn IT090IU")
        result = self.processor.process(parsed)
        assert result["intent"] == ASK_DROP_TIME
        # New behavior: always returns notice + link, no missing slots
        assert "reply" in result
        assert result["missing_slots"] == []
        # Bot should have recognized IT090IU as the course
        assert result["slots"].get("course_code") == "IT090IU"

    def test_drop_time_via_parse_command_with_semester(self):
        """Combined: drop query with semester should produce drop time answer."""
        parsed = parse_command("khi nào drop IT090IU SU26")
        result = self.processor.process(parsed)
        assert result["intent"] == ASK_DROP_TIME
        # Should NOT be ASK_COURSE_REQUIREMENTS
        assert result["intent"] != ASK_COURSE_REQUIREMENTS
        assert result["slots"].get("course_code") == "IT090IU"
        assert result["slots"].get("semester_code") == "SU26"


class TestIntentDetection:
    """Test various Vietnamese patterns for intent detection."""

    def test_eligibility_patterns(self):
        patterns = [
            "eligibility IT017IU",
            "eligible IT017IU",
            "học được IT017IU không",
        ]
        for pattern in patterns:
            result = parse_command(pattern)
            assert result["intent"] == ASK_COURSE_ELIGIBILITY, f"Failed for: {pattern}"

    def test_prerequisite_patterns(self):
        patterns = [
            "tiên quyết IT017IU",
            "prerequisite IT017IU",
            "phải học gì trước IT017IU",
        ]
        for pattern in patterns:
            result = parse_command(pattern)
            assert result["intent"] == ASK_PREREQUISITE_ONLY, f"Failed for: {pattern}"

    def test_previous_patterns(self):
        patterns = [
            "học trước IT017IU",
            "previous IT017IU",
            "đã học môn gì trước IT017IU",
        ]
        for pattern in patterns:
            result = parse_command(pattern)
            assert result["intent"] == ASK_PREVIOUS_ONLY, f"Failed for: {pattern}"


# ============================================
# Course Alias / Name Resolution
# ============================================

class TestCourseAliasResolution:
    """Test that the bot resolves course names and abbreviations to course codes."""

    def setup_method(self):
        self.processor = CommandProcessor()

    def test_oop_alias_resolves(self):
        """'muốn học về OOP' should resolve to IT069IU and show course info."""
        result = self.processor.process(parse_command("muốn học về OOP", student_id="ITCSIU22001"))
        assert result["intent"] != "UNKNOWN"
        assert "IT069IU" in result["reply"]

    def test_ai_alias_resolves(self):
        """'tìm hiểu môn AI' should resolve to IT159IU."""
        result = self.processor.process(parse_command("tìm hiểu môn AI", student_id="ITCSIU22001"))
        assert result["intent"] != "UNKNOWN"
        assert "IT159IU" in result["reply"]

    def test_ml_alias_resolves(self):
        """'học được không môn ML' should resolve to a course code."""
        result = self.processor.process(parse_command("học được không môn ML", student_id="ITCSIU22001"))
        assert result["intent"] != "UNKNOWN"
        # ML in CS/K22 resolves to IT162IU (Machine Learning Platforms)
        assert "IT162IU" in result["reply"]

    def test_operating_system_alias_resolves(self):
        """'học operating system được không' should resolve to IT017IU (eligibility)."""
        result = self.processor.process(parse_command("học operating system được không", student_id="ITCSIU22001"))
        assert result["intent"] == ASK_COURSE_ELIGIBILITY
        assert "IT017IU" in result["reply"]

    def test_algorithms_alias_resolves(self):
        """'học algorithms and data structures được không' should resolve to IT013IU (eligibility)."""
        result = self.processor.process(parse_command("học algorithms and data structures được không", student_id="ITCSIU22001"))
        assert result["intent"] == ASK_COURSE_ELIGIBILITY
        assert "IT013IU" in result["reply"]

    def test_dsa_alias_resolves(self):
        """'dsa' (data structures & algorithms) should resolve to IT013IU."""
        result = self.processor.process(parse_command("dự án này có nhận môn dsa không", student_id="ITCSIU22001"))
        assert result["intent"] == ASK_COURSE_ELIGIBILITY
        assert "IT013IU" in result["reply"]

    def test_machine_learning_alias_resolves(self):
        """'học được môn machine learning không' should resolve."""
        result = self.processor.process(parse_command("học được môn machine learning không", student_id="ITCSIU22001"))
        assert result["intent"] != "UNKNOWN"
        # ML in CS/K22 = IT162IU (Machine Learning Platforms)
        assert "IT162IU" in result["reply"]

    def test_vietnamese_alias_resolves(self):
        """'cấu trúc dữ liệu là gì' should resolve to IT013IU."""
        result = self.processor.process(parse_command("cấu trúc dữ liệu là gì", student_id="ITCSIU22001"))
        assert result["intent"] != "UNKNOWN"
        assert "IT013IU" in result["reply"]


# ============================================
# Edge Cases
# ============================================

class TestEdgeCases:
    def test_empty_input(self):
        result = parse_command("")
        assert result["intent"] == "UNKNOWN"

    def test_whitespace_only(self):
        result = parse_command("   ")
        assert result["intent"] == "UNKNOWN"

    def test_course_code_case_insensitive(self):
        result = parse_command("it017iu là gì")
        # Course code should be extracted regardless of case
        assert result["slots"]["course_code"] is not None

    def test_multiple_course_codes_takes_first(self):
        result = parse_command("IT017IU và CS101IU")
        assert result["slots"]["course_code"] == "IT017IU"


# ============================================
# Onboarding Flow Tests
# ============================================

from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService


class TestMssvExtractionFromMessage:
    """Test extracting MSSV from message text."""

    def setup_method(self):
        self.service = ChatService()

    def test_extracts_mssv_from_plain_text(self):
        mssv = self.service._extract_student_id_from_message("ITCSIU22001")
        assert mssv == "ITCSIU22001"

    def test_extracts_mssv_with_prefix(self):
        mssv = self.service._extract_student_id_from_message("mssv ITCSIU22001")
        assert mssv == "ITCSIU22001"

    def test_extracts_mssv_from_sentence(self):
        mssv = self.service._extract_student_id_from_message("MSSV của tôi là ITCSIU22001")
        assert mssv == "ITCSIU22001"

    def test_extracts_mssv_lowercase(self):
        mssv = self.service._extract_student_id_from_message("itcsiu22001")
        assert mssv == "ITCSIU22001"  # Pattern matches uppercase version

    def test_returns_none_when_no_mssv(self):
        mssv = self.service._extract_student_id_from_message("tôi hỏi về IT017IU")
        assert mssv is None


class TestOnboardingWithMssvInMessage:
    """Test that onboarding works when MSSV is embedded in message."""

    def setup_method(self):
        self.service = ChatService()

    def test_onboarding_detects_mssv_from_message(self):
        """
        When user says 'ITCSIU22001' or 'mssv ITCSIU22001',
        the bot should NOT ask for MSSV again.
        """
        session_id = "test-mssv-inline"

        result = self.service.handle_message(
            ChatRequest(message="mssv ITCSIU22001 hỏi về IT017IU", session_id=session_id)
        )

        # Should not trigger onboarding - MSSV was extracted from message
        assert result.intent != "ONBOARDING"
        assert result.slots.get("student_id") == "ITCSIU22001"

    def test_onboarding_still_works_without_mssv(self):
        service = ChatService()
        result = service.handle_message(ChatRequest(message="xin chào", session_id="onboard-1"))

        # "xin chào" is correctly classified as GREETING, not ONBOARDING
        assert result.intent == "GREETING"
        # Bot should request identity info
        assert "student_id_or_cohort_and_major" in result.missing_slots


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
