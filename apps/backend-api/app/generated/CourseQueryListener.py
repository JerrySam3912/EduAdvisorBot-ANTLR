# Generated from D:\ppl\projectPpl\EduAdvisorBot-ANTLR\apps\backend-api\app\grammar\CourseQuery.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CourseQueryParser import CourseQueryParser
else:
    from CourseQueryParser import CourseQueryParser

# This class defines a complete listener for a parse tree produced by CourseQueryParser.
class CourseQueryListener(ParseTreeListener):

    # Enter a parse tree produced by CourseQueryParser#query.
    def enterQuery(self, ctx:CourseQueryParser.QueryContext):
        pass

    # Exit a parse tree produced by CourseQueryParser#query.
    def exitQuery(self, ctx:CourseQueryParser.QueryContext):
        pass


    # Enter a parse tree produced by CourseQueryParser#helpQuery.
    def enterHelpQuery(self, ctx:CourseQueryParser.HelpQueryContext):
        pass

    # Exit a parse tree produced by CourseQueryParser#helpQuery.
    def exitHelpQuery(self, ctx:CourseQueryParser.HelpQueryContext):
        pass


    # Enter a parse tree produced by CourseQueryParser#courseQuery.
    def enterCourseQuery(self, ctx:CourseQueryParser.CourseQueryContext):
        pass

    # Exit a parse tree produced by CourseQueryParser#courseQuery.
    def exitCourseQuery(self, ctx:CourseQueryParser.CourseQueryContext):
        pass


    # Enter a parse tree produced by CourseQueryParser#courseCodeOnly.
    def enterCourseCodeOnly(self, ctx:CourseQueryParser.CourseCodeOnlyContext):
        pass

    # Exit a parse tree produced by CourseQueryParser#courseCodeOnly.
    def exitCourseCodeOnly(self, ctx:CourseQueryParser.CourseCodeOnlyContext):
        pass


    # Enter a parse tree produced by CourseQueryParser#questionPrefix.
    def enterQuestionPrefix(self, ctx:CourseQueryParser.QuestionPrefixContext):
        pass

    # Exit a parse tree produced by CourseQueryParser#questionPrefix.
    def exitQuestionPrefix(self, ctx:CourseQueryParser.QuestionPrefixContext):
        pass


    # Enter a parse tree produced by CourseQueryParser#questionSuffix.
    def enterQuestionSuffix(self, ctx:CourseQueryParser.QuestionSuffixContext):
        pass

    # Exit a parse tree produced by CourseQueryParser#questionSuffix.
    def exitQuestionSuffix(self, ctx:CourseQueryParser.QuestionSuffixContext):
        pass


    # Enter a parse tree produced by CourseQueryParser#courseCode.
    def enterCourseCode(self, ctx:CourseQueryParser.CourseCodeContext):
        pass

    # Exit a parse tree produced by CourseQueryParser#courseCode.
    def exitCourseCode(self, ctx:CourseQueryParser.CourseCodeContext):
        pass



del CourseQueryParser