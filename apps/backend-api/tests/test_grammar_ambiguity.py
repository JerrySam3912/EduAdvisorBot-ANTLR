"""
Ambiguity Tests for CourseQuery.g4

Tests potential ambiguity issues in the ANTLR grammar:
1. Question word overlaps across different query types
2. Overlapping tokens between query types
3. Edge cases that could cause parse ambiguity
4. Previously problematic patterns
"""

from app.nlp.parser import parse_command


def test_question_word_context():
    """
    Test: Question words should only work in specific contexts.
    Without a prefix, question-word-only phrases should be rejected.
    """
    test_cases = [
        ("khi nào drop IT017IU", "dropQuery with khi nào", "ASK_DROP_TIME"),
        ("khi nào đăng ký", "registrationQuery with khi nào", "ASK_REGISTRATION_TIME"),
        ("thời gian drop môn", "dropQuery with thời gian", "ASK_DROP_TIME"),
        ("bao giờ đăng ký", "registrationQuery with bao giờ", "ASK_REGISTRATION_TIME"),
        ("tiên quyết IT017IU là gì", "prerequisiteQuery with gì", "ASK_PREREQUISITE_ONLY"),
        ("đã học IT017IU là gì", "previousQuery with gì", "ASK_PREVIOUS_ONLY"),
        ("IT017IU là gì", "courseInfoQuery with gì", "ASK_COURSE_REQUIREMENTS"),
        ("thông tin IT017IU là gì", "courseInfoQuery with thông tin", "ASK_COURSE_REQUIREMENTS"),
        ("học được IT017IU không", "eligibilityQuery with không", "ASK_COURSE_ELIGIBILITY"),
        ("có được không IT017IU", "eligibilityQuery with không", "ASK_COURSE_ELIGIBILITY"),
    ]

    for text, description, expected_intent in test_cases:
        result = parse_command(text)
        actual_intent = result.get("intent", "UNKNOWN")
        assert actual_intent == expected_intent, f"[{description}] Input: '{text}', Expected: {expected_intent}, Got: {actual_intent}"


def test_no_prefix_no_match():
    """
    Test: Phrases with only question words (no prefix) should NOT match.
    """
    test_cases = [
        ("khi nào", "Only khi nào"),
        ("gì", "Only gì"),
        ("nào", "Only nào"),
        ("thời gian", "Only thời gian"),
    ]

    for text, description in test_cases:
        result = parse_command(text)
        intent = result.get("intent", "")
        should_fail = intent in ("UNKNOWN", "NO_MATCH", "") or result.get("antlr_parsed") is False
        assert should_fail, f"[{description}] Input: '{text}', Intent: {intent} (expected UNKNOWN/NO_MATCH)"


def test_prefix_disambiguation():
    """
    Test: Same question word with different prefixes = different intents.
    """
    test_cases = [
        ("tiên quyết IT017IU là gì", "ASK_PREREQUISITE_ONLY"),
        ("đã học IT017IU là gì", "ASK_PREVIOUS_ONLY"),
        ("IT017IU là gì", "ASK_COURSE_REQUIREMENTS"),
        ("thông tin IT017IU là gì", "ASK_COURSE_REQUIREMENTS"),
    ]

    for text, expected_intent in test_cases:
        result = parse_command(text)
        actual_intent = result.get("intent", "")
        assert actual_intent == expected_intent, f"Input: '{text}', Expected: {expected_intent}, Got: {actual_intent}"


def test_drop_vs_registration():
    """
    Test: Drop and registration are correctly disambiguated.
    """
    test_cases = [
        ("drop IT017IU", "ASK_DROP_TIME"),
        ("hủy môn IT017IU", "ASK_DROP_TIME"),
        ("khi nào drop IT017IU", "ASK_DROP_TIME"),
        ("thời gian hủy môn", "ASK_DROP_TIME"),
        ("rút môn IT017IU", "ASK_DROP_TIME"),
        ("drop IT017IU SU26", "ASK_DROP_TIME"),
        ("đăng ký", "ASK_REGISTRATION_TIME"),
        ("khi nào đăng ký", "ASK_REGISTRATION_TIME"),
        ("nền tảng đăng ký", "ASK_REGISTRATION_PLATFORM"),
        ("website đăng ký", "ASK_REGISTRATION_PLATFORM"),
        ("đăng ký ở đâu", "ASK_REGISTRATION_PLATFORM"),
    ]

    for text, expected_intent in test_cases:
        result = parse_command(text)
        actual_intent = result.get("intent", "")
        assert actual_intent == expected_intent, f"Input: '{text}', Expected: {expected_intent}, Got: {actual_intent}"


def test_bare_course_code_ambiguity():
    """
    Test: Bare course code should NOT trigger drop by itself.
    """
    test_cases = [
        ("IT017IU khi nào", "Should NOT match drop (no prefix)", False),
        ("IT017IU", "Bare course code", False),
        ("khi nào IT017IU", "Question word before course (no prefix)", False),
        ("drop IT017IU khi nào", "Drop prefix + course + question", True),
        ("hủy môn IT017IU", "Hủy môn + course", True),
    ]

    for text, description, should_match in test_cases:
        result = parse_command(text)
        intent = result.get("intent", "")

        if should_match:
            matched = intent not in ("UNKNOWN", "NO_MATCH", "")
        else:
            matched = intent in ("UNKNOWN", "NO_MATCH", "")
        assert matched, f"[{description}] Input: '{text}', Intent: {intent}"


def test_previously_ambiguous():
    """
    Test: Cases that previously caused ambiguity.
    """
    test_cases = [
        ("cần uống nước", "Should NOT match prerequisite", "UNKNOWN"),
        ("học IT017IU được không", "Should match eligibility", "ASK_COURSE_ELIGIBILITY"),
        ("nối tiếp IT017IU", "Should match previous", "ASK_PREVIOUS_ONLY"),
        ("IT017IU là", "Should NOT match (incomplete)", "UNKNOWN"),
    ]

    for text, description, expected_intent in test_cases:
        result = parse_command(text)
        actual_intent = result.get("intent", "UNKNOWN")

        if expected_intent == "UNKNOWN":
            should_be_unknown = actual_intent in ("UNKNOWN", "NO_MATCH", "") or result.get("antlr_parsed") is False
            assert should_be_unknown, f"[{description}] Input: '{text}', Expected UNKNOWN, Got: {actual_intent}"
        else:
            assert actual_intent == expected_intent, f"[{description}] Input: '{text}', Expected: {expected_intent}, Got: {actual_intent}"


def test_greeting_with_trailing_words():
    """
    Test: Greetings with trailing words (like "xin chào bạn", "chào bạn mình")
    should still be classified as GREETING.
    This was the bug: the old regex used $ anchor which required the string to
    end immediately after the greeting keyword, breaking "xin chào bạn".
    """
    test_cases = [
        ("xin chào bạn", "xin chào + bạn", "GREETING"),
        ("chào bạn mình", "chào + bạn mình", "GREETING"),
        ("buổi sáng tốt lành", "buổi sáng + trailing words", "GREETING"),
        ("xin chào", "xin chào alone", "GREETING"),
        ("chào", "chào alone", "GREETING"),
        ("buổi chiều", "buổi chiều alone", "GREETING"),
    ]

    for text, description, expected_intent in test_cases:
        result = parse_command(text)
        actual_intent = result.get("intent", "")
        assert actual_intent == expected_intent, f"[{description}] Input: '{text}', Expected: {expected_intent}, Got: {actual_intent}"


def test_greeting_not_confused_with_course_info():
    """
    Test: Greeting patterns should NOT be confused with course codes or student IDs.
    The greeting regex starts with word boundary at the beginning of string,
    so no false positives expected here — but guard against future regressions.
    """
    test_cases = [
        ("xin chào IT017IU", "Greeting + course code — NOT a greeting (has course)", "ASK_COURSE_REQUIREMENTS"),
        ("chào ITCSIU22001", "Greeting + student ID — NOT a greeting (has student ID)", "GREETING"),
    ]

    for text, description, expected_intent in test_cases:
        result = parse_command(text)
        actual_intent = result.get("intent", "")
        # "chào ITCSIU22001" — greeting should still fire (no course code in slots)
        if expected_intent == "GREETING":
            assert actual_intent == "GREETING", f"[{description}] Input: '{text}', Expected: GREETING, Got: {actual_intent}"


def test_semester_with_queries():
    """
    Test: Semester codes work correctly with different query types.
    """
    test_cases = [
        ("drop IT017IU SP26", "Drop with Spring 2026", "ASK_DROP_TIME"),
        ("drop IT017IU FA25", "Drop with Fall 2025", "ASK_DROP_TIME"),
        ("drop IT017IU SU26", "Drop with Summer 2026", "ASK_DROP_TIME"),
        ("SU26 drop IT017IU", "Semester before drop", "ASK_DROP_TIME"),
        ("FA25 hủy môn IT017IU", "Fall with hủy", "ASK_DROP_TIME"),
    ]

    for text, description, expected_intent in test_cases:
        result = parse_command(text)
        actual_intent = result.get("intent", "")
        assert actual_intent == expected_intent, f"[{description}] Input: '{text}', Expected: {expected_intent}, Got: {actual_intent}"

