import re

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from app.generated.CourseQueryLexer import CourseQueryLexer
from app.generated.CourseQueryParser import CourseQueryParser


SEMESTER_PATTERN = re.compile(r"\b(sp|su|fa)\s*[-_/]?\s*(\d{2})\b", flags=re.IGNORECASE)
COHORT_PATTERN = re.compile(r"\b(k(?:hoa)?\s*)?(\d{2})\b", flags=re.IGNORECASE)
STUDENT_ID_COHORT_PATTERN = re.compile(r"^[A-Z]{4,8}(\d{2})\d{3,4}$")
COURSE_CODE_PATTERN = re.compile(r"\b([A-Z]{2,4}\d{3}(?:IU)?)\b", flags=re.IGNORECASE)

COURSE_REQUIREMENT_PATTERNS = (
    r"(cần|need|needs|phải|prerequisite|tiên quyết|trước|before)",
    r"(học gì|need to study|study before|môn nào|what course|which course)",
)
ELIGIBILITY_PATTERNS = (
    r"(ổn không|ok không|được không|eligible|eligibility|học được không|take this semester|semester này|có ổn không)",
    r"(can i|can I|is it ok|am I eligible|có được không|học OOP sem 2|sem 2 này)",
)
REGISTRATION_TIME_PATTERNS = (
    r"(đăng ký|registration|register|enroll|adjust|điều chỉnh)",
    r"(khi nào|when|thời gian|time)",
)
DROP_TIME_PATTERNS = (
    r"(drop|hủy|huy|rút|withdraw)",
    r"(khi nào|when|thời gian|time)",
)
REGISTRATION_PLATFORM_PATTERNS = (
    r"(website|web|cổng|portal|nền tảng|platform|làm ở đâu|where|đâu)",
    r"(đăng ký|registration|register|enroll)",
)
INSTRUCTOR_PATTERNS = (
    r"(giảng viên|instructor|lecturer|teacher|phụ trách|advisor|ai dạy|ai day|dạy)",
    r"(môn|course|subject|course code)",
)


class _SilentErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        return


def normalize_text(user_text: str) -> str:
    return user_text.strip().lower()


def extract_semester_code(text: str) -> str | None:
    match = SEMESTER_PATTERN.search(text)
    if not match:
        return None
    term, year = match.groups()
    return f"{term.upper()}{year}"


def extract_explicit_cohort(text: str) -> str | None:
    match = COHORT_PATTERN.search(text)
    if not match:
        return None
    return f"k{match.group(2)}"


def infer_cohort_from_student_id(student_id: str | None) -> str | None:
    if not student_id:
        return None
    normalized = student_id.strip().upper()
    match = STUDENT_ID_COHORT_PATTERN.match(normalized)
    if not match:
        return None
    return f"k{match.group(1)}"


def extract_course_code(text: str) -> str | None:
    match = COURSE_CODE_PATTERN.search(text.upper())
    if not match:
        return None
    return match.group(1).upper()


def classify_intent(text: str) -> str:
    lower = text.lower()
    if any(re.search(p, lower) for p in DROP_TIME_PATTERNS):
        return "ASK_DROP_TIME"
    if any(re.search(p, lower) for p in REGISTRATION_PLATFORM_PATTERNS):
        return "ASK_REGISTRATION_PLATFORM"
    if any(re.search(p, lower) for p in REGISTRATION_TIME_PATTERNS):
        return "ASK_REGISTRATION_TIME"
    if any(re.search(p, lower) for p in INSTRUCTOR_PATTERNS):
        return "ASK_INSTRUCTOR"
    if any(re.search(p, lower) for p in ELIGIBILITY_PATTERNS):
        return "ASK_COURSE_ELIGIBILITY"
    if any(re.search(p, lower) for p in COURSE_REQUIREMENT_PATTERNS):
        return "ASK_COURSE_REQUIREMENTS"
    return "UNKNOWN"


def _antlr_parse(text: str) -> bool:
    input_stream = InputStream(text)
    lexer = CourseQueryLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(_SilentErrorListener())

    token_stream = CommonTokenStream(lexer)
    parser = CourseQueryParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(_SilentErrorListener())
    parser.query()
    return True


def parse_command(user_text: str, student_id: str | None = None) -> dict:
    normalized = normalize_text(user_text)
    explicit_cohort = extract_explicit_cohort(normalized)
    inferred_cohort = infer_cohort_from_student_id(student_id)
    course_code = extract_course_code(normalized)

    antlr_ok = False
    try:
        antlr_ok = _antlr_parse(normalized)
    except Exception:
        antlr_ok = False

    return {
        "raw_text": user_text,
        "normalized_text": normalized,
        "intent": classify_intent(normalized),
        "antlr": antlr_ok,
        "slots": {
            "semester_code": extract_semester_code(normalized),
            "cohort": explicit_cohort or inferred_cohort,
            "cohort_from_text": explicit_cohort,
            "cohort_from_student_id": inferred_cohort,
            "student_id": student_id,
            "course_code": course_code,
        },
    }
