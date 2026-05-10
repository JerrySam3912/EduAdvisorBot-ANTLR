# Generated from D:\ppl\projectPpl\EduAdvisorBot-ANTLR\apps\backend-api\app\grammar\CourseQuery.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CourseQueryParser import CourseQueryParser
else:
    from CourseQueryParser import CourseQueryParser

# This class defines a complete generic visitor for a parse tree produced by CourseQueryParser.

class CourseQueryVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CourseQueryParser#query.
    def visitQuery(self, ctx:CourseQueryParser.QueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#helpQuery.
    def visitHelpQuery(self, ctx:CourseQueryParser.HelpQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#courseQuery.
    def visitCourseQuery(self, ctx:CourseQueryParser.CourseQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#courseCodeOnly.
    def visitCourseCodeOnly(self, ctx:CourseQueryParser.CourseCodeOnlyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#questionPrefix.
    def visitQuestionPrefix(self, ctx:CourseQueryParser.QuestionPrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#questionSuffix.
    def visitQuestionSuffix(self, ctx:CourseQueryParser.QuestionSuffixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#courseCode.
    def visitCourseCode(self, ctx:CourseQueryParser.CourseCodeContext):
        return self.visitChildren(ctx)



del CourseQueryParser