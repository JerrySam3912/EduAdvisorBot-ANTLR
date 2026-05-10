from __future__ import annotations

import re
from functools import lru_cache

from app.repositories.academic_repository import AcademicRepository


COURSE_CODE_PATTERN = re.compile(r"\b([A-Z]{2,4}\d{3}(?:IU)?)\b", flags=re.IGNORECASE)


class CurriculumService:
    def __init__(self):
        self.repository = AcademicRepository()

    @staticmethod
    def extract_course_code(text: str) -> str | None:
        match = COURSE_CODE_PATTERN.search(text.upper())
        if not match:
            return None
        return match.group(1).upper()

    @lru_cache(maxsize=256)
    def get_curriculum(self, major: str, cohort: str) -> dict:
        return self.repository.load_curriculum(major, cohort)

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
