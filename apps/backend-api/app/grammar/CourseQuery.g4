grammar CourseQuery;

query
    : helpQuery EOF
    | courseQuery EOF
    ;

helpQuery
    : HELP
    ;

courseQuery
    : questionPrefix? courseCode questionSuffix?
    | questionPrefix questionSuffix? courseCode questionSuffix?
    | courseCodeOnly
    ;

courseCodeOnly
    : courseCode
    ;

questionPrefix
    : PREREQUISITE_ASK
    | BEFORE_ASK
    | COMPLETE_ASK
    | RELATION_ASK
    | NEED_ASK
    | ASK_QUESTION
    ;

questionSuffix
    : QUESTION_WORD+
    ;

courseCode
    : COURSE_CODE
    ;

PREREQUISITE_ASK
    : 'need'
    | 'needs'
    | 'cần'
    | 'cần phải'
    | 'phải'
    | 'tiên quyết'
    | 'tien quet'
    | 'prerequisite'
    | 'prerequisites'
    ;

BEFORE_ASK
    : 'before'
    | 'trước'
    | 'truoc'
    | 'trước đó'
    | 'truoc do'
    ;

COMPLETE_ASK
    : 'complete'
    | 'hoàn thành'
    | 'hoan thanh'
    | 'finish'
    | 'pass'
    ;

RELATION_ASK
    : 'relation'
    | 'quan hệ'
    | 'quan he'
    ;

NEED_ASK
    : 'which'
    | 'what'
    | 'how'
    | 'nào'
    | 'nao'
    | 'mấy'
    | 'may'
    ;

ASK_QUESTION
    : 'bạn'
    | 'ban'
    | 'môn'
    | 'mon'
    | 'mình'
    | 'minh'
    | 'tôi'
    | 'toi'
    ;

HELP
    : 'help'
    | 'gợi ý'
    | 'goi y'
    ;

QUESTION_WORD
    : 'gì'
    | 'gi'
    | 'nào'
    | 'nao'
    | 'mấy'
    | 'may'
    | 'học'
    | 'hoc'
    | 'để'
    | 'de'
    | 'với'
    | 'voi'
    | 'cho'
    | 'là'
    | 'la'
    | 'của'
    | 'cua'
    | 'cần'
    | 'can'
    | 'phải'
    | 'phai'
    | 'trước'
    | 'truoc'
    ;

COURSE_CODE
    : LETTER LETTER (LETTER LETTER?)? DIGIT DIGIT DIGIT 'IU'?
    ;

fragment LETTER : [a-zA-Z];
fragment DIGIT : [0-9];
WS : [ \t\r\n]+ -> skip;
