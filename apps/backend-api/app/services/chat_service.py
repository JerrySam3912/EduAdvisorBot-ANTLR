import re

from app.nlp.language_detection import detect_non_vietnamese, validate_response_language
from app.nlp.parser import (
    extract_major_from_student_id,
    infer_cohort_from_student_id,
    parse_command,
    STUDENT_ID_PATTERN,
)
from app.nlp.processor import CommandProcessor
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.session_memory_service import SessionMemoryService


class ChatService:
    def __init__(self):
        self.processor = CommandProcessor()
        self.session_memory = SessionMemoryService()

    @staticmethod
    def _extract_student_id_from_message(message: str) -> str | None:
        text = message.strip()
        # Full format: ITCSIU22001
        match = STUDENT_ID_PATTERN.search(text.upper())
        if match:
            return match.group(0)
        # 7-digit numeric format: 2401036
        match7 = re.search(r'\b(\d{7})\b', text)
        if match7:
            return match7.group(1)
        return None

    @staticmethod
    def _extract_cohort_from_message(message: str) -> str | None:
        text = message.strip().lower()
        # Extract ANY cohort from k10 to k99 (handles k19, k20, k25, etc.)
        match = re.search(r"\bk(\d{2})\b", text)
        if match:
            return f"k{match.group(1)}"
        return None

    @staticmethod
    def _extract_major_from_message(message: str) -> str | None:
        text = message.strip().lower()
        # Extract standalone major codes first (MUST come before course_code extraction
        # so that "CS" in "mình học CS" is recognized as a major, not a course_code).
        # These must be standalone tokens to avoid matching them inside longer words.
        # Use word boundary: preceded by space/start and followed by space/end/punctuation.
        major_patterns = [
            (r'(?:^|\s)cs(?:\s|$|[,.\-–])', "cs"),
            (r'(?:^|\s)ne(?:\s|$|[,.\-–])', "ne"),
            (r'(?:^|\s)ds(?:\s|$|[,.\-–])', "ds"),
            (r'(?:^|\s)ce(?:\s|$|[,.\-–])', "it-ce"),
        ]
        for pattern, major in major_patterns:
            if re.search(pattern, text):
                return major
        if "computer science" in text or "khoa cs" in text:
            return "cs"
        if "network engineering" in text or "khoa ne" in text:
            return "ne"
        if "data science" in text or "khoa ds" in text:
            return "ds"
        if "computer engineering" in text or "it-ce" in text or "it ce" in text:
            return "it-ce"
        if any(token in text for token in (" ngành cs", " nganh cs", " cs ", "cs,")):
            return "cs"
        if any(token in text for token in (" ngành ne", " nganh ne", " ne ", "ne,")):
            return "ne"
        if any(token in text for token in (" ngành ds", " nganh ds", " ds ", "ds,")):
            return "ds"
        if any(token in text for token in (" ngành ce", " nganh ce", " ce ", "ce,")):
            return "it-ce"
        return None

    def _infer_identity(self, payload: ChatRequest, parsed_slots: dict) -> tuple[str | None, str | None, str | None]:
        student_id = (
            payload.student_id
            or parsed_slots.get("student_id")
            or self._extract_student_id_from_message(payload.message)
        )
        cohort = (
            parsed_slots.get("cohort")
            or parsed_slots.get("cohort_from_student_id")
            or infer_cohort_from_student_id(student_id)
            or self._extract_cohort_from_message(payload.message)
        )
        major = (
            parsed_slots.get("major_from_student_id")
            or extract_major_from_student_id(student_id)
            or self._extract_major_from_message(payload.message)
        )
        return major, cohort, student_id

    @staticmethod
    def _sanitize_response(response: dict) -> dict:
        reply = response.get("reply", "") or ""
        validation = validate_response_language(reply)
        if not validation["is_valid"]:
            response = dict(response)
            response["reply"] = validation["sanitized"]
            response["message"] = validation["sanitized"]
            response["confidence"] = 0.01
        return response

    def _build_response(self, response: dict) -> ChatResponse:
        return ChatResponse(**self._sanitize_response(response))

    def _build_onboarding_response(self, reply: str, *, student_id, cohort, major, missing_slots) -> dict:
        return {
            "intent": "ONBOARDING",
            "confidence": 0.98,
            "reply": reply,
            "message": reply,
            "slots": {"student_id": student_id, "cohort": cohort, "major": major},
            "missing_slots": missing_slots or ["student_id_or_cohort"],
            "follow_up_question": reply,
            "data": None,
        }

    def _update_memory_from_result(self, memory, result: dict, result_slots: dict,
                                   parsed_slots: dict,
                                   explicit_cohort, inferred_cohort,
                                   explicit_major, inferred_major,
                                   student_id) -> None:
        """Update session memory from processor result.

        Priority for cohort: explicit_cohort_from_text > memory.last_cohort > student_id_inference
        Priority for course_code: result_slots.course_code > parsed_slots.course_code > memory.last_course_code
        """
        # Priority: explicit text cohort > memory > inferred from student_id
        # This ensures user's explicit correction ("khóa 23") is NEVER overwritten by student_id inference ("k22")
        cohort_value = parsed_slots.get("cohort_from_text") or memory.last_cohort or inferred_cohort

        # Major: explicit text > memory > inferred from student_id
        major_value = parsed_slots.get("major") or memory.last_major or inferred_major

        if cohort_value:
            memory.last_cohort = cohort_value
        if major_value:
            memory.last_major = major_value
        if student_id:
            memory.last_student_id = student_id

        # Course code: result_slots.course_code > parsed_slots.course_code > memory.last_course_code
        course_code = result_slots.get("course_code") or parsed_slots.get("course_code") or memory.last_course_code
        memory.last_course_code = course_code
        memory.last_course_name = result.get("data", {}).get("course_name") if result.get("data") else memory.last_course_name
        memory.last_intent = result.get("intent")
        memory.last_semester_code = result_slots.get("semester_code") or memory.last_semester_code
        memory.onboarding_complete = bool(memory.last_cohort and memory.last_major)

    def handle_message(self, payload: ChatRequest) -> ChatResponse:
        memory = self.session_memory.get_or_create(payload.session_id)

        # ================================================================
        # STEP 1: Language drift guard — ALWAYS runs first
        # ================================================================
        lang_check = detect_non_vietnamese(payload.message)
        if not lang_check["is_vietnamese"]:
            response = {
                "intent": "LANGUAGE_DRIFT",
                "confidence": 0.99,
                "reply": (
                    "Mình chỉ hỗ trợ tiếng Việt thôi nhé. "
                    "Bạn vừa dùng ngôn ngữ khác — mình không hiểu được. "
                    "Bạn hỏi lại bằng tiếng Việt giúp mình nhé!"
                ),
                "message": (
                    "Mình chỉ hỗ trợ tiếng Việt thôi nhé. "
                    "Bạn vừa dùng ngôn ngữ khác — mình không hiểu được. "
                    "Bạn hỏi lại bằng tiếng Việt giúp mình nhé!"
                ),
                "slots": {},
                "missing_slots": [],
                "follow_up_question": "Bạn hỏi mình bằng tiếng Việt nhé! Ví dụ: 'tiên quyết IT017IU là gì?'",
                "data": {"detected_language": lang_check["detected_language"]},
            }
            return ChatResponse(**self._sanitize_response(response))

        # ================================================================
        # STEP 2: Parse intent — ALWAYS runs first (this is critical)
        # ================================================================
        # Pass last_course_code for session memory (pronoun resolution like "môn này")
        parsed = parse_command(
            payload.message,
            student_id=payload.student_id,
            last_course_code=memory.last_course_code if memory else None,
        )
        slots = parsed.setdefault("slots", {})

        inferred_major, inferred_cohort, inferred_student_id = self._infer_identity(payload, slots)
        student_id = payload.student_id or inferred_student_id
        explicit_major = slots.get("major") or inferred_major
        explicit_cohort = slots.get("cohort") or inferred_cohort

        # ================================================================
        # STEP 3: Validate cohort range — only k21–k24 supported
        # ================================================================
        def _is_cohort_in_range(cohort: str | None) -> bool:
            if not cohort:
                return True  # Unknown cohort passes through — handled later as missing info
            try:
                num = int(cohort.lower().replace("k", ""))
                return 21 <= num <= 24
            except (ValueError, AttributeError):
                return True  # Invalid format passes through — handled later

        if not _is_cohort_in_range(explicit_cohort):
            return self._build_response(self._build_onboarding_response(
                "Hiện tại mình chỉ có thể tư vấn cho các bạn sinh viên từ K21 đến K24 thôi nhé. "
                "Tụi mình sẽ cập nhật thêm trong tương lai gần — mong bạn thông cảm!",
                student_id=student_id,
                cohort=explicit_cohort,
                major=explicit_major,
                missing_slots=["cohort_out_of_range"],
            ))

        if not _is_cohort_in_range(inferred_cohort):
            return self._build_response(self._build_onboarding_response(
                "Hiện tại mình chỉ có thể tư vấn cho các bạn sinh viên từ K21 đến K24 thôi nhé. "
                "Tụi mình sẽ cập nhật thêm trong tương lai gần — mong bạn thông cảm!",
                student_id=student_id,
                cohort=inferred_cohort,
                major=explicit_major,
                missing_slots=["cohort_out_of_range"],
            ))

        # ================================================================
        # STEP 4: Detect new student_id in current message and override memory
        # This handles "cho mình hỏi về môn OOP với mssv ITCSIU22001" mid-session
        # ================================================================
        new_student_id_in_message = self._extract_student_id_from_message(payload.message)
        explicit_new_student_id = None
        if new_student_id_in_message and new_student_id_in_message != memory.last_student_id:
            # New student_id in message → override memory for THIS request
            explicit_new_student_id = new_student_id_in_message
            student_id = explicit_new_student_id
            # Derive cohort/major from the new student_id
            from app.nlp.parser import (
                extract_major_from_student_id as _extract_major_from_id,
                infer_cohort_from_student_id as _infer_cohort_from_id,
            )
            explicit_major = _extract_major_from_id(explicit_new_student_id)
            explicit_cohort = _infer_cohort_from_id(explicit_new_student_id)

            # Validate new student_id's cohort range too
            if not _is_cohort_in_range(explicit_cohort):
                return self._build_response(self._build_onboarding_response(
                    "Hiện tại mình chỉ có thể tư vấn cho các bạn sinh viên từ K21 đến K24 thôi nhé. "
                    "Tụi mình sẽ cập nhật thêm trong tương lai gần — mong bạn thông cảm!",
                    student_id=explicit_new_student_id,
                    cohort=explicit_cohort,
                    major=explicit_major,
                    missing_slots=["cohort_out_of_range"],
                ))

        # ================================================================
        # STEP 5: Update session memory with identity from message
        # ================================================================
        if memory:
            if student_id:
                memory.last_student_id = student_id
            if explicit_cohort:
                memory.last_cohort = explicit_cohort
            if explicit_major:
                memory.last_major = explicit_major

            slots["student_id"] = memory.last_student_id
            slots["cohort"] = memory.last_cohort  # must OVERWRITE (not setdefault) to override stale inferred cohort
            slots["major"] = memory.last_major
            slots["semester_code"] = memory.last_semester_code
            # Fill course_code from memory so the processor can use it immediately
            # (critical for "môn này có học được không" — bot must know last course)
            if not slots.get("course_code") and memory.last_course_code:
                slots["course_code"] = memory.last_course_code

        # ================================================================
        # STEP 6: Validate cohort from memory — catches stale out-of-range cohorts
        # ================================================================
        if memory and memory.last_cohort and not _is_cohort_in_range(memory.last_cohort):
            return self._build_response(self._build_onboarding_response(
                "Hiện tại mình chỉ có thể tư vấn cho các bạn sinh viên từ K21 đến K24 thôi nhé. "
                "Tụi mình sẽ cập nhật thêm trong tương lai gần — mong bạn thông cảm!",
                student_id=memory.last_student_id,
                cohort=memory.last_cohort,
                major=memory.last_major,
                missing_slots=["cohort_out_of_range"],
            ))

        # ================================================================
        # STEP 7: Run the NLP processor — ALWAYS, no matter what
        # Inject memory defaults into slots BEFORE processor runs so that
        # the processor sees the full session context (cohort/major from memory),
        # enabling correct course lookup and identity-aware responses.
        # ================================================================
        if memory:
            # CRITICAL: Always create a FRESH parsed dict with FRESH slots — never share with parsed.
            # The parser's returned dict is reused across calls, and if the processor modifies
            # its slots, those modifications leak into subsequent calls (causing stale course codes).
            # Compute cohort/major from student_id for identity completeness check
            parsed_cohort_from_student_id = parsed["slots"].get("cohort_from_student_id")
            parsed_major_from_student_id = parsed["slots"].get("major_from_student_id")
            # Use explicit values if user provided a new student_id in this message;
            # otherwise fall back to memory. This ensures "cho mình hỏi với mssv X"
            # mid-session overrides the previously stored identity for THIS request.
            memory_student_id = explicit_new_student_id if explicit_new_student_id else memory.last_student_id
            effective_cohort = explicit_cohort if explicit_new_student_id else memory.last_cohort
            effective_major = explicit_major if explicit_new_student_id else memory.last_major
            if not parsed_cohort_from_student_id and memory_student_id:
                parsed_cohort_from_student_id = infer_cohort_from_student_id(memory_student_id)
            if not parsed_major_from_student_id and memory_student_id:
                from app.nlp.parser import extract_major_from_student_id
                parsed_major_from_student_id = extract_major_from_student_id(memory_student_id)

            processor_slots = {
                "semester_code": memory.last_semester_code,
                "cohort": effective_cohort,
                "cohort_from_text": None,
                "cohort_from_student_id": parsed_cohort_from_student_id,
                "major_from_student_id": parsed_major_from_student_id,
                "student_id": memory_student_id,
                "course_code": parsed["slots"].get("course_code"),
                "major": effective_major,
            }

            parsed_with_memory = {
                "raw_text": parsed["raw_text"],
                "normalized_text": parsed["normalized_text"],
                "intent": parsed["intent"],
                "antlr_parsed": parsed["antlr_parsed"],
                "language_detected": parsed["language_detected"],
                "language_warning": parsed["language_warning"],
                "slots": processor_slots,
            }
            result = self.processor.process(parsed_with_memory)
        else:
            result = self.processor.process(parsed)

        # ================================================================
        # STEP 8: Update memory from processor result
        # ================================================================
        if memory:
            result_slots = dict(result.get("slots", {}))
            self._update_memory_from_result(
                memory, result, result_slots,
                parsed["slots"],  # <-- pass parsed_slots for correct cohort priority
                explicit_cohort, inferred_cohort,
                explicit_major, inferred_major,
                student_id
            )
            # Merge result slots: explicit message values take PRIORITY over memory.
            # This ensures that if user says "ngành CS" in a new message,
            # the response uses "CS" even if memory previously stored "DS".
            result_slots.setdefault("student_id", memory.last_student_id)
            result_slots["cohort"] = (
                explicit_cohort if explicit_cohort else memory.last_cohort
            )
            result_slots["major"] = (
                explicit_major if explicit_major else memory.last_major
            )
            result_slots.setdefault("semester_code", memory.last_semester_code)
            # course_code: preserve what the handler set (e.g. recovered from "môn này" → IT094IU),
            # OR fill from memory if handler didn't set it
            if not result_slots.get("course_code"):
                result_slots["course_code"] = memory.last_course_code
            result["slots"] = result_slots

        # ================================================================
        # STEP 9: ONBOARDING — handle incomplete identity scenarios
        # ================================================================
        if result.get("intent") == "UNKNOWN":
            known_student = bool(memory.last_student_id) if memory else False
            known_cohort = bool(memory.last_cohort) if memory else False
            known_major = bool(memory.last_major) if memory else False

            # Case A: No identity at all
            if not (known_student or known_cohort or known_major):
                return self._build_response(self._build_onboarding_response(
                    "Bạn cho mình biết MSSV, hoặc tên ngành (NE/CE/CS/DS) và khóa (K21/K22/K23/K24) để mình tư vấn đúng chương trình nhé.",
                    student_id=student_id,
                    cohort=explicit_cohort,
                    major=explicit_major,
                    missing_slots=["student_id_or_cohort"],
                ))

            # Case B: Has student_id → full identity → ask what they need
            if known_student and not (known_cohort and known_major):
                return self._build_response(self._build_onboarding_response(
                    f"OK, mình đã ghi nhận MSSV: {memory.last_student_id.upper()}. "
                    "Bạn cần mình hỗ trợ gì?",
                    student_id=memory.last_student_id,
                    cohort=memory.last_cohort,
                    major=memory.last_major,
                    missing_slots=[],
                ))

            # Case C: Only major known → acknowledge + ask for cohort
            if known_major and not known_cohort and not known_student:
                return self._build_response(self._build_onboarding_response(
                    f"OK mình đã ghi nhận bạn học ngành {memory.last_major.upper()}. "
                    "Giờ bạn cho mình biết bạn khóa bao nhiêu? (K21/K22/K23/K24)?",
                    student_id=student_id,
                    cohort=None,
                    major=memory.last_major,
                    missing_slots=["cohort"],
                ))

            # Case D: Only cohort known → acknowledge + ask for major
            if known_cohort and not known_major and not known_student:
                return self._build_response(self._build_onboarding_response(
                    f"Mình đã ghi nhận bạn học Khóa {memory.last_cohort.upper()}. "
                    "Bạn đang học ngành nào? (NE/CE/CS/DS) để mình tư vấn đúng chương trình nhé.",
                    student_id=student_id,
                    cohort=memory.last_cohort,
                    major=None,
                    missing_slots=["major"],
                ))

            # Case E: Has partial (cohort but not major, or vice versa) + asking about course
            # → acknowledge what we know, ask for what we need
            has_partial = (known_cohort and not known_major) or (known_major and not known_cohort)
            if has_partial:
                lower_msg = payload.message.lower()
                asking_about_course = any(kw in lower_msg for kw in (
                    "môn ", "về môn", "tiên quyết", "prerequisite", "info", "thông tin",
                    "là gì", "giới thiệu", "eligible", "drop", "đăng ký", "register",
                    "hỏi", "tra ", "xem ", "tìm hiểu", "học được không",
                    "muốn học", "học oop", "muốn hỏi",
                    "oop", " ai ", " ml ", " os ",
                    "cần học gì trước", "học gì trước", "học được không",
                    "tư vấn môn", "tư vấn về", "học gì", "môn nào",
                    "operating system", "thuật toán", "cấu trúc dữ liệu",
                    "machine learning", "data structures",
                ))
                if asking_about_course:
                    if known_major and not known_cohort:
                        return self._build_response(self._build_onboarding_response(
                            f"OK mình đã ghi nhận bạn học ngành {memory.last_major.upper()}. "
                            "Giờ bạn cho mình biết bạn khóa bao nhiêu? (K21/K22/K23/K24)?",
                            student_id=student_id,
                            cohort=None,
                            major=memory.last_major,
                            missing_slots=["cohort"],
                        ))
                    if known_cohort and not known_major:
                        return self._build_response(self._build_onboarding_response(
                            f"Mình đã ghi nhận bạn học Khóa {memory.last_cohort.upper()}. "
                            "Bạn đang học ngành nào? (NE/CE/CS/DS) để mình tư vấn đúng chương trình nhé.",
                            student_id=student_id,
                            cohort=memory.last_cohort,
                            major=None,
                            missing_slots=["major"],
                        ))

        # ================================================================
        # STEP 10: Override IDENTITY_ACKNOWLEDGED when user also asked a course question
        # e.g. "cho mình hỏi về OOP với mssv X"
        # Only proceeds if identity is COMPLETE (student_id OR cohort+major).
        # ================================================================
        if result.get("intent") == "IDENTITY_ACKNOWLEDGED" and result.get("missing_slots") == ["course_code"]:
            lower_msg = payload.message.lower()
            asking_about_course = any(kw in lower_msg for kw in (
                "môn ", "về môn", "tiên quyết", "prerequisite", "info", "thông tin",
                "là gì", "giới thiệu", "eligible", "drop", "đăng ký", "register",
                "hỏi", "tra ", "xem ", "tìm hiểu", "học được không",
                "muốn học", "học oop", "muốn hỏi",
                "oop", " ai ", " ml ", " os ",
                "cần học gì trước", "học gì trước", "học được không",
                "tư vấn môn", "tư vấn về", "học gì", "môn nào",
                "operating system", "thuật toán", "cấu trúc dữ liệu",
                "machine learning", "data structures",
            ))
            if asking_about_course:
                # Identity completeness check: student_id OR (cohort AND major)
                has_student_id = bool(result_slots.get("student_id"))
                has_cohort = bool(result_slots.get("cohort"))
                has_major = bool(result_slots.get("major"))
                has_identity_complete = has_student_id or (has_cohort and has_major)

                if has_identity_complete:
                    # Re-process to get the course answer
                    reprocessed = parse_command(
                        payload.message,
                        student_id=payload.student_id,
                        last_course_code=memory.last_course_code if memory else None,
                    )
                    reprocessed_slots = reprocessed.setdefault("slots", {})
                    identity_slots = result_slots if memory else result.get("slots", {})
                    reprocessed_slots["cohort"] = identity_slots.get("cohort") or identity_slots.get("cohort_from_student_id")
                    reprocessed_slots["major"] = identity_slots.get("major") or identity_slots.get("major_from_student_id")
                    reprocessed_slots["student_id"] = identity_slots.get("student_id")
                    reprocessed_slots["semester_code"] = identity_slots.get("semester_code")
                    extracted_code = identity_slots.get("course_code")
                    if extracted_code and STUDENT_ID_PATTERN.search(extracted_code.upper()):
                        extracted_code = None
                    reprocessed_slots["course_code"] = extracted_code
                    reprocessed["slots"] = reprocessed_slots
                    course_result = self.processor.process(reprocessed)
                    course_result_slots = course_result.setdefault("slots", {})
                    parsed_student_id = parsed.get("slots", {}).get("student_id")
                    if parsed_student_id:
                        course_result_slots["student_id"] = parsed_student_id
                    return self._build_response(course_result)
                # Identity incomplete — fall through; let the partial identity block above handle it

        return self._build_response(result)
