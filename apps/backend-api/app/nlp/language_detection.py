"""
Language detection module to prevent language drift.
This chatbot is designed for Vietnamese users.
Detects when user switches to non-Vietnamese languages (especially Chinese).
"""
import re
import logging

logger = logging.getLogger(__name__)

# Chinese characters pattern
CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]+')

# Vietnamese-specific diacritics
VIETNAMESE_DIACRITICS = 'ăâđêôơưàảãạằẳẵắặầẩẫậấờởỡợèẻẽẹéềểễệìỉĩịòỏõọóồổỗộờởỡớợùủũụúừửữứỳỷỹỵ'

# Non-Vietnamese markers organized by type
_CHINESE_CHARS_MARKERS = ['你', '好', '吗', '我吗']
_PINYIN_MARKERS = ['nihao', 'nima', 'nahao', 'woshu']  # distinct pinyin, not common Vietnamese
_NON_VIETNAMESE_OTHER = ['kamu', 'siapa', 'was', 'ist']  # Malay, German

# English words that might indicate user is not Vietnamese
ENGLISH_ONLY_MARKERS = [
    'what is the prerequisite of',
    'how do i register',
    'when can i drop',
    'can i take this course if',
    'do i need to pass',
]


def detect_non_vietnamese(text: str) -> dict:
    """
    Detect if the text contains non-Vietnamese language patterns.

    Returns:
        dict with 'is_vietnamese': bool and 'detected_language': str
    """
    result = {
        "is_vietnamese": True,
        "detected_language": None,
        "confidence": 1.0,
        "warning": None,
    }

    text_lower = text.lower().strip()

    # Check for Chinese characters
    if CHINESE_PATTERN.search(text):
        result["is_vietnamese"] = False
        result["detected_language"] = "chinese"
        result["confidence"] = 0.95
        result["warning"] = "Phát hiện ký tự Trung Quốc. Chatbot hỗ trợ tiếng Việt."
        return result

    # Check for Chinese pinyin — require at least 2 from either group
    chinese_chars_count = sum(1 for m in _CHINESE_CHARS_MARKERS if m in text_lower)
    pinyin_count = sum(1 for m in _PINYIN_MARKERS if m in text_lower)
    if chinese_chars_count + pinyin_count >= 2:
        result["is_vietnamese"] = False
        result["detected_language"] = "chinese"
        result["confidence"] = 0.7
        result["warning"] = "Có vẻ như bạn đang dùng tiếng Trung. Chatbot hỗ trợ tiếng Việt."
        return result

    # Check for English-only patterns (context matters - English mixed with Vietnamese is OK)
    for pattern in ENGLISH_ONLY_MARKERS:
        if pattern in text_lower:
            # Check if there's Vietnamese mixed in
            has_vietnamese = any(c in text_lower for c in VIETNAMESE_DIACRITICS)
            if not has_vietnamese:
                result["is_vietnamese"] = False
                result["detected_language"] = "english"
                result["confidence"] = 0.6
                result["warning"] = "Bạn có thể hỏi bằng tiếng Việt không?"
                return result

    return result


def filter_vietnamese_intent(text: str, detected_intent: str) -> tuple[str, float]:
    """
    Adjust intent confidence based on language detection.

    If language doesn't match, reduce confidence and suggest correction.
    """
    lang_check = detect_non_vietnamese(text)

    if not lang_check["is_vietnamese"]:
        return lang_check["warning"], lang_check["confidence"]

    return None, 1.0


def get_language_warning(text: str) -> str | None:
    """Get warning message if non-Vietnamese language detected."""
    result = detect_non_vietnamese(text)
    return result["warning"]


def validate_response_language(reply: str) -> dict:
    """
    Scan a bot response for non-Vietnamese language artifacts.
    This is a defensive output guard — if Chinese slips through the pipeline,
    this will catch it before it reaches the user.

    Returns a dict with:
      - is_valid: bool — True if response is safe (Vietnamese)
      - detected_language: str | None
      - sanitized: str | None — safe replacement if original was bad

    The sanitized reply uses a safe fallback to ensure the user always
    receives a Vietnamese response even if the backend generates garbage.
    """
    lang_check = detect_non_vietnamese(reply)

    if lang_check["is_vietnamese"]:
        return {
            "is_valid": True,
            "detected_language": None,
            "sanitized": None,
        }

    detected = lang_check["detected_language"] or "unknown"
    logger.warning(
        "OUTPUT LANGUAGE DRIFT detected! "
        "Bot response contained non-Vietnamese language (%s). "
        "Original reply (first 100 chars): %r",
        detected,
        reply[:100],
    )

    return {
        "is_valid": False,
        "detected_language": detected,
        "sanitized": (
            "Xin lỗi, mình gặp sự cố kỹ thuật. "
            "Bạn hỏi lại bằng tiếng Việt giúp mình nhé!"
        ),
    }
