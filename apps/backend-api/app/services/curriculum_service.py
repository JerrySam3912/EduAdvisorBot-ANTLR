from __future__ import annotations

import re
from functools import lru_cache

from app.repositories.academic_repository import AcademicRepository


# Course code pattern: 2-4 letters + 3 digits + optional IU
# Examples: IT017IU, CS101, PE019, NE012
COURSE_CODE_PATTERN = re.compile(r"\b([A-Z]{2,4}\d{3}(?:IU)?)\b", flags=re.IGNORECASE)

# Strict pattern for known prefixes to avoid false matches like "TT06" -> "IT06"
KNOWN_COURSE_PREFIXES = ["IT", "CS", "NE", "DS", "PE", "MA", "ITCE", "ITIT", "ITDS", "ITNE", "ITCS"]
COURSE_CODE_STRICT_PATTERN = re.compile(
    r"\b(" + "|".join(KNOWN_COURSE_PREFIXES) + r"\d{3}(?:IU)?)\b",
    flags=re.IGNORECASE
)
# Exact word boundaries for precise matching
COURSE_ALIAS_MAP = {
    # English names (canonical)
    "object-oriented programming": "Object-Oriented Programming",
    "object oriented programming": "Object-Oriented Programming",
    "oop": "Object-Oriented Programming",
    "oop course": "Object-Oriented Programming",
    "programming oop": "Object-Oriented Programming",
    "artificial intelligence": "Artificial Intelligence",
    "ai course": "Artificial Intelligence",
    "ai": "Artificial Intelligence",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "web dev": "Web Application Development",
    "web application": "Web Application Development",
    "web development": "Web Application Development",
    "principles of database management": "Principles of Database Management",
    "database": "Principles of Database Management",
    "db": "Principles of Database Management",
    "data mining": "Data Mining",
    "operating systems": "Operating System",
    "operating system": "Operating System",
    "os": "Operating System",
    "computer network": "Computer Networks",
    "computer networks": "Computer Networks",
    "cn": "Computer Networks",
    "net-centric programming": "Net-centric Programming",
    "net centric programming": "Net-centric Programming",
    "project management": "IT Project Management",
    "software engineering": "Software Engineering",
    "se": "Software Engineering",
    "computer graphics": "Computer Graphics",
    "cg": "Computer Graphics",
    "mobile app": "Mobile Application Development",
    "mobile development": "Mobile Application Development",
    "internet of things": "Internet of Things",
    "iot": "Internet of Things",
    "deep learning": "Deep Learning",
    "blockchain": "Blockchain",
    "devops": "Development & Operation",
    "algorithms and data structures": "Algorithms and Data Structures",
    "algorithm": "Algorithms and Data Structures",
    "algorithms": "Algorithms and Data Structures",
    "data structures": "Algorithms and Data Structures",
    "ads": "Algorithms and Data Structures",
    "dsa": "Algorithms and Data Structures",
    "discrete math": "Discrete Mathematics",
    "discrete mathematics": "Discrete Mathematics",
    "calculus": "Calculus 1",
    "physics": "Physics 1",
    "entrepreneurship": "Entrepreneurship",
    # Vietnamese names (canonical, matching curriculum exactly)
    "trí tuệ nhân tạo": "Artificial Intelligence",
    "ttnt": "Artificial Intelligence",
    "học máy": "Machine Learning",
    "khai phá dữ liệu": "Data Mining",
    "hệ điều hành": "Operating System",
    "mạng máy tính": "Computer Networks",
    "lập trình mạng": "Net-centric Programming",
    "quản lý dự án": "IT Project Management",
    "công nghệ phần mềm": "Software Engineering",
    "đồ họa máy tính": "Computer Graphics",
    "ứng dụng di động": "Mobile Application Development",
    "iot": "Internet of Things",
    "internet vạn vật": "Internet of Things",
    "học sâu": "Deep Learning",
    "blockchain": "Blockchain",
    "hcm thoughts": "Ho Chi Minh's Thoughts",
    "tư tưởng hồ chí minh": "Ho Chi Minh's Thoughts",
    "triết học mác lênin": "Philosophy Marx – Lenin",
    "triết": "Philosophy Marx – Lenin",
    "kinh tế chính trị": "Marxist – Leninist Political Economy",
    "chủ nghĩa xã hội": "Scientific Socialism",
    "lịch sử đảng": "History of Vietnamese Communist Party",
    "tư tưởng hồ chí minh": "Ho Chi Minh's Thoughts",
    "giải tích": "Calculus 1",
    "vật lý": "Physics 1",
    "xác suất thống kê": "Probability, Statistic & Random Process",
    "xác suất": "Probability, Statistic & Random Process",
    "toán rời rạc": "Discrete Mathematics",
    "cấu trúc dữ liệu": "Algorithms and Data Structures",
    "giải thuật": "Algorithms and Data Structures",
    "lập trình c": "C/C++ Programming",
    "lập trình c cộng cộng": "C/C++ Programming",
    "c cộng cộng": "C/C++ Programming",
    "kiến trúc máy tính": "Computer Architecture",
    "thiết kế số": "Digital Logic Design",
    "kỹ thuật số": "Digital Logic Design",
    "logic số": "Digital Logic Design",
    "khởi nghiệp": "Entrepreneurship",
    "quản trị hệ thống thông tin": "Information System Management",
    "hệ thống thông tin": "Information System Management",
    "lập trình hướng đối tượng": "Object-Oriented Programming",
    "lập trình java": "Object-Oriented Programming",
    # Common abbreviations
    "15m": "Machine Learning",
    "ml": "Machine Learning",
    "3d": "Computer Graphics",
}


class CurriculumService:
    def __init__(self):
        self.repository = AcademicRepository()

    @staticmethod
    def extract_course_code(text: str) -> str | None:
        """
        Extract course code from text.
        Uses strict pattern to avoid false matches like "TT0691U" -> "IT06".
        """
        # Try strict pattern first (known prefixes)
        match = COURSE_CODE_STRICT_PATTERN.search(text.upper())
        if match:
            return match.group(1).upper()

        # Fallback to general pattern
        match = COURSE_CODE_PATTERN.search(text.upper())
        if not match:
            return None
        code = match.group(1).upper()
        # Validate: must have 2-4 letters followed by exactly 3 digits
        if not re.match(r"^[A-Z]{2,4}\d{3}(?:IU)?$", code):
            return None
        return code

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    @staticmethod
    def _contains_exact_phrase(text: str, phrase: str) -> bool:
        # Match phrase as a whole word/phrase surrounded by spaces or string boundaries.
        # Do NOT use \w word boundaries — \w matches Unicode letters including
        # Vietnamese characters, which breaks alias matching for short terms like "ai"
        # (e.g. "môn ai" would not match "ai" because "n" is a \w char).
        # Instead, match: space before/after, or string start/end.
        pattern = r"(?<![^\s])" + re.escape(phrase) + r"(?![^\s])"
        return re.search(pattern, text, flags=re.IGNORECASE) is not None

    @lru_cache(maxsize=256)
    def get_curriculum(self, major: str, cohort: str) -> dict:
        return self.repository.load_curriculum(major, cohort)

    def resolve_course_by_name(self, major: str, cohort: str, user_text: str) -> dict | None:
        normalized_text = self._normalize_text(user_text)

        # Try the specified major first
        result = self._resolve_in_major(major, cohort, normalized_text)
        if result:
            return result

        # Fallback: try other majors if not found
        for other_major in ["cs", "ne", "ds", "it-ce"]:
            if other_major == major:
                continue
            try:
                result = self._resolve_in_major(other_major, cohort, normalized_text)
                if result:
                    return result
            except FileNotFoundError:
                continue

        return None

    def _resolve_in_major(self, major: str, cohort: str, normalized_text: str) -> dict | None:
        """Try to resolve course name within a specific major/cohort."""
        curriculum = self.get_curriculum(major, cohort)

        exact_matches: list[dict] = []
        for alias, canonical_name in COURSE_ALIAS_MAP.items():
            if self._contains_exact_phrase(normalized_text, alias):
                for course in curriculum.get("courses", []):
                    course_name = str(course.get("course_name", "")).lower()
                    canonical_lower = canonical_name.lower()
                    # Match if course name contains canonical OR canonical contains course name
                    # This handles plural/singular differences: "Operating Systems" vs "Operating System"
                    if canonical_lower in course_name or course_name in canonical_lower:
                        exact_matches.append(course)

        # Deduplicate by course_code (multiple aliases can map to the same course)
        seen_codes = set()
        unique_exact = []
        for course in exact_matches:
            code = course.get("course_code", "")
            if code not in seen_codes:
                seen_codes.add(code)
                unique_exact.append(course)
        exact_matches = unique_exact

        if len(exact_matches) == 1:
            return exact_matches[0]
        if len(exact_matches) > 1:
            return None

        matches: list[dict] = []
        for course in curriculum.get("courses", []):
            course_name = self._normalize_text(str(course.get("course_name", "")))
            course_code = str(course.get("course_code", "")).lower()

            if course_name and self._contains_exact_phrase(normalized_text, course_name):
                matches.append(course)
                continue

            if course_code and course_code in normalized_text:
                matches.append(course)

        if len(matches) == 1:
            return matches[0]
        return None

    def get_course_requirements(self, major: str, cohort: str, course_code: str) -> dict:
        curriculum = self.get_curriculum(major, cohort)
        normalized_code = course_code.upper()

        for course in curriculum.get("courses", []):
            if course.get("course_code", "").upper() == normalized_code:
                return {
                    "found": True,
                    "course_code": course.get("course_code"),
                    "course_name": course.get("course_name"),
                    "prerequisites": course.get("prerequisites", []),
                    "previous": course.get("previous", []),
                    "co_requisites": course.get("co_requisites", []),
                }

        return {
            "found": False,
            "course_code": normalized_code,
            "course_name": None,
            "prerequisites": [],
            "previous": [],
            "co_requisites": [],
        }
