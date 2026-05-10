from app.nlp.intents import (
    ASK_COURSE_ELIGIBILITY,
    ASK_COURSE_REQUIREMENTS,
    ASK_DROP_TIME,
    ASK_INSTRUCTOR,
    ASK_REGISTRATION_PLATFORM,
    ASK_REGISTRATION_TIME,
    UNKNOWN,
)
from app.nlp.parser import infer_cohort_from_student_id
from app.repositories.academic_repository import AcademicRepository
from app.services.curriculum_service import CurriculumService
from app.services.edusoft_notice_service import EdusoftNoticeService


class CommandProcessor:
    def __init__(self):
        self.repository = AcademicRepository()
        self.curriculum_service = CurriculumService()
        self.notice_service = EdusoftNoticeService()

    def process(self, parsed: dict) -> dict:
        text = parsed["normalized_text"]
        slots = parsed.get("slots", {})
        intent = parsed.get("intent", UNKNOWN)

        course_code = slots.get("course_code") or self.curriculum_service.extract_course_code(text)
        if course_code:
            if intent == ASK_COURSE_ELIGIBILITY:
                return self._handle_course_eligibility(text=text, slots=slots, course_code=course_code)
            if intent == ASK_REGISTRATION_TIME:
                return self._handle_registration_time(text=text, slots=slots, course_code=course_code)
            if intent == ASK_DROP_TIME:
                return self._handle_drop_time(text=text, slots=slots, course_code=course_code)
            if intent == ASK_REGISTRATION_PLATFORM:
                return self._handle_registration_platform(text=text, slots=slots, course_code=course_code)
            if intent == ASK_INSTRUCTOR:
                return self._handle_instructor(text=text, slots=slots, course_code=course_code)
            return self._handle_course_query(text=text, slots=slots, course_code=course_code)

        if intent in {ASK_REGISTRATION_TIME, ASK_DROP_TIME, ASK_REGISTRATION_PLATFORM, ASK_INSTRUCTOR, ASK_COURSE_ELIGIBILITY, ASK_COURSE_REQUIREMENTS}:
            return self._handle_missing_course_slot(intent=intent, slots=slots)

        return self._build_response(
            intent=UNKNOWN,
            confidence=0.35,
            reply="Mình hiện hỗ trợ hỏi về môn học, đăng ký môn, drop môn, giảng viên và điều kiện học. Ví dụ: 'IT094IU cần học gì trước?'.",
            slots={},
            missing_slots=[],
            follow_up_question="Bạn muốn hỏi về môn nào?",
            data=None,
        )

    def _handle_missing_course_slot(self, *, intent: str, slots: dict) -> dict:
        missing_slots = ["course_code"]
        if not (slots.get("student_id") or slots.get("cohort")) and intent == ASK_COURSE_ELIGIBILITY:
            missing_slots.append("student_id_or_cohort")

        question = "Bạn cho mình mã môn để mình kiểm tra nhé."
        if intent == ASK_COURSE_ELIGIBILITY:
            question = "Bạn cho mình mã môn và MSSV hoặc khóa để mình kiểm tra điều kiện học nhé."
        elif intent == ASK_REGISTRATION_TIME:
            question = "Bạn cho mình mã môn và kỳ học để mình tra thời gian đăng ký nhé."
        elif intent == ASK_DROP_TIME:
            question = "Bạn cho mình mã môn và kỳ học để mình tra thời gian drop nhé."
        elif intent == ASK_REGISTRATION_PLATFORM:
            question = "Bạn cho mình mã môn để mình tra nền tảng đăng ký nhé."
        elif intent == ASK_INSTRUCTOR:
            question = "Bạn cho mình mã môn để mình tra giảng viên nhé."

        return self._build_response(
            intent=intent,
            confidence=0.8,
            reply=question,
            slots=slots,
            missing_slots=missing_slots,
            follow_up_question=question,
            data=None,
        )

    def _handle_course_query(self, *, text: str, slots: dict, course_code: str) -> dict:
        cohort = slots.get("cohort") or infer_cohort_from_student_id(slots.get("student_id")) or "k21"
        major = self._infer_major_from_cohort(cohort)
        course = self.repository.get_course(major=major, cohort=cohort, course_code=course_code)

        if not course:
            return self._build_response(
                intent=ASK_COURSE_REQUIREMENTS,
                confidence=0.82,
                reply=f"Mình chưa tìm thấy dữ liệu cho môn {course_code} trong {major.upper()} {cohort.upper()}.",
                slots={"course_code": course_code, "major": major, "cohort": cohort},
                missing_slots=[],
                follow_up_question=None,
                data=None,
            )

        requirements = self.curriculum_service.get_course_requirements(major=major, cohort=cohort, course_code=course_code)
        reply = self._format_course_reply(requirements)
        return self._build_response(
            intent=ASK_COURSE_REQUIREMENTS,
            confidence=0.96,
            reply=reply,
            slots={"course_code": course_code, "major": major, "cohort": cohort},
            missing_slots=[],
            follow_up_question=None,
            data=requirements,
        )

    def _handle_course_eligibility(self, *, text: str, slots: dict, course_code: str) -> dict:
        if not slots.get("student_id") and not slots.get("cohort"):
            return self._build_response(
                intent=ASK_COURSE_ELIGIBILITY,
                confidence=0.85,
                reply="Bạn cho mình MSSV hoặc khóa để mình kiểm tra môn này có học được không nhé.",
                slots={"course_code": course_code},
                missing_slots=["student_id_or_cohort"],
                follow_up_question="Bạn cho mình MSSV hoặc khóa nhé.",
                data=None,
            )

        cohort = slots.get("cohort") or infer_cohort_from_student_id(slots.get("student_id")) or "k21"
        major = self._infer_major_from_cohort(cohort)
        requirements = self.curriculum_service.get_course_requirements(major=major, cohort=cohort, course_code=course_code)

        if not requirements.get("found"):
            return self._build_response(
                intent=ASK_COURSE_ELIGIBILITY,
                confidence=0.83,
                reply=f"Mình chưa có dữ liệu để kiểm tra điều kiện học cho môn {course_code}.",
                slots={"course_code": course_code, "major": major, "cohort": cohort},
                missing_slots=[],
                follow_up_question=None,
                data=None,
            )

        reply = self._format_eligibility_reply(requirements, cohort=cohort, student_id=slots.get("student_id"))
        return self._build_response(
            intent=ASK_COURSE_ELIGIBILITY,
            confidence=0.95,
            reply=reply,
            slots={"course_code": course_code, "major": major, "cohort": cohort},
            missing_slots=[],
            follow_up_question=None,
            data=requirements,
        )

    def _handle_registration_time(self, *, text: str, slots: dict, course_code: str) -> dict:
        notice = self.notice_service.get_latest_drop_notice()
        semester_code = slots.get("semester_code")
        if not semester_code:
            question = "Bạn cho mình kỳ học (ví dụ SP25) để mình tra thời gian đăng ký nhé."
            return self._build_response(
                intent=ASK_REGISTRATION_TIME,
                confidence=0.84,
                reply=question,
                slots={"course_code": course_code, **slots},
                missing_slots=["semester_code"],
                follow_up_question=question,
                data=None,
            )
        if notice:
            return self._build_response(
                intent=ASK_REGISTRATION_TIME,
                confidence=0.92,
                reply=(
                    f"Theo thông báo Edusoft, thời gian điều chỉnh đăng ký môn học {notice['semester']}: "
                    f"{notice['time_windows'][0]['from']}–{notice['time_windows'][0]['to']} từ {notice['time_windows'][0]['days'][0]} "
                    f"đến {notice['time_windows'][0]['days'][-1]}, và {notice['time_windows'][1]['from']}–{notice['time_windows'][1]['to']} vào {notice['time_windows'][1]['days'][0]}."
                ),
                slots={"course_code": course_code, **slots},
                missing_slots=[],
                follow_up_question=None,
                data=notice,
            )
        return self._build_response(
            intent=ASK_REGISTRATION_TIME,
            confidence=0.86,
            reply=f"Mình chưa có lịch đăng ký thật cho {semester_code.upper()} trong dữ liệu hiện tại.",
            slots={"course_code": course_code, **slots},
            missing_slots=[],
            follow_up_question=None,
            data={"semester_code": semester_code},
        )

    def _handle_drop_time(self, *, text: str, slots: dict, course_code: str) -> dict:
        notice = self.notice_service.get_latest_drop_notice()
        semester_code = slots.get("semester_code")
        if not semester_code:
            question = "Bạn cho mình kỳ học (ví dụ SP25) để mình tra thời gian drop nhé."
            return self._build_response(
                intent=ASK_DROP_TIME,
                confidence=0.84,
                reply=question,
                slots={"course_code": course_code, **slots},
                missing_slots=["semester_code"],
                follow_up_question=question,
                data=None,
            )
        if notice:
            return self._build_response(
                intent=ASK_DROP_TIME,
                confidence=0.95,
                reply=(
                    f"Theo thông báo Edusoft, thời gian hiệu chỉnh / drop môn học {notice['semester']} là: "
                    f"{notice['time_windows'][0]['from']}–{notice['time_windows'][0]['to']} từ {notice['time_windows'][0]['days'][0]} "
                    f"đến {notice['time_windows'][0]['days'][-1]}, và {notice['time_windows'][1]['from']}–{notice['time_windows'][1]['to']} vào {notice['time_windows'][1]['days'][0]}."
                ),
                slots={"course_code": course_code, **slots},
                missing_slots=[],
                follow_up_question=None,
                data=notice,
            )
        return self._build_response(
            intent=ASK_DROP_TIME,
            confidence=0.86,
            reply=f"Mình chưa có lịch drop thật cho {semester_code.upper()} trong dữ liệu hiện tại.",
            slots={"course_code": course_code, **slots},
            missing_slots=[],
            follow_up_question=None,
            data={"semester_code": semester_code},
        )

    def _handle_registration_platform(self, *, text: str, slots: dict, course_code: str) -> dict:
        return self._build_response(
            intent=ASK_REGISTRATION_PLATFORM,
            confidence=0.9,
            reply=f"Bạn đăng ký môn {course_code} trên cổng đăng ký của trường (theo quy định từng kỳ). Nếu bạn muốn, mình có thể tra theo khóa/kỳ cụ thể.",
            slots={"course_code": course_code, **slots},
            missing_slots=[],
            follow_up_question=None,
            data={"platform": "university_registration_portal"},
        )

    def _handle_instructor(self, *, text: str, slots: dict, course_code: str) -> dict:
        return self._build_response(
            intent=ASK_INSTRUCTOR,
            confidence=0.88,
            reply=f"Mình hiện chưa có dữ liệu giảng viên cho môn {course_code}. Nếu bạn gửi syllabus hoặc danh sách lớp, mình có thể hỗ trợ tra tiếp.",
            slots={"course_code": course_code, **slots},
            missing_slots=[],
            follow_up_question=None,
            data=None,
        )

    @staticmethod
    def _infer_major_from_cohort(cohort: str) -> str:
        cohort = (cohort or "").lower()
        if cohort == "k21":
            return "cs"
        if cohort in {"k22", "k23"}:
            return "cs"
        if cohort == "k24":
            return "ne"
        return "cs"

    @staticmethod
    def _format_course_reply(requirements: dict) -> str:
        if not requirements.get("found"):
            return f"Mình chưa có dữ liệu cho môn {requirements['course_code']}."

        parts = [f"Môn {requirements['course_code']} - {requirements.get('course_name', '')}".strip()]

        prerequisites = requirements.get("prerequisites", [])
        previous = requirements.get("previous", [])
        co_requisites = requirements.get("co_requisites", [])

        if prerequisites:
            parts.append(f"Tiên quyết: {', '.join(prerequisites)}")
        if previous:
            parts.append(f"Previous: {', '.join(previous)}")
        if co_requisites:
            parts.append(f"Co-requisite: {', '.join(co_requisites)}")

        return " | ".join(parts)

    @staticmethod
    def _format_eligibility_reply(requirements: dict, *, cohort: str, student_id: str | None) -> str:
        prerequisites = requirements.get("prerequisites", [])
        if not prerequisites:
            return f"Theo data {cohort.upper()}, môn {requirements['course_code']} không có tiên quyết bắt buộc."
        return (
            f"Theo data {cohort.upper()}, để học {requirements['course_code']} bạn cần hoàn thành: "
            f"{', '.join(prerequisites)}."
        )

    @staticmethod
    def _build_response(
        *,
        intent: str,
        confidence: float,
        reply: str,
        slots: dict,
        missing_slots: list[str],
        follow_up_question: str | None,
        data: dict | None,
    ) -> dict:
        return {
            "intent": intent,
            "confidence": confidence,
            "reply": reply,
            "message": reply,
            "slots": slots,
            "missing_slots": missing_slots,
            "follow_up_question": follow_up_question,
            "data": data,
        }
