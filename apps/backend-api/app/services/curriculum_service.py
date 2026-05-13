from __future__ import annotations

import re
from functools import lru_cache

from app.repositories.academic_repository import AcademicRepository


COURSE_CODE_PATTERN = re.compile(r"\b([A-Z]{2,4}\d{3}(?:IU)?)\b", flags=re.IGNORECASE)
COURSE_ALIAS_MAP = {
    "oop": "Object-Oriented Programming",
    "ai": "Artificial Intelligence",
    "web dev": "Web Application Development",
    "web application": "Web Application Development",
    "db": "Principles of Database Management",
    "database": "Principles of Database Management",
    "data mining": "Data Mining",
    "os": "Operating Systems",
    "operating system": "Operating Systems",
    "network": "Computer Networks",
    "net-centric": "Net-centric Programming",
    "project management": "IT Project Management",
    "software engineering": "Software Engineering",
    "computer graphics": "Computer Graphics",
    "mobile app": "Mobile Application Development",
    "iot": "Internet of Things",
    "deep learning": "Deep Learning",
    "blockchain": "Blockchain",
    "devops": "Development & Operation",
    "hcm thoughts": "Ho Chi Minh's Thoughts",
}


class CurriculumService:
    def __init__(self):
        self.repository = AcademicRepository()

    @staticmethod
    def extract_course_code(text: str) -> str | None:
        match = COURSE_CODE_PATTERN.search(text.upper())
        if not match:
            return None
        return match.group(1).upper()

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    @lru_cache(maxsize=256)
    def get_curriculum(self, major: str, cohort: str) -> dict:
        return self.repository.load_curriculum(major, cohort)

    def resolve_course_by_name(self, major: str, cohort: str, user_text: str) -> dict | None:
        curriculum = self.get_curriculum(major, cohort)
        normalized_text = self._normalize_text(user_text)

        for alias, canonical_name in COURSE_ALIAS_MAP.items():
            if alias in normalized_text:
                for course in curriculum.get("courses", []):
                    course_name = self._normalize_text(str(course.get("course_name", "")))
                    if canonical_name.lower() == course_name:
                        return course

        matches: list[dict] = []
        for course in curriculum.get("courses", []):
            course_name = self._normalize_text(str(course.get("course_name", "")))
            course_code = str(course.get("course_code", "")).lower()

            if course_name and course_name in normalized_text:
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
