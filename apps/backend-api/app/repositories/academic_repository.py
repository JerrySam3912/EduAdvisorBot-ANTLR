from __future__ import annotations

from app.services.curriculum_loader import CurriculumLoader


class AcademicRepository:
    """
    Curriculum access layer.
    Loads machine-readable curriculum rules instead of demo registration data.
    """

    def __init__(self):
        self.loader = CurriculumLoader()

    def load_curriculum(self, major: str, cohort: str) -> dict:
        return self.loader.load_curriculum(major, cohort)

    def get_course(self, major: str, cohort: str, course_code: str) -> dict | None:
        curriculum = self.load_curriculum(major, cohort)
        normalized_code = course_code.upper()

        for course in curriculum.get("courses", []):
            if course.get("course_code", "").upper() == normalized_code:
                return course
        return None
