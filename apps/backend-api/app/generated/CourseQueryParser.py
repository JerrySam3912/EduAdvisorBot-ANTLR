# Generated from D:\ppl\projectPpl\EduAdvisorBot-ANTLR\apps\backend-api\app\grammar\CourseQuery.g4 by ANTLR 4.9.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\f")
        buf.write("8\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\3\2\3\2\3\2\3\2\3\2\3\2\5\2\27\n\2\3\3\3\3\3\4\5")
        buf.write("\4\34\n\4\3\4\3\4\5\4 \n\4\3\4\3\4\5\4$\n\4\3\4\3\4\5")
        buf.write("\4(\n\4\3\4\5\4+\n\4\3\5\3\5\3\6\3\6\3\7\6\7\62\n\7\r")
        buf.write("\7\16\7\63\3\b\3\b\3\b\2\2\t\2\4\6\b\n\f\16\2\3\3\2\3")
        buf.write("\b\28\2\26\3\2\2\2\4\30\3\2\2\2\6*\3\2\2\2\b,\3\2\2\2")
        buf.write("\n.\3\2\2\2\f\61\3\2\2\2\16\65\3\2\2\2\20\21\5\4\3\2\21")
        buf.write("\22\7\2\2\3\22\27\3\2\2\2\23\24\5\6\4\2\24\25\7\2\2\3")
        buf.write("\25\27\3\2\2\2\26\20\3\2\2\2\26\23\3\2\2\2\27\3\3\2\2")
        buf.write("\2\30\31\7\t\2\2\31\5\3\2\2\2\32\34\5\n\6\2\33\32\3\2")
        buf.write("\2\2\33\34\3\2\2\2\34\35\3\2\2\2\35\37\5\16\b\2\36 \5")
        buf.write("\f\7\2\37\36\3\2\2\2\37 \3\2\2\2 +\3\2\2\2!#\5\n\6\2\"")
        buf.write("$\5\f\7\2#\"\3\2\2\2#$\3\2\2\2$%\3\2\2\2%\'\5\16\b\2&")
        buf.write("(\5\f\7\2\'&\3\2\2\2\'(\3\2\2\2(+\3\2\2\2)+\5\b\5\2*\33")
        buf.write("\3\2\2\2*!\3\2\2\2*)\3\2\2\2+\7\3\2\2\2,-\5\16\b\2-\t")
        buf.write("\3\2\2\2./\t\2\2\2/\13\3\2\2\2\60\62\7\n\2\2\61\60\3\2")
        buf.write("\2\2\62\63\3\2\2\2\63\61\3\2\2\2\63\64\3\2\2\2\64\r\3")
        buf.write("\2\2\2\65\66\7\13\2\2\66\17\3\2\2\2\t\26\33\37#\'*\63")
        return buf.getvalue()


class CourseQueryParser ( Parser ):

    grammarFileName = "CourseQuery.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "PREREQUISITE_ASK", "BEFORE_ASK", "COMPLETE_ASK", 
                      "RELATION_ASK", "NEED_ASK", "ASK_QUESTION", "HELP", 
                      "QUESTION_WORD", "COURSE_CODE", "WS" ]

    RULE_query = 0
    RULE_helpQuery = 1
    RULE_courseQuery = 2
    RULE_courseCodeOnly = 3
    RULE_questionPrefix = 4
    RULE_questionSuffix = 5
    RULE_courseCode = 6

    ruleNames =  [ "query", "helpQuery", "courseQuery", "courseCodeOnly", 
                   "questionPrefix", "questionSuffix", "courseCode" ]

    EOF = Token.EOF
    PREREQUISITE_ASK=1
    BEFORE_ASK=2
    COMPLETE_ASK=3
    RELATION_ASK=4
    NEED_ASK=5
    ASK_QUESTION=6
    HELP=7
    QUESTION_WORD=8
    COURSE_CODE=9
    WS=10

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class QueryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def helpQuery(self):
            return self.getTypedRuleContext(CourseQueryParser.HelpQueryContext,0)


        def EOF(self):
            return self.getToken(CourseQueryParser.EOF, 0)

        def courseQuery(self):
            return self.getTypedRuleContext(CourseQueryParser.CourseQueryContext,0)


        def getRuleIndex(self):
            return CourseQueryParser.RULE_query

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuery" ):
                listener.enterQuery(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuery" ):
                listener.exitQuery(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQuery" ):
                return visitor.visitQuery(self)
            else:
                return visitor.visitChildren(self)




    def query(self):

        localctx = CourseQueryParser.QueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_query)
        try:
            self.state = 20
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [CourseQueryParser.HELP]:
                self.enterOuterAlt(localctx, 1)
                self.state = 14
                self.helpQuery()
                self.state = 15
                self.match(CourseQueryParser.EOF)
                pass
            elif token in [CourseQueryParser.PREREQUISITE_ASK, CourseQueryParser.BEFORE_ASK, CourseQueryParser.COMPLETE_ASK, CourseQueryParser.RELATION_ASK, CourseQueryParser.NEED_ASK, CourseQueryParser.ASK_QUESTION, CourseQueryParser.COURSE_CODE]:
                self.enterOuterAlt(localctx, 2)
                self.state = 17
                self.courseQuery()
                self.state = 18
                self.match(CourseQueryParser.EOF)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class HelpQueryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def HELP(self):
            return self.getToken(CourseQueryParser.HELP, 0)

        def getRuleIndex(self):
            return CourseQueryParser.RULE_helpQuery

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterHelpQuery" ):
                listener.enterHelpQuery(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitHelpQuery" ):
                listener.exitHelpQuery(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitHelpQuery" ):
                return visitor.visitHelpQuery(self)
            else:
                return visitor.visitChildren(self)




    def helpQuery(self):

        localctx = CourseQueryParser.HelpQueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_helpQuery)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 22
            self.match(CourseQueryParser.HELP)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CourseQueryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def courseCode(self):
            return self.getTypedRuleContext(CourseQueryParser.CourseCodeContext,0)


        def questionPrefix(self):
            return self.getTypedRuleContext(CourseQueryParser.QuestionPrefixContext,0)


        def questionSuffix(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CourseQueryParser.QuestionSuffixContext)
            else:
                return self.getTypedRuleContext(CourseQueryParser.QuestionSuffixContext,i)


        def courseCodeOnly(self):
            return self.getTypedRuleContext(CourseQueryParser.CourseCodeOnlyContext,0)


        def getRuleIndex(self):
            return CourseQueryParser.RULE_courseQuery

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCourseQuery" ):
                listener.enterCourseQuery(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCourseQuery" ):
                listener.exitCourseQuery(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCourseQuery" ):
                return visitor.visitCourseQuery(self)
            else:
                return visitor.visitChildren(self)




    def courseQuery(self):

        localctx = CourseQueryParser.CourseQueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_courseQuery)
        self._la = 0 # Token type
        try:
            self.state = 40
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 25
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << CourseQueryParser.PREREQUISITE_ASK) | (1 << CourseQueryParser.BEFORE_ASK) | (1 << CourseQueryParser.COMPLETE_ASK) | (1 << CourseQueryParser.RELATION_ASK) | (1 << CourseQueryParser.NEED_ASK) | (1 << CourseQueryParser.ASK_QUESTION))) != 0):
                    self.state = 24
                    self.questionPrefix()


                self.state = 27
                self.courseCode()
                self.state = 29
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==CourseQueryParser.QUESTION_WORD:
                    self.state = 28
                    self.questionSuffix()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 31
                self.questionPrefix()
                self.state = 33
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==CourseQueryParser.QUESTION_WORD:
                    self.state = 32
                    self.questionSuffix()


                self.state = 35
                self.courseCode()
                self.state = 37
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==CourseQueryParser.QUESTION_WORD:
                    self.state = 36
                    self.questionSuffix()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 39
                self.courseCodeOnly()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CourseCodeOnlyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def courseCode(self):
            return self.getTypedRuleContext(CourseQueryParser.CourseCodeContext,0)


        def getRuleIndex(self):
            return CourseQueryParser.RULE_courseCodeOnly

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCourseCodeOnly" ):
                listener.enterCourseCodeOnly(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCourseCodeOnly" ):
                listener.exitCourseCodeOnly(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCourseCodeOnly" ):
                return visitor.visitCourseCodeOnly(self)
            else:
                return visitor.visitChildren(self)




    def courseCodeOnly(self):

        localctx = CourseQueryParser.CourseCodeOnlyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_courseCodeOnly)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 42
            self.courseCode()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuestionPrefixContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PREREQUISITE_ASK(self):
            return self.getToken(CourseQueryParser.PREREQUISITE_ASK, 0)

        def BEFORE_ASK(self):
            return self.getToken(CourseQueryParser.BEFORE_ASK, 0)

        def COMPLETE_ASK(self):
            return self.getToken(CourseQueryParser.COMPLETE_ASK, 0)

        def RELATION_ASK(self):
            return self.getToken(CourseQueryParser.RELATION_ASK, 0)

        def NEED_ASK(self):
            return self.getToken(CourseQueryParser.NEED_ASK, 0)

        def ASK_QUESTION(self):
            return self.getToken(CourseQueryParser.ASK_QUESTION, 0)

        def getRuleIndex(self):
            return CourseQueryParser.RULE_questionPrefix

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuestionPrefix" ):
                listener.enterQuestionPrefix(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuestionPrefix" ):
                listener.exitQuestionPrefix(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQuestionPrefix" ):
                return visitor.visitQuestionPrefix(self)
            else:
                return visitor.visitChildren(self)




    def questionPrefix(self):

        localctx = CourseQueryParser.QuestionPrefixContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_questionPrefix)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << CourseQueryParser.PREREQUISITE_ASK) | (1 << CourseQueryParser.BEFORE_ASK) | (1 << CourseQueryParser.COMPLETE_ASK) | (1 << CourseQueryParser.RELATION_ASK) | (1 << CourseQueryParser.NEED_ASK) | (1 << CourseQueryParser.ASK_QUESTION))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuestionSuffixContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUESTION_WORD(self, i:int=None):
            if i is None:
                return self.getTokens(CourseQueryParser.QUESTION_WORD)
            else:
                return self.getToken(CourseQueryParser.QUESTION_WORD, i)

        def getRuleIndex(self):
            return CourseQueryParser.RULE_questionSuffix

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuestionSuffix" ):
                listener.enterQuestionSuffix(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuestionSuffix" ):
                listener.exitQuestionSuffix(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQuestionSuffix" ):
                return visitor.visitQuestionSuffix(self)
            else:
                return visitor.visitChildren(self)




    def questionSuffix(self):

        localctx = CourseQueryParser.QuestionSuffixContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_questionSuffix)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 47 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 46
                self.match(CourseQueryParser.QUESTION_WORD)
                self.state = 49 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==CourseQueryParser.QUESTION_WORD):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CourseCodeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COURSE_CODE(self):
            return self.getToken(CourseQueryParser.COURSE_CODE, 0)

        def getRuleIndex(self):
            return CourseQueryParser.RULE_courseCode

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCourseCode" ):
                listener.enterCourseCode(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCourseCode" ):
                listener.exitCourseCode(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCourseCode" ):
                return visitor.visitCourseCode(self)
            else:
                return visitor.visitChildren(self)




    def courseCode(self):

        localctx = CourseQueryParser.CourseCodeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_courseCode)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self.match(CourseQueryParser.COURSE_CODE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





