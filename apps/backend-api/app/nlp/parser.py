import re

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from app.generated.CourseQueryLexer import CourseQueryLexer
from app.generated.CourseQueryParser import CourseQueryParser
from app.nlp.antlr_visitor import IntentSlotExtractor
from app.nlp.language_detection import detect_non_vietnamese


# Semester patterns: covers SP26, SU26, SUMMER26, FA26, hè 2026, HKIII, hoc ky he, etc.
# CRITICAL: longer terms MUST come before shorter prefixes (hoc ky he before hoc ky, summer before sum)
SEMESTER_PATTERN = re.compile(
    r"(?<!\w)(?P<term>mùa hè|mua hè|hoc ky he|hkiii|hocky iii|summer|spring|fall|hoc ky|hocky|"
    r"sp|spr|su|sum|fa|fal|hè|"
    r"SPRING|SUMMER|FALL|SUM|FA|SP|SU|HK|HOCKY|HKIII|HÈ|MÙA HÈ|MUA HÈ)"
    r"\s*[-_]?\s*(?P<year>\d{4}|\d{2}|[ivxlc]+)\b",
    flags=re.IGNORECASE
)
COHORT_PATTERN = re.compile(r"\b(k(?:hoa)?\s*)?(\d{2})\b", flags=re.IGNORECASE)
# Student ID patterns for IU students
# Examples: ITCSIU22001, ITDSIU23109, ITCEIU24001, ITITWE22009
STUDENT_ID_PATTERN = re.compile(r'\b([A-Z]{2}[A-Z]{2,6}?\d{5})\b')
STUDENT_ID_SHORT_PATTERN = re.compile(r'\b(?P<prefix>IT)(?P<major>[A-Z]{2,4})?(?:IU)?(?P<cohort>\d{2})(?P<suffix>\d{3,4})\b', flags=re.IGNORECASE)
COURSE_CODE_PATTERN = re.compile(r"\b([A-Z]{2,4}\d{3}(?:IU)?)\b", flags=re.IGNORECASE)


class _SilentErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        return


def normalize_text(user_text: str) -> str:
    return user_text.strip().lower()


def extract_semester_code(text: str) -> str | None:
    """
    Extract semester code from text.
    Handles: SP26, SU26, SUM26, SUMMER26, FA26, FA2026, hè 2026, mùa hè 2026, spring 2026, etc.
    Also handles standalone: hè -> SU26 (current summer), mùa hè -> SU26
    Returns: SP26, SU26, FA26 format (TERM + 2-digit year)
    """
    match = SEMESTER_PATTERN.search(text)
    if not match:
        # Fallback: standalone "mùa hè" or "hè" (no year) — default to next summer (SU26)
        standalone = re.search(
            r"(?<!\w)(mùa hè|mua hè|hè|hè\s*$)\b",
            text, flags=re.IGNORECASE
        )
        if standalone:
            return "SU26"
        return None
    term_raw = match.group("term").lower().strip()
    year_raw = match.group("year")

    # Normalize term to 2-letter code
    # STANDALONE 'hè' or 'mùa hè' (no year) defaults to next summer
    term_map = {
        "sp": "SP", "spr": "SP", "spring": "SP",
        "su": "SU", "sum": "SU", "summer": "SU",
        "fa": "FA", "fal": "FA", "fall": "FA",
        "hè": "SU",
        "mùa hè": "SU", "mua hè": "SU",
        "hoc ky he": "HK",  # học kỳ hè / summer semester
        "hoc ky": "HK", "hocky": "HK", "hk": "HK",
        "hkiii": "HKIII", "hocky iii": "HKIII",
    }
    term = term_map.get(term_raw)
    if not term:
        return None

    # Normalize year to 2 digits (or preserve roman numerals like III, II)
    if year_raw is None:
        return None
    year_lower = year_raw.lower()
    # Preserve roman numerals (hocky III -> HKIII)
    if year_lower in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"):
        return f"{term}{year_raw.upper()}"
    year = year_raw[-2:]  # "2026" -> "26"
    return f"{term}{year}"


def extract_explicit_cohort(text: str) -> str | None:
    match = COHORT_PATTERN.search(text)
    if not match:
        return None
    return f"k{match.group(2)}"


def extract_major_from_student_id(student_id: str | None) -> str | None:
    """
    Extract major from student ID.
    Examples:
    - ITCSIU22001 -> cs
    - ITDSIU23109 -> ds
    - ITCEIU24001 -> ce
    - ITITWE22009 -> it (or itwe depending on program)
    """
    if not student_id:
        return None
    normalized = student_id.strip().upper()

    # Known major prefixes
    major_patterns = [
        (r'ITCSIU', 'cs'),
        (r'ITDSIU', 'ds'),
        (r'ITCEIU', 'ce'),
        (r'ITNEIU', 'ne'),
        (r'ITITIU', 'it'),
        (r'ITITWE', 'it'),
        (r'ITITCS', 'it'),
    ]

    for pattern, major in major_patterns:
        if pattern in normalized:
            return major

    # Fallback: try to extract 2-letter major
    match = re.match(r'IT([A-Z]{2})', normalized)
    if match:
        return match.group(1).lower()

    return None


def infer_cohort_from_student_id(student_id: str | None) -> str | None:
    """
    Extract cohort from student ID.
    Examples:
    - ITCSIU22001 -> k22
    - ITDSIU23109 -> k23
    - ITCEIU24001 -> k24
    """
    if not student_id:
        return None
    normalized = student_id.strip().upper()

    # Try short pattern first
    match = STUDENT_ID_SHORT_PATTERN.search(normalized)
    if match and match.group("cohort"):
        return f"k{match.group('cohort')}"

    # Fallback: look for 2-digit number
    match = re.search(r'\d{5}', normalized)
    if match:
        cohort_num = match.group(0)[:2]
        return f"k{cohort_num}"

    # Handle 7-digit student IDs (e.g. 2401036)
    # First 2 digits = year prefix (24 → k24)
    match = re.match(r'^(\d{2})\d{5}$', normalized)
    if match:
        return f"k{match.group(1)}"

    return None


def extract_course_code(text: str) -> str | None:
    """
    Extract course code from text.
    Course codes: 2-4 letters + 3 digits + optional IU (e.g., IT017IU, IT069IU, PE019)
    Student IDs: 2+ letters + IU + 5 digits (e.g., ITCSIU22001, ITCEIU24001)
    If the "3 digits" are followed by MORE digits, it's a student ID → skip.
    """
    match = COURSE_CODE_PATTERN.search(text.upper())
    if not match:
        return None
    code = match.group(1).upper()
    # Count total consecutive digits in the original text starting from the match
    start = match.start()
    remaining = text.upper()[start:]
    digit_count = 0
    for ch in remaining:
        if ch.isdigit():
            digit_count += 1
        else:
            break
    # If we matched more than 3 consecutive digits, it's a student ID
    if digit_count > 3:
        return None
    return code


def _antlr_classify(user_text: str) -> dict | None:
    """
    Use ANTLR to classify intent and extract course code from parse tree.
    Returns dict with 'intent' and 'course_code' if parse succeeds, None otherwise.
    """
    try:
        input_stream = InputStream(user_text)
        lexer = CourseQueryLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(_SilentErrorListener())

        token_stream = CommonTokenStream(lexer)
        parser = CourseQueryParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(_SilentErrorListener())

        tree = parser.query()

        extractor = IntentSlotExtractor()
        result = extractor.extract(tree, raw_text=user_text)
        return result
    except Exception:
        return None


def classify_intent(text: str, last_course_code: str | None = None) -> str:
    """
    Classify intent using regex-based classification.
    Handles Vietnamese queries that ANTLR (English-only grammar) cannot parse.
    Conservative patterns — require course code where ambiguous.
    Supports session memory: 'last_course_code' from previous turns.
    """
    lower = text.lower()
    extracted_course = extract_course_code(lower)
    has_course = extracted_course is not None or last_course_code is not None

    # --- DROP TIME ---
    # "hủy môn", "hiệu chỉnh môn", "rút môn" = DROP_TIME (unambiguous)
    # "drop", "withdraw" + time_words OR course code = DROP_TIME
    drop_standalone = r"(hủy môn|hiệu chỉnh môn|rút môn|bỏ môn|loại bỏ môn)"
    drop_need_context = r"(drop|withdraw|cancel)"
    time_words = r"(khi nào|thời gian|thời điểm|bao giờ|lúc nào|ngày nào|mấy|tháng nào|năm nào)"
    if re.search(drop_standalone, lower):
        return "ASK_DROP_TIME"
    if re.search(drop_need_context, lower):
        if re.search(time_words, lower) or re.search(r"\?", lower) or has_course:
            return "ASK_DROP_TIME"

    # --- REGISTRATION ---
    reg_keywords = r"(đăng ký|dang ky|registration|register|enroll)"
    platform_words = r"(website|web|cổng|nền tảng|portal|nơi|chỗ|đâu|ở đâu|platform)"
    time_reg_words = r"(khi nào|thời gian|thời điểm|bao giờ|lúc nào|mấy|\?)"

    if re.search(reg_keywords, lower):
        if re.search(platform_words, lower):
            return "ASK_REGISTRATION_PLATFORM"
        if re.search(time_reg_words, lower) or re.search(r"(\?|\S+\s+\?)$", lower.strip()):
            return "ASK_REGISTRATION_TIME"
        # Bare "đăng ký" or "registration" alone
        if re.match(r"^\s*(" + reg_keywords.replace(r"(", r"(?:") + r")\s*$", lower):
            return "ASK_REGISTRATION_TIME"

    # --- ELIGIBILITY ---
    # Requires course code to avoid false positives
    elig_keywords = r"(học được không|học được|được học|có thể học|có được không|eligible|eligibility|can take|can i take|take this|take it|học về|muốn học|tìm hiểu môn|learn about|tell me about|what is|what's about|học.*được không)"
    if has_course and re.search(elig_keywords, lower):
        return "ASK_COURSE_ELIGIBILITY"

    # --- PREREQUISITE ---
    prereq_keywords = r"(tiên quyết|prerequisite|prerequisites|must pass|need to pass|cần pass|can pass|phải pass|bắt buộc|phải học gì trước|cần học trước)"
    if has_course and re.search(prereq_keywords, lower):
        return "ASK_PREREQUISITE_ONLY"

    # --- PREVIOUS ---
    prev_keywords = r"(đã học|học rồi|previous|prev|học trước|cần học gì trước|nối tiếp)"
    if has_course and re.search(prev_keywords, lower):
        return "ASK_PREVIOUS_ONLY"

    # --- COURSE INFO ---
    info_keywords = r"(thông tin|chi tiết|info|information|là môn gì|là gì|môn gì|giới thiệu môn|tư vấn|tra)"
    if has_course and re.search(info_keywords, lower):
        return "ASK_COURSE_REQUIREMENTS"

    # --- GREETING ---
    # Match greeting keyword at the START of the string. Allow optional trailing words
    # (e.g. "xin chào bạn", "chào bạn mình") by requiring whitespace before any additional
    # content — prevents matching course codes or student info embedded without spacing.
    # (?:\s+|$) means: at least one whitespace, OR end of string.
    greeting_keywords = r"(xin chào|chào|buổi sáng|buổi chiều)"
    if re.match(r"^\s*" + greeting_keywords + r"(?:\s+|$)", lower):
        return "GREETING"

    # --- HELP ---
    help_keywords = r"(help|gợi ý|trợ giúp|hướng dẫn|bạn là ai|bạn có thể làm gì)"
    if re.search(help_keywords, lower):
        return "HELP"

    return "UNKNOWN"


def parse_command(user_text: str, student_id: str | None = None, last_course_code: str | None = None) -> dict:
    """
    Parse user command and extract intent, slots.

    Pipeline:
    1. Language detection - check for non-Vietnamese
    2. ANTLR parse -> extract intent + course_code (if available)
    3. Regex fallback for slots (semester, cohort, etc.)
    4. Merge results
    """
    normalized = normalize_text(user_text)

    # Check for non-Vietnamese language (language drift prevention)
    lang_check = detect_non_vietnamese(user_text)

    antlr_result = _antlr_classify(user_text)

    explicit_cohort = extract_explicit_cohort(normalized)
    inferred_cohort = infer_cohort_from_student_id(student_id)
    inferred_major = extract_major_from_student_id(student_id)

    course_code = antlr_result.get("course_code") if antlr_result else None
    if not course_code:
        course_code = extract_course_code(normalized)

    # Get semester from ANTLR visitor first, then fall back to regex
    antlr_semester = antlr_result.get("semester_code") if antlr_result else None
    semester_code = antlr_semester or extract_semester_code(normalized)

    # Get intent: try ANTLR first, fall back to regex
    antlr_intent = antlr_result.get("intent") if antlr_result else None
    known_intents = {"ASK_COURSE_ELIGIBILITY", "ASK_COURSE_REQUIREMENTS", "ASK_PREREQUISITE_ONLY",
                     "ASK_PREVIOUS_ONLY", "ASK_REGISTRATION_TIME", "ASK_DROP_TIME",
                     "ASK_REGISTRATION_PLATFORM", "HELP", "GREETING", "IDENTITY_ACKNOWLEDGED"}
    if antlr_intent and antlr_intent in known_intents:
        intent = antlr_intent
    else:
        # Always try regex fallback for Vietnamese patterns ANTLR can't handle
        # Pass last_course_code for session memory (pronoun resolution)
        intent = classify_intent(normalized, last_course_code=last_course_code)

    # Handle language drift
    language_warning = None
    if not lang_check["is_vietnamese"]:
        language_warning = lang_check["warning"]
        intent = "LANGUAGE_DRIFT"

    return {
        "raw_text": user_text,
        "normalized_text": normalized,
        "intent": intent,
        "antlr_parsed": antlr_result is not None,
        "language_detected": lang_check["detected_language"],
        "language_warning": language_warning,
        "slots": {
            "semester_code": semester_code,
            "cohort": explicit_cohort or inferred_cohort,
            "cohort_from_text": explicit_cohort,
            "cohort_from_student_id": inferred_cohort,
            "major_from_student_id": inferred_major,
            "student_id": student_id,
            "course_code": course_code,
        },
    }
