import re

from app.generated.CourseQueryParser import CourseQueryParser
from app.generated.CourseQueryVisitor import CourseQueryVisitor
from app.nlp.intents import (
    ASK_COURSE_ELIGIBILITY,
    ASK_COURSE_REQUIREMENTS,
    ASK_DROP_TIME,
    ASK_PREREQUISITE_ONLY,
    ASK_PREVIOUS_ONLY,
    ASK_REGISTRATION_PLATFORM,
    ASK_REGISTRATION_TIME,
)


class IntentSlotExtractor(CourseQueryVisitor):
    """
    ANTLR visitor for the simplified CourseQuery grammar.

    Grammar mapping:
    - greetingQuery -> GREETING
    - helpQuery -> HELP
    - eligibilityQuery -> ASK_COURSE_ELIGIBILITY
    - prerequisiteQuery -> ASK_PREREQUISITE_ONLY
    - previousQuery -> ASK_PREVIOUS_ONLY
    - courseInfoQuery -> ASK_COURSE_REQUIREMENTS
    - dropQuery -> ASK_DROP_TIME
    - registrationQuery -> ASK_REGISTRATION_TIME
    """

    def __init__(self):
        self.intent = None
        self.course_code = None
        self.semester_code = None
        self._raw_text = ""

    def extract(self, ctx, raw_text: str = "") -> dict:
        """Main entry point - visit the tree and return result."""
        self._raw_text = raw_text or (ctx.getText() if ctx else "")
        self.visit(ctx)
        if not self.semester_code and self._raw_text:
            from app.nlp.parser import extract_semester_code
            self.semester_code = extract_semester_code(self._raw_text)
        return {
            "intent": self.intent,
            "course_code": self.course_code,
            "semester_code": self.semester_code,
            "antlr_parsed": self.course_code is not None or self.intent is not None,
        }

    def visitGreetingQuery(self, ctx: CourseQueryParser.GreetingQueryContext):
        self.intent = "GREETING"

    def visitHelpQuery(self, ctx: CourseQueryParser.HelpQueryContext):
        self.intent = "HELP"

    def visitEligibilityQuery(self, ctx: CourseQueryParser.EligibilityQueryContext):
        self.intent = ASK_COURSE_ELIGIBILITY
        self._extract_course_code(ctx)

    def visitPrerequisiteQuery(self, ctx: CourseQueryParser.PrerequisiteQueryContext):
        self.intent = ASK_PREREQUISITE_ONLY
        self._extract_course_code(ctx)

    def visitPreviousQuery(self, ctx: CourseQueryParser.PreviousQueryContext):
        self.intent = ASK_PREVIOUS_ONLY
        self._extract_course_code(ctx)

    def visitCourseInfoQuery(self, ctx: CourseQueryParser.CourseInfoQueryContext):
        self.intent = ASK_COURSE_REQUIREMENTS
        self._extract_course_code(ctx)

    def visitDropQuery(self, ctx: CourseQueryParser.DropQueryContext):
        self.intent = ASK_DROP_TIME
        self._extract_course_code(ctx)
        self._extract_semester(ctx)

    def visitRegistrationQuery(self, ctx: CourseQueryParser.RegistrationQueryContext):
        # Check if there's a platform keyword in raw text
        lower = self._raw_text.lower()
        if any(w in lower for w in ["website", "web", "platform", "cổng", "nền tảng"]):
            self.intent = ASK_REGISTRATION_PLATFORM
        else:
            self.intent = ASK_REGISTRATION_TIME
        self._extract_course_code(ctx)
        self._extract_semester(ctx)

    def _extract_course_code(self, ctx):
        if ctx.COURSE_CODE():
            self.course_code = ctx.COURSE_CODE().getText().upper()

    def _extract_semester(self, ctx):
        if ctx.SEMESTER():
            raw = ctx.SEMESTER().getText().lower().strip()
            m = re.match(r"(sp|spr|spring|su|sum|summer|fa|fal|fall)[\-]?(\d{2,4})", raw)
            if m:
                term_map = {"sp": "SP", "spr": "SP", "spring": "SP",
                            "su": "SU", "sum": "SU", "summer": "SU",
                            "fa": "FA", "fal": "FA", "fall": "FA"}
                term = term_map.get(m.group(1), "")
                year_part = m.group(2)
                year = year_part[-2:] if year_part else ""
                if term and year:
                    self.semester_code = f"{term}{year}"
