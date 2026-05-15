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


    # Visit a parse tree produced by CourseQueryParser#greetingQuery.
    def visitGreetingQuery(self, ctx:CourseQueryParser.GreetingQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#helpQuery.
    def visitHelpQuery(self, ctx:CourseQueryParser.HelpQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#eligibilityQuery.
    def visitEligibilityQuery(self, ctx:CourseQueryParser.EligibilityQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#eligibleSuffix.
    def visitEligibleSuffix(self, ctx:CourseQueryParser.EligibleSuffixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#courseQuery.
    def visitCourseQuery(self, ctx:CourseQueryParser.CourseQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#prerequisiteQuery.
    def visitPrerequisiteQuery(self, ctx:CourseQueryParser.PrerequisiteQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#previousQuery.
    def visitPreviousQuery(self, ctx:CourseQueryParser.PreviousQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#courseInfoQuery.
    def visitCourseInfoQuery(self, ctx:CourseQueryParser.CourseInfoQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#dropQuery.
    def visitDropQuery(self, ctx:CourseQueryParser.DropQueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CourseQueryParser#registrationQuery.
    def visitRegistrationQuery(self, ctx:CourseQueryParser.RegistrationQueryContext):
        return self.visitChildren(ctx)



del CourseQueryParser