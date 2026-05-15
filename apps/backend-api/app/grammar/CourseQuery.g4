grammar CourseQuery;

// ============================================
// TOP-LEVEL QUERY PARSER
// ============================================
// Grammar is intentionally MINIMAL.
// Complex Vietnamese phrases are handled by regex fallback in parser.py.
// Only unambiguous English keywords are in the grammar.
// ============================================

query
    : helpQuery EOF
    | greetingQuery EOF
    | eligibilityQuery EOF
    | courseQuery EOF
    | dropQuery EOF
    | registrationQuery EOF
    ;

// ============================================
// GREETING
// ============================================
greetingQuery
    : GREETING
    ;

// ============================================
// HELP
// ============================================
helpQuery
    : HELP
    | HELP_ASK
    ;

// ============================================
// ELIGIBILITY
// ============================================
eligibilityQuery
    : ELIGIBLE_PREFIX COURSE_CODE eligibleSuffix?
    | ELIGIBLE_PREFIX COURSE_CODE
    ;

eligibleSuffix
    : ELIGIBLE_QUESTION+
    ;

// ============================================
// COURSE INFO / PREREQUISITE / PREVIOUS
// ============================================
courseQuery
    : prerequisiteQuery
    | previousQuery
    | courseInfoQuery
    ;

prerequisiteQuery
    : PREREQUISITE_PREFIX COURSE_CODE PREREQUISITE_SUFFIX?
    | PREREQUISITE_PREFIX COURSE_CODE
    ;

previousQuery
    : PREVIOUS_PREFIX COURSE_CODE
    ;

courseInfoQuery
    : INFO_PREFIX COURSE_CODE
    | WHAT_PREFIX COURSE_CODE
    ;

// ============================================
// DROP TIME
// ============================================
dropQuery
    : DROP_PREFIX COURSE_CODE? SEMESTER? DROP_SUFFIX?
    | DROP_PREFIX COURSE_CODE SEMESTER
    | DROP_PREFIX COURSE_CODE
    | DROP_PREFIX SEMESTER
    | DROP_PREFIX SEMESTER COURSE_CODE
    ;

// ============================================
// REGISTRATION
// ============================================
registrationQuery
    : REG_PREFIX COURSE_CODE?
    | REG_PREFIX COURSE_CODE
    ;

// ============================================
// LEXER TOKENS
// All tokens are explicit lexer rules for reliable tokenization.
// ============================================

// --- GREETING ---
GREETING
    : 'hello'
    | 'hey'
    | 'good morning'
    | 'good afternoon'
    ;

// --- HELP ---
HELP
    : 'help'
    ;

HELP_ASK
    : 'what can you do'
    | 'who are you'
    | 'how can you help'
    ;

// --- ELIGIBILITY ---
ELIGIBLE_PREFIX
    : 'eligibility'
    | 'eligible'
    | 'can take'
    | 'can i take'
    ;

ELIGIBLE_QUESTION
    : '?'
    ;

// --- PREREQUISITE ---
PREREQUISITE_PREFIX
    : 'prerequisite'
    | 'prerequisites'
    | 'must pass'
    ;

PREREQUISITE_SUFFIX
    : '?'
    ;

// --- PREVIOUS ---
PREVIOUS_PREFIX
    : 'previous'
    | 'prev'
    | 'prerequisite for'
    ;

// --- COURSE INFO ---
INFO_PREFIX
    : 'info'
    | 'information'
    | 'info of'
    | 'information about'
    ;

WHAT_PREFIX
    : 'what is'
    | 'what are'
    | 'which is'
    ;

// --- DROP ---
DROP_PREFIX
    : 'drop'
    | 'withdraw'
    | 'cancel'
    ;

DROP_SUFFIX
    : '?'
    ;

// --- REGISTRATION ---
REG_PREFIX
    : 'registration'
    | 'register'
    | 'enroll'
    ;

// ============================================
// TOKEN PATTERNS
// ============================================

COURSE_CODE
    : [A-Z][A-Z] DIGIT DIGIT DIGIT 'IU'?
    | [A-Z][A-Z][A-Z][A-Z] DIGIT DIGIT DIGIT 'IU'?
    ;

fragment LETTER : [a-zA-Z];
fragment DIGIT  : [0-9];

SEMESTER
    : 'sp' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'spr' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'spring' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'su' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'sum' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'summer' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'fa' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'fal' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'fall' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'SP' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'SU' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'FA' '-'? DIGIT DIGIT (DIGIT DIGIT)?
    | 'SP26' | 'SP2026' | 'SU26' | 'SU2026' | 'FA26' | 'FA2026'
    ;

// --- WHITESPACE ---
WS : [ \t\r\n]+ -> skip;
