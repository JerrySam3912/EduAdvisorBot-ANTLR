# Test Suite Report — EduAdvisorBot-ANTLR

**Total: 119 tests | Status: 119 passed, 0 failed**

Generated: Saturday, May 16, 2026

---

## 1. Grammar Ambiguity Tests (`test_grammar_ambiguity.py`) — 9 tests

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_question_word_context` | Question word "gì" không bị parse thành GREETING |
| 2 | `test_no_prefix_no_match` | Input không có prefix không khớp grammar |
| 3 | `test_prefix_disambiguation` | Prefix disambiguates giữa các loại query |
| 4 | `test_drop_vs_registration` | "drop" vs "registration" không bị nhầm |
| 5 | `test_bare_course_code_ambiguity` | Mã môn đứng riêng không bị ambiguous |
| 6 | `test_previously_ambiguous` | "previously" không bị nhầm với prerequisite |
| 7 | `test_greeting_with_trailing_words` | Greeting có trailing words vẫn match |
| 8 | `test_greeting_not_confused_with_course_info` | Greeting không bị nhầm với course info |
| 9 | `test_semester_with_queries` | Semester token hoạt động đúng trong queries |

---

## 2. Language Drift Tests (`test_language_drift.py`) — 17 tests

### DetectNonVietnamese (9 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 10 | `test_vietnamese_returns_true` | Tiếng Việt có dấu → is_vietnamese = True |
| 11 | `test_chinese_characters_detected` | Ký tự Trung Quốc → phát hiện tiếng Trung |
| 12 | `test_chinese_mixed_with_vietnamese` | Trung + Việt → bị chặn |
| 13 | `test_chinese_pinyin_single_is_ignored` | Pinyin đơn lẻ không bị chặn |
| 14 | `test_chinese_pinyin_pair_detected` | Pinyin ghép → bị chặn |
| 15 | `test_chinese_pinyin_multiple` | Nhiều pinyin → bị chặn |
| 16 | `test_english_only_detected` | Tiếng Anh thuần → bị chặn |
| 17 | `test_english_mixed_with_vietnamese_accepted` | Việt + Anh keywords → được chấp nhận |
| 18 | `test_pure_vietnamese_with_diacritics` | Việt có dấu → hợp lệ |

### ValidateResponseLanguage (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 19 | `test_vietnamese_response_valid` | Response tiếng Việt → hợp lệ |
| 20 | `test_chinese_in_response_invalid` | Response có chữ Trung → invalid |
| 21 | `test_empty_response_valid` | Response rỗng → vẫn hợp lệ |

### ProcessorLanguageDriftGuard (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 22 | `test_chinese_input_returns_language_drift` | Tiếng Trung → LANGUAGE_DRIFT intent |
| 23 | `test_chinese_pinyin_returns_language_drift` | Pinyin → LANGUAGE_DRIFT intent |
| 24 | `test_pure_english_returns_language_drift` | Tiếng Anh thuần → LANGUAGE_DRIFT intent |
| 25 | `test_vietnamese_input_works_normally` | Tiếng Việt → không bị chặn |
| 26 | `test_mixed_vietnamese_with_english_keywords_works` | Việt + keyword Anh → hoạt động bình thường |

### ChatServiceOutputSanitization (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 27 | `test_vietnamese_response_passed_through` | Response VN giữ nguyên |
| 28 | `test_chinese_input_blocked_at_processor` | Input Trung bị chặn ở processor |
| 29 | `test_normal_conversation_always_vietnamese` | Conversation luôn trả lời tiếng Việt |

---

## 3. NLP Flow Tests (`test_nlp_flow.py`) — 6 tests

| # | Test Name | Description |
|---|-----------|-------------|
| 30 | `test_infer_cohort_from_student_id` | Infer cohort từ MSSV (ITCSIU22001 → K22) |
| 31 | `test_course_query_it094_previous` | IT094IU previous courses → đúng dữ liệu |
| 32 | `test_course_query_it159_previous` | IT159IU previous courses → đúng dữ liệu |
| 33 | `test_course_query_pe019_previous` | PE019IU previous courses → đúng dữ liệu |
| 34 | `test_course_query_it017_prerequisites` | IT017IU prerequisites → IT013IU, IT089IU |
| 35 | `test_course_query_it093_prerequisites` | IT093IU prerequisites → IT069IU, IT079IU |

---

## 4. NLP Pipeline Tests (`test_nlp_pipeline.py`) — 78 tests

### NormalizeText (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 36 | `test_strips_whitespace` | Strip khoảng trắng thừa |
| 37 | `test_lowercase` | Lowercase nội dung |
| 38 | `test_preserves_content` | Giữ nguyên nội dung chữ |

### ExtractSemesterCode (10 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 39 | `test_sp25_format` | "SP25" → SP25 |
| 40 | `test_su_25_format` | "SU-25" → SU25 |
| 41 | `test_fa_24_format` | "FA24" → FA24 |
| 42 | `test_no_match` | Không match → None |
| 43 | `test_summer_variations` | "summer", "sum", "su" |
| 44 | `test_spring_variations` | "spring", "spr", "sp" |
| 45 | `test_fall_variations` | "fall", "fal", "fa" |
| 46 | `test_hkiii_variations` | "HKIII", "học kỳ 3" |
| 47 | `test_hoc_ky_he_variations` | "học kỳ hè" |
| 48 | `test_drop_with_semester` | "drop FA25" → extract được semester |

### ExtractExplicitCohort (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 49 | `test_k21_format` | "K21", "khóa 21", "k21" |
| 50 | `test_khoa_format` | "khóa 22" |
| 51 | `test_direct_format` | Format trực tiếp |

### ExtractCourseCode (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 52 | `test_it_format` | "IT017IU" → IT017IU |
| 53 | `test_cs_format` | "CS101" → CS101 |
| 54 | `test_ne_format` | "NE001" → NE001 |
| 55 | `test_no_match` | Không match → None |

### StudentIdExtraction (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 56 | `test_itcsiu_format` | "ITCSIU22001" → ITCSIU22001 |
| 57 | `test_ititwe_format` | "ITITWE22001" → ITITWE22001 |
| 58 | `test_itdsiu_format` | "ITDSIU22001" → ITDSIU22001 |
| 59 | `test_itceiu_format` | "ITCEIU22001" → ITCEIU22001 |
| 60 | `test_no_student_id` | Không có MSSV → None |

### AntlrClassify (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 61 | `test_eligibility_intent` | "eligibility IT017IU" → ASK_COURSE_ELIGIBILITY |
| 62 | `test_prerequisite_intent` | "prerequisite IT017IU" → ASK_PREREQUISITE_ONLY |
| 63 | `test_previous_intent` | "previous IT017IU" → ASK_PREVIOUS_ONLY |
| 64 | `test_help_intent` | "help" → HELP |

### ParseCommand (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 65 | `test_parses_eligibility_correctly` | Parse eligibility query đúng |
| 66 | `test_parses_prerequisite_correctly` | Parse prerequisite query đúng |
| 67 | `test_parses_previous_correctly` | Parse previous query đúng |
| 68 | `test_extracts_student_id_slots` | Extract MSSV vào slots |
| 69 | `test_unknown_returns_unknown` | Query lạ → UNKNOWN intent |

### CommandProcessor (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 70 | `test_course_eligibility_response` | Eligibility → reply đúng format |
| 71 | `test_prerequisite_only_response` | Prerequisite only → reply đúng |
| 72 | `test_previous_only_response` | Previous only → reply đúng |
| 73 | `test_missing_course_asks_for_slot` | Thiếu course → hỏi mã môn |
| 74 | `test_unknown_intent_response` | Intent lạ → fallback reply |

### DropTimeIntentDetection (8 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 75 | `test_drop_time_with_course_and_semester` | "drop IT017IU SP25" |
| 76 | `test_drop_time_standalone` | "drop" đứng riêng |
| 77 | `test_drop_time_khi_nao_drop` | "khi nào drop" |
| 78 | `test_drop_time_with_semicolon` | "drop;" |
| 79 | `test_drop_time_huy_mon` | "hủy môn" |
| 80 | `test_drop_time_rut_mon` | "rút môn" |
| 81 | `test_drop_time_semester_first` | Semester trước course code |
| 82 | `test_drop_time_no_ambiguous_bare_course_code` | Bare course code không ambiguous |

### DropTimeProcessor (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 83 | `test_drop_time_with_semester_gives_notice` | Có semester → trả notice |
| 84 | `test_drop_time_without_semester_asks_for_semester` | Thiếu semester → hỏi |
| 85 | `test_drop_time_without_course_or_semester_asks_for_both` | Thiếu cả hai → hỏi cả hai |
| 86 | `test_drop_query_then_semester_only` | Flow: drop query → semester only |

### IntentDetection (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 87 | `test_eligibility_patterns` | Eligibility keywords detection |
| 88 | `test_prerequisite_patterns` | Prerequisite keywords detection |
| 89 | `test_previous_patterns` | Previous keywords detection |

### CourseAliasResolution (8 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 90 | `test_oop_alias_resolves` | "OOP", "oop" → IT069IU |
| 91 | `test_ai_alias_resolves` | "AI", "ai" → IT159IU |
| 92 | `test_ml_alias_resolves` | "ML", "machine learning" → IT158IU |
| 93 | `test_operating_system_alias_resolves` | "OS", "operating system" → IT017IU |
| 94 | `test_algorithms_alias_resolves` | "algorithm", "dsa" → IT013IU |
| 95 | `test_dsa_alias_resolves` | "data structures" → IT013IU |
| 96 | `test_machine_learning_alias_resolves` | "machine learning" → IT158IU |
| 97 | `test_vietnamese_alias_resolves` | Alias tiếng Việt |

### EdgeCases (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 98 | `test_empty_input` | Input rỗng → xử lý được |
| 99 | `test_whitespace_only` | Chỉ khoảng trắng → xử lý được |
| 100 | `test_course_code_case_insensitive` | "it017iu" → IT017IU |
| 101 | `test_multiple_course_codes_takes_first` | Nhiều mã → lấy cái đầu |

### MssvExtractionFromMessage (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 102 | `test_extracts_mssv_from_plain_text` | MSSV đứng riêng |
| 103 | `test_extracts_mssv_with_prefix` | MSSV có prefix |
| 104 | `test_extracts_mssv_from_sentence` | MSSV trong câu |
| 105 | `test_extracts_mssv_lowercase` | MSSV viết thường |
| 106 | `test_returns_none_when_no_mssv` | Không có MSSV → None |

### OnboardingWithMssvInMessage (2 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 107 | `test_onboarding_detects_mssv_from_message` | Phát hiện MSSV trong message |
| 108 | `test_onboarding_still_works_without_mssv` | Không có MSSV → vẫn hoạt động |

---

## 5. Onboarding Flow Tests (`test_onboarding_flow.py`) — 11 tests

| # | Test Name | Description |
|---|-----------|-------------|
| 109 | `test_onboarding_asks_for_mssv_or_cohort_when_missing` | Thiếu identity → hỏi MSSV/cohort |
| 110 | `test_onboarding_stores_cohort_and_reuses_it` | Lưu cohort và tái sử dụng |
| 111 | `test_mssv_only_triggers_onboarding_asking_for_major` | Chỉ có MSSV → hỏi major |
| 112 | `test_major_only_asks_for_cohort_not_course` | Chỉ có major → hỏi cohort, không hỏi course |
| 113 | `test_standalone_cs_major_not_treated_as_course_code` | "CS" không bị nhầm thành course code |
| 114 | `test_standalone_ne_major_extracted` | "NE" được extract đúng |
| 115 | `test_cs_major_with_explicit_knowledge_still_asks_cohort` | CS + knowledge → vẫn hỏi cohort |
| 116 | `test_major_only_asking_about_course_still_asks_for_cohort` | Hỏi về course + có major → vẫn hỏi cohort |
| 117 | `test_complete_identity_acknowledged_then_ask_course` | Identity đủ → acknowledge rồi hỏi course |

---

## 6. Session Memory Tests (`test_session_memory.py`) — 1 test

| # | Test Name | Description |
|---|-----------|-------------|
| 118 | `test_session_memory_reuses_last_course_code` | Memory giữ last_course_code cho "môn này" |
| 119 | *(reserved for future)* | |

---

## Summary

| Module | File | Tests |
|--------|------|-------|
| Grammar Ambiguity | `test_grammar_ambiguity.py` | 9 |
| Language Drift | `test_language_drift.py` | 17 |
| NLP Flow | `test_nlp_flow.py` | 6 |
| NLP Pipeline | `test_nlp_pipeline.py` | 78 |
| Onboarding Flow | `test_onboarding_flow.py` | 11 |
| Session Memory | `test_session_memory.py` | 1 |
| **Total** | | **119** |

**Result: 119/119 passed** ✅
