from app.nlp.parser import infer_cohort_from_student_id, parse_command
from app.nlp.processor import CommandProcessor
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.session_memory_service import SessionMemoryService


class ChatService:
    def __init__(self):
        self.processor = CommandProcessor()
        self.session_memory = SessionMemoryService()

    @staticmethod
    def _extract_cohort_from_message(message: str) -> str | None:
        text = message.strip().lower()
        if any(token in text for token in ("k21", "khóa 21", "khoa 21", "khóa21", "khoa21")):
            return "k21"
        if any(token in text for token in ("k22", "khóa 22", "khoa 22", "khóa22", "khoa22")):
            return "k22"
        if any(token in text for token in ("k23", "khóa 23", "khoa 23", "khóa23", "khoa23")):
            return "k23"
        if any(token in text for token in ("k24", "khóa 24", "khoa 24", "khóa24", "khoa24")):
            return "k24"
        return None

    @staticmethod
    def _extract_major_from_message(message: str) -> str | None:
        text = message.strip().lower()
        if any(token in text for token in ("ds", "data science", "khoa ds")):
            return "ds"
        if any(token in text for token in ("it-ce", "it ce", "itce", "computer engineering")):
            return "it-ce"
        if any(token in text for token in ("cs", "computer science", "khoa cs")):
            return "cs"
        if any(token in text for token in ("ne", "network engineering", "khoa ne")):
            return "ne"
        return None

    @staticmethod
    def _extract_name_from_message(message: str) -> str | None:
        text = message.strip()
        markers = ["mình tên là", "toi ten la", "tôi tên là", "mình là", "toi la", "tôi là", "name is", "my name is"]
        lower = text.lower()
        for marker in markers:
            if marker in lower:
                after = text[lower.index(marker) + len(marker):].strip()
                return after.split(" ")[0] if after else None
        return None

    def handle_message(self, payload: ChatRequest) -> ChatResponse:
        memory = self.session_memory.get_or_create(payload.session_id)
        parsed = parse_command(payload.message, student_id=payload.student_id)
        parsed_slots = parsed.setdefault("slots", {})

        incoming_cohort = (
            parsed_slots.get("cohort")
            or parsed_slots.get("cohort_from_student_id")
            or infer_cohort_from_student_id(payload.student_id)
            or self._extract_cohort_from_message(payload.message)
        )
        incoming_major = self._extract_major_from_message(payload.message)
        incoming_name = self._extract_name_from_message(payload.message)

        # Determine whether onboarding identity is known before processing.
        known_identity = bool(
            payload.student_id
            or incoming_cohort
            or (memory and (memory.last_student_id or memory.last_cohort))
        )

        if memory:
            # Persist identity early so the next turn can reuse it.
            if incoming_cohort:
                memory.last_cohort = incoming_cohort
            if incoming_major:
                memory.last_major = incoming_major
            if payload.student_id:
                memory.last_student_id = payload.student_id
            if incoming_name:
                memory.metadata["student_name"] = incoming_name

            # Hydrate parsed slots from session memory.
            if not parsed_slots.get("student_id"):
                parsed_slots["student_id"] = payload.student_id or memory.last_student_id
            if not parsed_slots.get("cohort"):
                parsed_slots["cohort"] = incoming_cohort or memory.last_cohort
            if not parsed_slots.get("major"):
                parsed_slots["major"] = incoming_major or memory.last_major
            if not parsed_slots.get("semester_code"):
                parsed_slots["semester_code"] = memory.last_semester_code
            if not parsed_slots.get("course_code") and memory.last_course_code:
                parsed_slots["course_code"] = memory.last_course_code

            # Onboarding: if we still don't know the user identity, stop here.
            if not memory.onboarding_complete and not known_identity:
                result = {
                    "intent": "ONBOARDING",
                    "confidence": 0.98,
                    "reply": "Rất vui được giúp bạn, vui lòng cho mình mã số sinh viên hoặc cho mình biết bạn đang học K21, K22, K23, K24 (hoặc khóa 21/22/23/24) nhé.",
                    "message": "Rất vui được giúp bạn, vui lòng cho mình mã số sinh viên hoặc cho mình biết bạn đang học K21, K22, K23, K24 (hoặc khóa 21/22/23/24) nhé.",
                    "slots": {
                        "student_id": payload.student_id,
                        "cohort": incoming_cohort or memory.last_cohort,
                        "major": incoming_major or memory.last_major,
                    },
                    "missing_slots": ["student_id_or_cohort"],
                    "follow_up_question": "Bạn cho mình MSSV hoặc khóa nhé.",
                    "data": None,
                }
                return ChatResponse(**result)

        result = self.processor.process(parsed)

        if memory:
            result_slots = dict(result.get("slots", {}))
            cohort_value = result_slots.get("cohort") or result_slots.get("cohort_from_student_id") or memory.last_cohort or incoming_cohort
            major_value = result_slots.get("major") or memory.last_major or incoming_major

            if cohort_value:
                memory.last_cohort = cohort_value
            if major_value:
                memory.last_major = major_value
            if payload.student_id:
                memory.last_student_id = payload.student_id
            if incoming_name:
                memory.metadata["student_name"] = incoming_name

            memory.last_course_code = result_slots.get("course_code") or memory.last_course_code
            memory.last_course_name = result.get("data", {}).get("course_name") if result.get("data") else memory.last_course_name
            memory.last_intent = result.get("intent")
            memory.last_semester_code = result_slots.get("semester_code") or memory.last_semester_code
            memory.onboarding_complete = True

            # Ensure response carries the active context without losing processor slots.
            result_slots.setdefault("student_id", payload.student_id or memory.last_student_id)
            result_slots.setdefault("cohort", cohort_value)
            result_slots.setdefault("major", major_value)
            result_slots.setdefault("course_code", memory.last_course_code)
            result_slots.setdefault("semester_code", memory.last_semester_code)
            result["slots"] = result_slots

        return ChatResponse(**result)
