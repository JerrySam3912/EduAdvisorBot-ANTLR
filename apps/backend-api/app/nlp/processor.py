from app.nlp.intents import (
    ASK_COURSE_ELIGIBILITY,
    ASK_COURSE_REQUIREMENTS,
    ASK_DROP_TIME,
    ASK_REGISTRATION_PLATFORM,
    ASK_REGISTRATION_TIME,
    ASK_PREREQUISITE_ONLY,
    ASK_PREVIOUS_ONLY,
    UNKNOWN,
)
from app.nlp.language_detection import detect_non_vietnamese
from app.nlp.parser import extract_course_code, infer_cohort_from_student_id
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
        raw_text = parsed.get("raw_text", text)
        slots = parsed.get("slots", {})
        intent = parsed.get("intent", UNKNOWN)

        # ============================================================
        # LANGUAGE DRIFT GUARD — block non-Vietnamese input immediately
        # ============================================================
        lang_check = detect_non_vietnamese(raw_text)
        if not lang_check["is_vietnamese"]:
            return self._handle_language_drift(
                text=raw_text,
                slots=slots,
                detected_lang=lang_check["detected_language"],
            )

        # Check if user just provided identity info without asking anything
        if intent == UNKNOWN and not slots.get("course_code"):
            known_cohort = slots.get("cohort") or slots.get("cohort_from_student_id")
            known_major = slots.get("major") or slots.get("major_from_student_id")
            known_student_id = slots.get("student_id")

            # Identity is "complete" when:
            # - has student_id AND that student_id yields both major AND cohort (full format like ITCSIU22001)
            # - OR has explicit cohort AND major (e.g. "K23 CS")
            # Note: 7-digit MSSV (2401036) only gives cohort, NOT major → NOT complete
            student_id_has_full_info = (
                bool(known_student_id)
                and bool(known_cohort)
                and bool(known_major)
            )
            explicit_has_full_info = bool(known_cohort and known_major)
            has_identity_complete = student_id_has_full_info or explicit_has_full_info

            lower_text = text.lower()
            asking_about_course = any(kw in lower_text for kw in (
                "môn ", "về môn", "tiên quyết", "prerequisite", "info", "thông tin",
                "là gì", "giới thiệu", "eligible", "drop", "đăng ký", "register",
                "tra ", "xem ", "tìm hiểu", "học được không",
                "muốn học", "học oop", "muốn hỏi", "tư vấn",
                "oop", " ai ", " ml ", " os ", "os được",
                "cần học gì trước", "học gì trước", "học được không",
                "tư vấn môn", "tư vấn về", "học gì", "môn nào",
                "operating system", "thuật toán", "cấu trúc dữ liệu",
                "machine learning", "data structures",
            ))

            # CASE A: User is asking about a course
            if asking_about_course:
                if not has_identity_complete:
                    # Identity incomplete → ask for identity FIRST before answering any course question
                    reply = "Bạn cho mình biết MSSV, hoặc tên ngành (NE/CE/CS/DS) và khóa (K21/K22/K23/K24) để mình tư vấn đúng chương trình nhé."
                    return self._build_response(
                        intent="ONBOARDING",
                        confidence=0.97,
                        reply=reply,
                        slots=slots,
                        missing_slots=["cohort_and_major"],
                        follow_up_question=reply,
                        data=None,
                    )
                # Identity complete → resolve course by name/alias, then route
                major = slots.get("major") or "cs"
                cohort = slots.get("cohort") or slots.get("cohort_from_student_id") or "k23"
                resolved = self.curriculum_service.resolve_course_by_name(
                    major=major, cohort=cohort, user_text=text,
                )
                course_code = None
                if resolved:
                    resolved_code = str(resolved.get("course_code", "")).upper()
                    slots = dict(slots)
                    slots["course_code"] = resolved_code
                    course_code = resolved_code
                if course_code:
                    if any(kw in lower_text for kw in ("tiên quyết", "prerequisite", "must pass", "cần pass", "bắt buộc trước")):
                        return self._handle_prerequisite_only(text=text, slots=slots, course_code=course_code)
                    if any(kw in lower_text for kw in ("học trước", "previous", "đã học", "học rồi")):
                        return self._handle_previous_only(text=text, slots=slots, course_code=course_code)
                    return self._handle_course_eligibility(text=text, slots=slots, course_code=course_code)
                # Course code unresolved → ask user
                return self._handle_missing_course_slot(intent=ASK_COURSE_REQUIREMENTS, slots=slots, text=text)

            # CASE B: User only provided identity (no course question)
            # Skip this block if user is asking about a course — let alias resolution handle it
            if not asking_about_course and (known_cohort or known_major or known_student_id):
                if has_identity_complete:
                    # Identity complete → acknowledge and ask what they need
                    reply_parts = []
                    if known_student_id:
                        reply_parts.append(f"MSSV: {known_student_id.upper()}")
                    if known_cohort:
                        reply_parts.append(f"Khóa: {known_cohort.upper()}")
                    if known_major:
                        reply_parts.append(f"Ngành: {known_major.upper()}")
                    return self._build_response(
                        intent="IDENTITY_ACKNOWLEDGED",
                        confidence=0.95,
                        reply=f"OK, mình đã ghi nhận: {', '.join(reply_parts)}. Bạn cần mình hỗ trợ gì?",
                        slots=slots,
                        missing_slots=[],
                        follow_up_question="Bạn cần mình hỗ trợ gì?",
                        data=None,
                    )

                # Identity incomplete → ask for missing piece
                if known_cohort and not known_major:
                    reply = f"Mình đã ghi nhận bạn học Khóa {known_cohort.upper()}. Bạn đang học ngành nào vậy? (NE/CE/CS/DS)"
                elif known_major and not known_cohort:
                    # Do NOT ask for course code — must have cohort before answering course questions.
                    reply = f"OK bạn học ngành {known_major.upper()}. Giờ bạn cho mình biết bạn khóa bao nhiêu? (K21/K22/K23/K24)?"
                else:
                    reply = "Bạn cho mình biết MSSV, hoặc tên ngành (NE/CE/CS/DS) và khóa (K21/K22/K23/K24) để mình tư vấn đúng chương trình nhé."
                return self._build_response(
                    intent="ONBOARDING",
                    confidence=0.97,
                    reply=reply,
                    slots=slots,
                    missing_slots=["cohort_and_major"],
                    follow_up_question=reply,
                    data=None,
                )

        course_code = slots.get("course_code") or self.curriculum_service.extract_course_code(text)
        # VALIDATION: verify course_code actually exists in SOME curriculum before using it.
        # This prevents ambiguous short codes ("CS", "DS", "CE", "NE") or invalid codes
        # from being treated as real course codes, causing misleading "course not found" errors.
        if course_code:
            from app.repositories.academic_repository import AcademicRepository
            repo = AcademicRepository()
            found = False
            for major in ["cs", "ne", "ds", "it-ce"]:
                for cohort in ["k21", "k22", "k23", "k24"]:
                    try:
                        if repo.get_course(major=major, cohort=cohort, course_code=course_code):
                            found = True
                            break
                    except FileNotFoundError:
                        continue
                if found:
                    break
            if not found:
                # Not a real curriculum code — clear it and let recovery handle it.
                # This sends the flow to _handle_missing_course_slot or ONBOARDING,
                # producing a meaningful "ask for course code" response instead of
                # a confusing "no data for CS in CS K21" error.
                course_code = None

        # ASK_DROP_TIME is special: always return the notice + link, even without course_code
        if intent == ASK_DROP_TIME and not course_code:
            return self._handle_drop_time(text=text, slots=slots, course_code=None)

        # IMPORTANT: Try to resolve course by NAME before giving up on missing course_code.
        # This handles cases like "muốn học về OOP", "tìm hiểu môn AI", "học operating system"
        # where the user uses course name/abbreviation instead of course code.
        if not course_code and intent in {
            ASK_COURSE_ELIGIBILITY, ASK_COURSE_REQUIREMENTS,
            ASK_PREREQUISITE_ONLY, ASK_PREVIOUS_ONLY,
            ASK_REGISTRATION_TIME, ASK_REGISTRATION_PLATFORM,
        }:
            major = slots.get("major") or "cs"
            cohort = slots.get("cohort") or slots.get("cohort_from_student_id") or "k23"
            resolved = self.curriculum_service.resolve_course_by_name(
                major=major, cohort=cohort, user_text=text,
            )
            if resolved:
                resolved_code = str(resolved.get("course_code", "")).upper()
                slots = dict(slots)  # shallow copy so we don't mutate parsed
                slots["course_code"] = resolved_code
                course_code = resolved_code

        if course_code:
            if intent == ASK_COURSE_ELIGIBILITY:
                return self._handle_course_eligibility(text=text, slots=slots, course_code=course_code)
            if intent == ASK_PREREQUISITE_ONLY:
                return self._handle_prerequisite_only(text=text, slots=slots, course_code=course_code)
            if intent == ASK_PREVIOUS_ONLY:
                # Smart routing: "cần học gì trước?" should show prerequisites if available,
                # fall back to previous, then generic course info.
                # Check prerequisites first (more important than "previous" for "học gì trước")
                req_check = self.curriculum_service.get_course_requirements(
                    major=slots.get("major") or "cs",
                    cohort=slots.get("cohort") or "k21",
                    course_code=course_code,
                )
                if req_check.get("found") and req_check.get("prerequisites"):
                    return self._handle_prerequisite_only(text=text, slots=slots, course_code=course_code)
                return self._handle_previous_only(text=text, slots=slots, course_code=course_code)
            if intent == ASK_REGISTRATION_TIME:
                return self._handle_registration_time(text=text, slots=slots, course_code=course_code)
            if intent == ASK_DROP_TIME:
                return self._handle_drop_time(text=text, slots=slots, course_code=course_code)
            if intent == ASK_REGISTRATION_PLATFORM:
                return self._handle_registration_platform(text=text, slots=slots, course_code=course_code)
            return self._handle_course_query(text=text, slots=slots, course_code=course_code)

        # BLOCK course questions when user has NO identity info.
        # If user asks about a course without providing who they are,
        # we MUST ask for identity first (cohort + major) before answering anything.
        has_identity = bool(
            slots.get("cohort")
            or slots.get("cohort_from_student_id")
            or slots.get("major")
            or slots.get("major_from_student_id")
            or slots.get("student_id")
        )
        if not has_identity and intent in {
            ASK_REGISTRATION_TIME, ASK_DROP_TIME, ASK_REGISTRATION_PLATFORM,
            ASK_COURSE_ELIGIBILITY, ASK_COURSE_REQUIREMENTS,
            ASK_PREREQUISITE_ONLY, ASK_PREVIOUS_ONLY,
        }:
            return self._build_response(
                intent="ONBOARDING",
                confidence=0.97,
                reply="Để mình tư vấn đúng, bạn cho mình biết bạn đang học ngành nào và khóa nào nhé. Ví dụ: 'mình học ngành CS khóa 22'.",
                slots=slots,
                missing_slots=["cohort_or_major"],
                follow_up_question="Bạn cho mình biết bạn đang học ngành nào và khóa nào nhé. Ví dụ: 'mình học ngành CS khóa 22'.",
                data=None,
            )

        if intent in {ASK_REGISTRATION_TIME, ASK_DROP_TIME, ASK_REGISTRATION_PLATFORM, ASK_COURSE_ELIGIBILITY, ASK_COURSE_REQUIREMENTS, ASK_PREREQUISITE_ONLY, ASK_PREVIOUS_ONLY}:
            return self._handle_missing_course_slot(intent=intent, slots=slots, text=text)

        if intent == "GREETING":
            return self._handle_greeting(text=text)

        # IMPORTANT: Try to resolve course by NAME for UNKNOWN intent too.
        # This handles cases like "muốn học về OOP", "tìm hiểu môn AI", "học operating system"
        # where the user uses course name/abbreviation instead of course code.
        if intent == UNKNOWN and not slots.get("course_code"):
            lower_text = text.lower()
            asking_about_course = any(kw in lower_text for kw in (
                "môn ", "về môn", "tiên quyết", "prerequisite", "info", "thông tin",
                "là gì", "giới thiệu", "eligible", "drop", "đăng ký", "register",
                "hỏi", "tra ", "xem ", "tìm hiểu", "học được không",
                "muốn học", "học oop", "muốn hỏi", "tư vấn",
                "oop", " ai ", " ml ", " os ", "os được",
                "cần học gì trước", "học gì trước", "học được không",
                "tư vấn môn", "tư vấn về", "học gì", "môn nào",
                "operating system", "thuật toán", "cấu trúc dữ liệu",
                "machine learning", "data structures",
            ))

            if asking_about_course and not has_identity:
                # User is asking about a course but we don't know who they are
                return self._build_response(
                    intent="ONBOARDING",
                    confidence=0.97,
                    reply="Để mình tư vấn đúng, bạn cho mình biết bạn đang học ngành nào và khóa nào nhé. Ví dụ: 'mình học ngành CS khóa 22'.",
                    slots=slots,
                    missing_slots=["cohort_or_major"],
                    follow_up_question="Bạn cho mình biết bạn đang học ngành nào và khóa nào nhé. Ví dụ: 'mình học ngành CS khóa 22'.",
                    data=None,
                )

            if asking_about_course:
                major = slots.get("major") or "cs"
                cohort = slots.get("cohort") or slots.get("cohort_from_student_id") or "k23"
                recovered = self.curriculum_service.resolve_course_by_name(major=major, cohort=cohort, user_text=text)
                if recovered:
                    recovered_code = str(recovered.get("course_code", "")).upper()
                    slots = dict(slots)
                    slots["course_code"] = recovered_code

                    if any(kw in lower_text for kw in ("tiên quyết", "prerequisite", "must pass", "cần pass", "bắt buộc trước")):
                        return self._handle_prerequisite_only(text=text, slots=slots, course_code=recovered_code)
                    if any(kw in lower_text for kw in ("học trước", "previous", "đã học", "học rồi")):
                        return self._handle_previous_only(text=text, slots=slots, course_code=recovered_code)
                    has_id = bool(slots.get("student_id") or slots.get("cohort") or slots.get("major"))
                    if has_id:
                        return self._handle_course_eligibility(text=text, slots=slots, course_code=recovered_code)
                    return self._handle_course_query(text=text, slots=slots, course_code=recovered_code)

                # Resolution failed — ask for course code (identity already confirmed)
                return self._handle_missing_course_slot(intent=ASK_COURSE_REQUIREMENTS, slots=slots, text=text)

        return self._build_response(
            intent=UNKNOWN,
            confidence=0.35,
            reply="Câu hỏi của bạn không nằm trong phạm vi mình hỗ trợ. Bạn có thể hỏi về môn học, tiên quyết, môn học trước, thời gian đăng ký hoặc drop môn nhé.",
            slots=slots,
            missing_slots=[],
            follow_up_question="Bạn muốn hỏi về môn nào?",
            data=None,
        )

    def _handle_missing_course_slot(self, *, intent: str, slots: dict, text: str) -> dict:
        major = slots.get("major") or "cs"
        cohort = slots.get("cohort") or slots.get("cohort_from_student_id") or "k23"

        # Check for contextual course references like "môn này", "môn đó"
        # These explicitly refer to the previously discussed course (from memory)
        contextual_refs = [
            "môn này", "môn đó", "môn kia",
            "nó", "mon nay", "mon do",
            "this course", "that course",
        ]
        has_contextual_ref = any(ref in text.lower() for ref in contextual_refs)
        session_course_code = slots.get("course_code")  # already set from memory by chat_service

        if has_contextual_ref and session_course_code:
            return self._route_with_course_code(intent=intent, text=text, slots=slots, course_code=session_course_code)

        # Try to resolve course by name/alias first (before asking user!)
        recovered_course = self.curriculum_service.resolve_course_by_name(
            major=major,
            cohort=cohort,
            user_text=text,
        )
        if recovered_course:
            recovered_code = str(recovered_course.get("course_code", "")).upper()
            return self._route_with_course_code(intent=intent, text=text, slots=slots, course_code=recovered_code)

        # Try to extract course code from user text (e.g. "môn IT017IU")
        extracted_code = self.curriculum_service.extract_course_code(text)
        if extracted_code:
            return self._route_with_course_code(intent=intent, text=text, slots=slots, course_code=extracted_code)

        # Try known course name patterns in text
        from app.services.curriculum_service import COURSE_ALIAS_MAP
        normalized = text.lower().strip()
        for alias in COURSE_ALIAS_MAP:
            if alias in normalized:
                recovered = self.curriculum_service.resolve_course_by_name(major=major, cohort=cohort, user_text=alias)
                if recovered:
                    code = str(recovered.get("course_code", "")).upper()
                    return self._route_with_course_code(intent=intent, text=text, slots=slots, course_code=code)

        # Fallback: ask user for course code
        missing_slots = ["course_code"]
        if not (slots.get("student_id") or slots.get("cohort") or slots.get("major")) and intent == ASK_COURSE_ELIGIBILITY:
            missing_slots.append("student_id_or_major_or_cohort")

        question = "Bạn cho mình biết mã môn học để mình tra nhé."
        if intent == ASK_COURSE_ELIGIBILITY:
            question = "Bạn cho mình biết mã môn học, MSSV, hoặc tên ngành + khóa để mình kiểm tra điều kiện học nhé."
        elif intent == ASK_PREREQUISITE_ONLY:
            question = "Bạn cho mình biết mã môn học để mình tra tiên quyết nhé."
        elif intent == ASK_PREVIOUS_ONLY:
            question = "Bạn cho mình biết mã môn học để mình tra môn học trước nhé."
        elif intent == ASK_REGISTRATION_TIME:
            question = "Bạn cho mình biết mã môn học và kỳ học để mình tra thời gian đăng ký nhé."
        elif intent == ASK_DROP_TIME:
            question = "Bạn cho mình biết mã môn học và kỳ học để mình tra thời gian drop nhé."
        elif intent == ASK_REGISTRATION_PLATFORM:
            question = "Bạn cho mình biết mã môn học để mình tra nền tảng đăng ký nhé."

        return self._build_response(
            intent=intent,
            confidence=0.8,
            reply=question,
            slots=slots,
            missing_slots=missing_slots,
            follow_up_question=question,
            data=None,
        )

    def _route_with_course_code(self, *, intent: str, text: str, slots: dict, course_code: str) -> dict:
        if intent == ASK_COURSE_ELIGIBILITY:
            return self._handle_course_eligibility(text=text, slots=slots, course_code=course_code)
        if intent == ASK_PREREQUISITE_ONLY:
            return self._handle_prerequisite_only(text=text, slots=slots, course_code=course_code)
        if intent == ASK_PREVIOUS_ONLY:
            return self._handle_previous_only(text=text, slots=slots, course_code=course_code)
        if intent == ASK_REGISTRATION_TIME:
            return self._handle_registration_time(text=text, slots=slots, course_code=course_code)
        if intent == ASK_DROP_TIME:
            return self._handle_drop_time(text=text, slots=slots, course_code=course_code)
        if intent == ASK_REGISTRATION_PLATFORM:
            return self._handle_registration_platform(text=text, slots=slots, course_code=course_code)
        return self._handle_course_query(text=text, slots=slots, course_code=course_code)

    def _handle_course_query(self, *, text: str, slots: dict, course_code: str) -> dict:
        cohort = slots.get("cohort") or infer_cohort_from_student_id(slots.get("student_id")) or "k21"
        major = slots.get("major") or "cs"
        course = self.repository.get_course(major=major, cohort=cohort, course_code=course_code)

        if not course:
            resolved_course = self.curriculum_service.resolve_course_by_name(major=major, cohort=cohort, user_text=text)
            if resolved_course:
                course_code = str(resolved_course.get("course_code", course_code))
                course = resolved_course

        if not course:
            # Try all other majors before giving up — course might exist in another major
            for try_major in ["cs", "ne", "ds", "it-ce"]:
                if try_major == major:
                    continue
                course = self.repository.get_course(major=try_major, cohort=cohort, course_code=course_code)
                if course:
                    major = try_major
                    slots = dict(slots)
                    slots["major"] = major
                    break
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
        if not slots.get("student_id") and not slots.get("cohort") and not slots.get("major"):
            return self._build_response(
                intent=ASK_COURSE_ELIGIBILITY,
                confidence=0.85,
                reply="Bạn cho mình MSSV, hoặc cho mình biết ngành + khóa để mình kiểm tra môn này có học được không nhé.",
                slots={"course_code": course_code},
                missing_slots=["course_code", "student_id_or_major_or_cohort"],
                follow_up_question="Bạn cho mình MSSV hoặc ngành + khóa nhé.",
                data=None,
            )

        user_cohort = slots.get("cohort") or infer_cohort_from_student_id(slots.get("student_id")) or "k21"
        user_major = slots.get("major") or "cs"
        cohort = user_cohort
        major = user_major
        requirements = self.curriculum_service.get_course_requirements(major=major, cohort=cohort, course_code=course_code)

        if not requirements.get("found"):
            # Course not found in user's curriculum — try to resolve alias in user's curriculum first.
            # If still not found, try all other majors/cohorts.
            # CRITICAL: Only change major/cohort if the course genuinely doesn't exist in user's curriculum.
            # This prevents "OOP" from being resolved to DS/K21 when user said CS/K22.

            # Step 1: Try resolving with user's major and ALL cohorts
            for try_cohort in ["k21", "k22", "k23", "k24"]:
                if try_cohort == user_cohort:
                    continue
                resolved = self.curriculum_service.resolve_course_by_name(
                    major=user_major, cohort=try_cohort, user_text=text,
                )
                if resolved:
                    real_code = str(resolved.get("course_code", "")).upper()
                    req = self.curriculum_service.get_course_requirements(
                        major=user_major, cohort=try_cohort, course_code=real_code,
                    )
                    if req.get("found"):
                        course_code = real_code
                        cohort = try_cohort
                        requirements = req
                        slots = dict(slots)
                        slots["cohort"] = cohort
                        break
            else:
                # Step 2: Course not found in user's major at all — try all other majors/cohorts
                for try_major in ["cs", "ne", "ds", "it-ce"]:
                    if try_major == user_major:
                        continue
                    for try_cohort in ["k21", "k22", "k23", "k24"]:
                        resolved = self.curriculum_service.resolve_course_by_name(
                            major=try_major, cohort=try_cohort, user_text=text,
                        )
                        if resolved:
                            real_code = str(resolved.get("course_code", "")).upper()
                            req = self.curriculum_service.get_course_requirements(
                                major=try_major, cohort=try_cohort, course_code=real_code,
                            )
                            if req.get("found"):
                                course_code = real_code
                                major = try_major
                                cohort = try_cohort
                                requirements = req
                                slots = dict(slots)
                                slots["major"] = major
                                slots["cohort"] = cohort
                                break
                    else:
                        continue
                    break

        if not requirements.get("found"):
            # Step 2: Try raw course code in all majors
            found_in_other = None
            for try_major in ["cs", "ne", "ds", "it-ce"]:
                req = self.curriculum_service.get_course_requirements(major=try_major, cohort=cohort, course_code=course_code)
                if req.get("found"):
                    found_in_other = (try_major, req)
                    break
            if found_in_other:
                try_major, requirements = found_in_other
                slots = dict(slots)
                slots["major"] = try_major
            else:
                return self._build_response(
                    intent=ASK_COURSE_ELIGIBILITY,
                    confidence=0.83,
                    reply=f"Mình chưa có dữ liệu để kiểm tra điều kiện học cho môn {course_code} trong {major.upper()} {cohort.upper()}.",
                    slots={"course_code": course_code, "major": major, "cohort": cohort},
                    missing_slots=[],
                    follow_up_question=None,
                    data=None,
                )

        reply = self._format_eligibility_reply(
            requirements,
            cohort=user_cohort,
            student_id=slots.get("student_id"),
        )
        return self._build_response(
            intent=ASK_COURSE_ELIGIBILITY,
            confidence=0.95,
            reply=reply,
            slots={"course_code": course_code, **slots},
            missing_slots=[],
            follow_up_question=None,
            data=requirements,
        )

    def _handle_prerequisite_only(self, *, text: str, slots: dict, course_code: str) -> dict:
        """
        Handle ASK_PREREQUISITE_ONLY intent.
        User asks specifically about 'prerequisites' (must PASS).
        """
        cohort = slots.get("cohort") or infer_cohort_from_student_id(slots.get("student_id")) or "k21"
        major = slots.get("major") or "cs"
        requirements = self.curriculum_service.get_course_requirements(major=major, cohort=cohort, course_code=course_code)

        if not requirements.get("found"):
            # Try all other majors before giving up
            for try_major in ["cs", "ne", "ds", "it-ce"]:
                if try_major == major:
                    continue
                req = self.curriculum_service.get_course_requirements(major=try_major, cohort=cohort, course_code=course_code)
                if req.get("found"):
                    requirements = req
                    major = try_major
                    slots = dict(slots)
                    slots["major"] = major
                    break
            if not requirements.get("found"):
                return self._build_response(
                    intent=ASK_PREREQUISITE_ONLY,
                    confidence=0.83,
                    reply=f"Mình chưa có dữ liệu về tiên quyết cho môn {course_code} trong {major.upper()} {cohort.upper()}.",
                    slots={"course_code": course_code, "major": major, "cohort": cohort},
                    missing_slots=[],
                    follow_up_question=None,
                    data=None,
                )

        prerequisites = requirements.get("prerequisites", [])
        reply = self._format_prerequisite_only_reply(course_code, prerequisites, cohort)
        return self._build_response(
            intent=ASK_PREREQUISITE_ONLY,
            confidence=0.96,
            reply=reply,
            slots={"course_code": course_code, "major": major, "cohort": cohort},
            missing_slots=[],
            follow_up_question=None,
            data={"prerequisites": prerequisites},
        )

    def _handle_previous_only(self, *, text: str, slots: dict, course_code: str) -> dict:
        """
        Handle ASK_PREVIOUS_ONLY intent.
        User asks specifically about 'previous' courses (only need to have STUDIED).
        """
        cohort = slots.get("cohort") or infer_cohort_from_student_id(slots.get("student_id")) or "k21"
        major = slots.get("major") or "cs"
        requirements = self.curriculum_service.get_course_requirements(major=major, cohort=cohort, course_code=course_code)

        if not requirements.get("found"):
            # Try all other majors before giving up
            for try_major in ["cs", "ne", "ds", "it-ce"]:
                if try_major == major:
                    continue
                req = self.curriculum_service.get_course_requirements(major=try_major, cohort=cohort, course_code=course_code)
                if req.get("found"):
                    requirements = req
                    major = try_major
                    slots = dict(slots)
                    slots["major"] = major
                    break
            if not requirements.get("found"):
                return self._build_response(
                    intent=ASK_PREVIOUS_ONLY,
                    confidence=0.83,
                    reply=f"Mình chưa có dữ liệu về môn học trước cho môn {course_code} trong {major.upper()} {cohort.upper()}.",
                    slots={"course_code": course_code, "major": major, "cohort": cohort},
                    missing_slots=[],
                    follow_up_question=None,
                    data=None,
                )

        previous = requirements.get("previous", [])
        reply = self._format_previous_only_reply(course_code, previous, cohort)
        return self._build_response(
            intent=ASK_PREVIOUS_ONLY,
            confidence=0.96,
            reply=reply,
            slots={"course_code": course_code, "major": major, "cohort": cohort},
            missing_slots=[],
            follow_up_question=None,
            data={"previous": previous},
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
        edusoft_link = "https://edusoftweb.hcmiu.edu.vn/default.aspx?page=chitietthongtin&id=1613"

        if notice:
            windows = notice.get("time_windows", [])
            if len(windows) == 2:
                reply = (
                    f"Theo thông báo Edusoft, thời gian hiệu chỉnh / drop môn học {notice['semester']} là:\n"
                    f"  • Đợt 1: {windows[0]['from']}–{windows[0]['to']}, "
                    f"từ ngày {windows[0]['days'][0]} đến {windows[0]['days'][-1]}\n"
                    f"  • Đợt 2: {windows[1]['from']}–{windows[1]['to']}, "
                    f"ngày {windows[1]['days'][0]}\n\n"
                    f"Xem chi tiết: {edusoft_link}"
                )
            else:
                reply = (
                    f"Theo thông báo Edusoft, thời gian hiệu chỉnh / drop môn học {notice['semester']} là: "
                    f"{windows[0]['from']}–{windows[0]['to']} từ ngày {windows[0]['days'][0]} đến {windows[0]['days'][-1]}.\n\n"
                    f"Xem chi tiết: {edusoft_link}"
                )
            return self._build_response(
                intent=ASK_DROP_TIME,
                confidence=0.95,
                reply=reply,
                slots={"course_code": course_code, **slots},
                missing_slots=[],
                follow_up_question=None,
                data=notice,
            )

        # No notice data available — provide the edusoft link
        return self._build_response(
            intent=ASK_DROP_TIME,
            confidence=0.86,
            reply=(
                f"Mình chưa có lịch drop môn trong dữ liệu hiện tại. "
                f"Bạn có thể tra trực tiếp tại Edusoft: {edusoft_link}"
            ),
            slots={"course_code": course_code, **slots},
            missing_slots=[],
            follow_up_question=None,
            data={"fallback_url": edusoft_link},
        )

    def _handle_registration_platform(self, *, text: str, slots: dict, course_code: str) -> dict:
        return self._build_response(
            intent=ASK_REGISTRATION_PLATFORM,
            confidence=0.9,
            reply=f"Bạn đăng ký môn {course_code} trên cổng đăng ký của trường (theo quy định từng kỳ). Nếu bạn muốn, mình có thể tra theo ngành/kỳ cụ thể.",
            slots={"course_code": course_code, **slots},
            missing_slots=[],
            follow_up_question=None,
            data={"platform": "university_registration_portal"},
        )

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
        previous = requirements.get("previous", [])

        if not prerequisites and not previous:
            return f"Theo data {cohort.upper()}, môn {requirements['course_code']} không có điều kiện bắt buộc - bạn có thể đăng ký được."

        parts = []
        if prerequisites:
            parts.append(f"Tiên quyết (phải PASS): {', '.join(prerequisites)}")
        if previous:
            parts.append(f"Học trước (chỉ cần đã học): {', '.join(previous)}")

        return f"Theo data {cohort.upper()}, để học {requirements['course_code']}: " + ". ".join(parts) + "."

    @staticmethod
    def _format_prerequisite_only_reply(course_code: str, prerequisites: list, cohort: str) -> str:
        if not prerequisites:
            return f"Môn {course_code} không có tiên quyết bắt buộc trong {cohort.upper()}."
        return (
            f"Để học môn {course_code}, bạn phải PASS các môn tiên quyết sau: "
            f"{', '.join(prerequisites)}."
        )

    @staticmethod
    def _format_previous_only_reply(course_code: str, previous: list, cohort: str) -> str:
        if not previous:
            return f"Môn {course_code} không có môn học trước (previous) trong {cohort.upper()}."
        return (
            f"Trước khi học môn {course_code}, bạn cần đã học qua (rớt vẫn được) các môn sau: "
            f"{', '.join(previous)}."
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

    def _handle_language_drift(self, *, text: str, slots: dict, detected_lang: str | None = None) -> dict:
        """
        Handle when user uses non-Vietnamese language.
        This chatbot is strictly for Vietnamese users only.
        """
        lang_display = {
            "chinese": "tiếng Trung Quốc",
            "english": "tiếng Anh",
            "malay": "tiếng Malay",
            "german": "tiếng Đức",
        }.get(detected_lang or "", "ngôn ngữ khác")

        reply = (
            f"Mình chỉ hỗ trợ tiếng Việt thôi nhé. "
            f"Bạn vừa dùng {lang_display} — mình không hiểu được. "
            f"Bạn hỏi lại bằng tiếng Việt giúp mình nhé!"
        )

        return self._build_response(
            intent="LANGUAGE_DRIFT",
            confidence=0.99,
            reply=reply,
            slots=slots,
            missing_slots=[],
            follow_up_question="Bạn hỏi mình bằng tiếng Việt nhé! Ví dụ: 'tiên quyết IT017IU là gì?'",
            data={"detected_language": detected_lang, "original_text": text[:100]},
        )

    def _handle_greeting(self, *, text: str) -> dict:
        """
        Handle simple greetings with full onboarding request.
        """
        return self._build_response(
            intent="GREETING",
            confidence=0.98,
            reply="Xin chào! Mình là EduAdvisorBot, sẵn sàng tư vấn về môn học cho bạn. Bạn cho mình biết MSSV (ví dụ: ITCSIU22009) hoặc tên ngành (NE/CE/CS/DS) và khóa (K21/K22/K23/K24) nhé.",
            slots={},
            missing_slots=["student_id_or_cohort_and_major"],
            follow_up_question="Bạn cho mình biết MSSV, hoặc tên ngành và khóa học nhé.",
            data=None,
        )
