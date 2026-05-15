# Intent & Slot Mapping

Document này mô tả mapping giữa ANTLR grammar và intent/slots được sử dụng trong chatbot.

## Supported Languages

Chỉ hỗ trợ **tiếng Việt có dấu** và **tiếng Anh**. Pinyin (không dấu) không được hỗ trợ.

## Grammar Structure

```
query
├── helpQuery          -> HELP
├── greetingQuery      -> GREETING
├── eligibilityQuery    -> ASK_COURSE_ELIGIBILITY
├── courseQuery
│   ├── prerequisiteQuery -> ASK_PREREQUISITE_ONLY
│   ├── previousQuery     -> ASK_PREVIOUS_ONLY
│   └── courseInfoQuery  -> ASK_COURSE_REQUIREMENTS
├── dropQuery         -> ASK_DROP_TIME
└── registrationQuery -> ASK_REGISTRATION_TIME / ASK_REGISTRATION_PLATFORM
```

## Intent Definitions

| Intent | Mô tả | Ví dụ input |
|--------|-------|-------------|
| `ASK_COURSE_ELIGIBILITY` | Hỏi đủ điều kiện học môn không | "học IT017IU được không?", "eligibility IT017IU" |
| `ASK_PREREQUISITE_ONLY` | Hỏi về tiên quyết (phải PASS) | "tiên quyết của IT017IU là gì?", "must pass IT017IU" |
| `ASK_PREVIOUS_ONLY` | Hỏi về môn học trước (chỉ cần đã học) | "học trước môn IT017IU là gì?", "previous IT017IU" |
| `ASK_COURSE_REQUIREMENTS` | Hỏi thông tin chung về môn | "IT017IU là môn gì?", "thông tin IT017IU" |
| `ASK_REGISTRATION_TIME` | Hỏi thời gian đăng ký | "khi nào đăng ký?" |
| `ASK_DROP_TIME` | Hỏi thời gian drop môn | "khi nào drop được?", "hủy môn IT017IU" |
| `ASK_REGISTRATION_PLATFORM` | Hỏi nền tảng đăng ký | "đăng ký ở đâu?" |
| `HELP` | Lệnh help | "help", "gợi ý" |
| `GREETING` | Lời chào | "xin chào", "hello" |

## Slots

| Slot | Mô tả | Nguồn |
|------|-------|--------|
| `course_code` | Mã môn học | ANTLR grammar (COURSE_CODE token) |
| `cohort` | Khóa học (k21, k22...) | Regex hoặc student_id inference |
| `major` | Ngành học (cs, ne, ds...) | student_id inference |
| `student_id` | MSSV | Input hoặc session |
| `semester_code` | Kỳ học (SP25, FA25...) | Regex |

## Eligibility Policy

Theo quy ước của dự án:

| Loại | Yêu cầu | Ví dụ |
|------|----------|--------|
| `prerequisites` | Phải **PASS** môn trước | Nét liền trên sơ đồ |
| `previous` | Chỉ cần **đã học** (rớt vẫn được) | Nét đứt trên sơ đồ |
| `co_requisites` | Học cùng kỳ | Học song song |

## Grammar Tokens

### Eligibility Tokens
```
ELIGIBILITY_ASK: eligibility, elibible, đủ điều kiện, điều kiện để học, điều kiện
ELIGIBLE_ASK: có được không, được không
CAN_TAKE_ASK: học được, được học, có thể học, can take, take this
ELIGIBILITY_WORKS: ok đấy, ok rồi, ok được, ổn đấy, ổn rồi
ELIGIBILITY_QUESTION_WORDS: không, ko, chứ
```

### Prerequisite Tokens (must PASS)
```
PREREQUISITE_ASK: prerequisite, tiên quyết, môn tiên quyết, điều kiện tiên quyết
MUST_PASS_ASK: must pass, need to pass, cần pass, phải đậu, bắt buộc
TIEN_QUYET_ASK: tiên quyết của, prerequisite of, cần học trước, phải học trước
PREREQUISITE_QUESTION_WORDS: gì, nào, trước
```

### Previous Tokens (only need to have studied)
```
PREVIOUS_ASK: previous, prev, học trước đó, nối tiếp
DA_HOC_ASK: đã học, học rồi, đã học môn, đã học được
HOC_TRUOC_ASK: học trước, học trước môn, học qua môn
PREVIOUS_QUESTION_WORDS: nào, gì, không
```

## Parser Pipeline

```
User Input
    │
    ▼
ANTLR Parser (CourseQuery.g4)
    │
    ├── Parse thành công
    │   └── IntentSlotExtractor visitor
    │       └── Extract intent + course_code + semester_code
    │
    └── Parse thất bại (fallback)
        └── Regex-based classify_intent()
```

## Test Cases

| Input | Intent | Slots |
|-------|--------|-------|
| "học IT017IU được không" | ASK_COURSE_ELIGIBILITY | {course_code: IT017IU} |
| "tiên quyết của IT017IU là gì" | ASK_PREREQUISITE_ONLY | {course_code: IT017IU} |
| "học trước IT017IU là môn gì" | ASK_PREVIOUS_ONLY | {course_code: IT017IU} |
| "IT017IU là môn gì" | ASK_COURSE_REQUIREMENTS | {course_code: IT017IU} |
| "khi nào đăng ký" | ASK_REGISTRATION_TIME | {} |
| "khi nào drop được" | ASK_DROP_TIME | {} |
| "drop IT017IU SU26" | ASK_DROP_TIME | {course_code: IT017IU, semester_code: SU26} |
| "thời gian drop môn" | ASK_DROP_TIME | {} |
| "help" | HELP | {} |
