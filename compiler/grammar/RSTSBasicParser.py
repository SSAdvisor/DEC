# Generated from compiler/grammar/RSTSBasic.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,48,168,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,1,0,5,
        0,14,8,0,10,0,12,0,17,9,0,1,0,1,0,1,1,3,1,22,8,1,1,1,1,1,1,1,5,1,
        27,8,1,10,1,12,1,30,9,1,1,1,1,1,1,2,1,2,1,3,1,3,1,3,1,3,1,3,1,3,
        5,3,42,8,3,10,3,12,3,45,9,3,1,3,3,3,48,8,3,1,3,3,3,51,8,3,1,3,1,
        3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,3,3,65,8,3,1,3,1,3,1,3,
        5,3,70,8,3,10,3,12,3,73,9,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,3,3,110,8,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,5,3,120,8,3,10,3,12,3,123,9,3,3,3,125,8,3,1,
        4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,142,
        8,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,5,4,153,8,4,10,4,12,4,156,
        9,4,1,5,1,5,3,5,160,8,5,1,5,1,5,1,5,1,5,3,5,166,8,5,1,5,1,71,1,8,
        6,0,2,4,6,8,10,0,6,1,1,47,47,1,0,15,16,1,0,28,29,1,0,30,31,2,0,6,
        6,32,36,1,0,41,42,196,0,15,1,0,0,0,2,21,1,0,0,0,4,33,1,0,0,0,6,124,
        1,0,0,0,8,141,1,0,0,0,10,157,1,0,0,0,12,14,3,2,1,0,13,12,1,0,0,0,
        14,17,1,0,0,0,15,13,1,0,0,0,15,16,1,0,0,0,16,18,1,0,0,0,17,15,1,
        0,0,0,18,19,5,0,0,1,19,1,1,0,0,0,20,22,3,4,2,0,21,20,1,0,0,0,21,
        22,1,0,0,0,22,23,1,0,0,0,23,28,3,6,3,0,24,25,5,1,0,0,25,27,3,6,3,
        0,26,24,1,0,0,0,27,30,1,0,0,0,28,26,1,0,0,0,28,29,1,0,0,0,29,31,
        1,0,0,0,30,28,1,0,0,0,31,32,7,0,0,0,32,3,1,0,0,0,33,34,5,43,0,0,
        34,5,1,0,0,0,35,36,5,2,0,0,36,43,3,8,4,0,37,38,5,3,0,0,38,42,3,8,
        4,0,39,40,5,4,0,0,40,42,3,8,4,0,41,37,1,0,0,0,41,39,1,0,0,0,42,45,
        1,0,0,0,43,41,1,0,0,0,43,44,1,0,0,0,44,47,1,0,0,0,45,43,1,0,0,0,
        46,48,5,4,0,0,47,46,1,0,0,0,47,48,1,0,0,0,48,125,1,0,0,0,49,51,5,
        5,0,0,50,49,1,0,0,0,50,51,1,0,0,0,51,52,1,0,0,0,52,53,3,10,5,0,53,
        54,5,6,0,0,54,55,3,8,4,0,55,125,1,0,0,0,56,57,5,7,0,0,57,125,3,4,
        2,0,58,59,5,8,0,0,59,60,3,8,4,0,60,61,5,9,0,0,61,64,3,6,3,0,62,63,
        5,10,0,0,63,65,3,6,3,0,64,62,1,0,0,0,64,65,1,0,0,0,65,125,1,0,0,
        0,66,125,5,11,0,0,67,71,5,12,0,0,68,70,9,0,0,0,69,68,1,0,0,0,70,
        73,1,0,0,0,71,72,1,0,0,0,71,69,1,0,0,0,72,74,1,0,0,0,73,71,1,0,0,
        0,74,125,7,0,0,0,75,76,5,13,0,0,76,77,3,8,4,0,77,78,5,14,0,0,78,
        79,7,1,0,0,79,80,5,17,0,0,80,81,5,18,0,0,81,82,5,19,0,0,82,83,5,
        43,0,0,83,125,1,0,0,0,84,85,5,13,0,0,85,86,3,8,4,0,86,87,5,17,0,
        0,87,88,5,18,0,0,88,89,5,19,0,0,89,90,5,43,0,0,90,91,5,3,0,0,91,
        92,5,20,0,0,92,93,5,3,0,0,93,94,5,21,0,0,94,95,5,22,0,0,95,96,3,
        10,5,0,96,125,1,0,0,0,97,98,5,23,0,0,98,99,5,19,0,0,99,125,5,43,
        0,0,100,101,5,24,0,0,101,102,5,19,0,0,102,125,5,43,0,0,103,104,5,
        25,0,0,104,105,5,19,0,0,105,109,5,43,0,0,106,107,5,3,0,0,107,108,
        5,22,0,0,108,110,3,10,5,0,109,106,1,0,0,0,109,110,1,0,0,0,110,125,
        1,0,0,0,111,112,5,26,0,0,112,125,5,45,0,0,113,114,5,15,0,0,114,125,
        3,10,5,0,115,116,5,27,0,0,116,121,3,10,5,0,117,118,5,3,0,0,118,120,
        3,10,5,0,119,117,1,0,0,0,120,123,1,0,0,0,121,119,1,0,0,0,121,122,
        1,0,0,0,122,125,1,0,0,0,123,121,1,0,0,0,124,35,1,0,0,0,124,50,1,
        0,0,0,124,56,1,0,0,0,124,58,1,0,0,0,124,66,1,0,0,0,124,67,1,0,0,
        0,124,75,1,0,0,0,124,84,1,0,0,0,124,97,1,0,0,0,124,100,1,0,0,0,124,
        103,1,0,0,0,124,111,1,0,0,0,124,113,1,0,0,0,124,115,1,0,0,0,125,
        7,1,0,0,0,126,127,6,4,-1,0,127,142,5,37,0,0,128,129,5,38,0,0,129,
        130,5,39,0,0,130,131,3,8,4,0,131,132,5,40,0,0,132,142,1,0,0,0,133,
        142,5,43,0,0,134,142,5,44,0,0,135,142,5,45,0,0,136,142,3,10,5,0,
        137,138,5,39,0,0,138,139,3,8,4,0,139,140,5,40,0,0,140,142,1,0,0,
        0,141,126,1,0,0,0,141,128,1,0,0,0,141,133,1,0,0,0,141,134,1,0,0,
        0,141,135,1,0,0,0,141,136,1,0,0,0,141,137,1,0,0,0,142,154,1,0,0,
        0,143,144,10,10,0,0,144,145,7,2,0,0,145,153,3,8,4,11,146,147,10,
        9,0,0,147,148,7,3,0,0,148,153,3,8,4,10,149,150,10,8,0,0,150,151,
        7,4,0,0,151,153,3,8,4,9,152,143,1,0,0,0,152,146,1,0,0,0,152,149,
        1,0,0,0,153,156,1,0,0,0,154,152,1,0,0,0,154,155,1,0,0,0,155,9,1,
        0,0,0,156,154,1,0,0,0,157,159,5,46,0,0,158,160,7,5,0,0,159,158,1,
        0,0,0,159,160,1,0,0,0,160,165,1,0,0,0,161,162,5,39,0,0,162,163,3,
        8,4,0,163,164,5,40,0,0,164,166,1,0,0,0,165,161,1,0,0,0,165,166,1,
        0,0,0,166,11,1,0,0,0,17,15,21,28,41,43,47,50,64,71,109,121,124,141,
        152,154,159,165
    ]

class RSTSBasicParser ( Parser ):

    grammarFileName = "RSTSBasic.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "':'", "'PRINT'", "','", "';'", "'LET'", 
                     "'='", "'GOTO'", "'IF'", "'THEN'", "'ELSE'", "'END'", 
                     "'REM'", "'OPEN'", "'FOR'", "'INPUT'", "'OUTPUT'", 
                     "'AS'", "'FILE'", "'#'", "'INDEXED'", "'PRIMARY'", 
                     "'KEY'", "'CLOSE'", "'PUT'", "'GET'", "'CALL'", "'DIM'", 
                     "'*'", "'/'", "'+'", "'-'", "'<'", "'>'", "'<='", "'>='", 
                     "'<>'", "'INKEY$'", "'CHR$'", "'('", "')'", "'%'", 
                     "'$'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "INT", "FLOAT", 
                      "STRING", "ID", "NEWLINE", "WS" ]

    RULE_program = 0
    RULE_line = 1
    RULE_lineNumber = 2
    RULE_statement = 3
    RULE_expression = 4
    RULE_variable = 5

    ruleNames =  [ "program", "line", "lineNumber", "statement", "expression", 
                   "variable" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    T__29=30
    T__30=31
    T__31=32
    T__32=33
    T__33=34
    T__34=35
    T__35=36
    T__36=37
    T__37=38
    T__38=39
    T__39=40
    T__40=41
    T__41=42
    INT=43
    FLOAT=44
    STRING=45
    ID=46
    NEWLINE=47
    WS=48

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(RSTSBasicParser.EOF, 0)

        def line(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.LineContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.LineContext,i)


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProgram" ):
                return visitor.visitProgram(self)
            else:
                return visitor.visitChildren(self)




    def program(self):

        localctx = RSTSBasicParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 79165097294244) != 0):
                self.state = 12
                self.line()
                self.state = 17
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 18
            self.match(RSTSBasicParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.StatementContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.StatementContext,i)


        def NEWLINE(self):
            return self.getToken(RSTSBasicParser.NEWLINE, 0)

        def EOF(self):
            return self.getToken(RSTSBasicParser.EOF, 0)

        def lineNumber(self):
            return self.getTypedRuleContext(RSTSBasicParser.LineNumberContext,0)


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_line

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLine" ):
                listener.enterLine(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLine" ):
                listener.exitLine(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLine" ):
                return visitor.visitLine(self)
            else:
                return visitor.visitChildren(self)




    def line(self):

        localctx = RSTSBasicParser.LineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_line)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 21
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==43:
                self.state = 20
                self.lineNumber()


            self.state = 23
            self.statement()
            self.state = 28
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 24
                self.match(RSTSBasicParser.T__0)
                self.state = 25
                self.statement()
                self.state = 30
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 31
            _la = self._input.LA(1)
            if not(_la==-1 or _la==47):
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


    class LineNumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def getRuleIndex(self):
            return RSTSBasicParser.RULE_lineNumber

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLineNumber" ):
                listener.enterLineNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLineNumber" ):
                listener.exitLineNumber(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLineNumber" ):
                return visitor.visitLineNumber(self)
            else:
                return visitor.visitChildren(self)




    def lineNumber(self):

        localctx = RSTSBasicParser.LineNumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_lineNumber)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 33
            self.match(RSTSBasicParser.INT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_statement

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class OpenIdxStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)
        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOpenIdxStmt" ):
                listener.enterOpenIdxStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOpenIdxStmt" ):
                listener.exitOpenIdxStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOpenIdxStmt" ):
                return visitor.visitOpenIdxStmt(self)
            else:
                return visitor.visitChildren(self)


    class RemStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NEWLINE(self):
            return self.getToken(RSTSBasicParser.NEWLINE, 0)
        def EOF(self):
            return self.getToken(RSTSBasicParser.EOF, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRemStmt" ):
                listener.enterRemStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRemStmt" ):
                listener.exitRemStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRemStmt" ):
                return visitor.visitRemStmt(self)
            else:
                return visitor.visitChildren(self)


    class LetStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLetStmt" ):
                listener.enterLetStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLetStmt" ):
                listener.exitLetStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLetStmt" ):
                return visitor.visitLetStmt(self)
            else:
                return visitor.visitChildren(self)


    class GotoStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def lineNumber(self):
            return self.getTypedRuleContext(RSTSBasicParser.LineNumberContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGotoStmt" ):
                listener.enterGotoStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGotoStmt" ):
                listener.exitGotoStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGotoStmt" ):
                return visitor.visitGotoStmt(self)
            else:
                return visitor.visitChildren(self)


    class InputStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInputStmt" ):
                listener.enterInputStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInputStmt" ):
                listener.exitInputStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInputStmt" ):
                return visitor.visitInputStmt(self)
            else:
                return visitor.visitChildren(self)


    class EndStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEndStmt" ):
                listener.enterEndStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEndStmt" ):
                listener.exitEndStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEndStmt" ):
                return visitor.visitEndStmt(self)
            else:
                return visitor.visitChildren(self)


    class PrintStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrintStmt" ):
                listener.enterPrintStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrintStmt" ):
                listener.exitPrintStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrintStmt" ):
                return visitor.visitPrintStmt(self)
            else:
                return visitor.visitChildren(self)


    class CallStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(RSTSBasicParser.STRING, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCallStmt" ):
                listener.enterCallStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCallStmt" ):
                listener.exitCallStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCallStmt" ):
                return visitor.visitCallStmt(self)
            else:
                return visitor.visitChildren(self)


    class DimStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.VariableContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.VariableContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDimStmt" ):
                listener.enterDimStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDimStmt" ):
                listener.exitDimStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDimStmt" ):
                return visitor.visitDimStmt(self)
            else:
                return visitor.visitChildren(self)


    class IfStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.StatementContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.StatementContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIfStmt" ):
                listener.enterIfStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIfStmt" ):
                listener.exitIfStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIfStmt" ):
                return visitor.visitIfStmt(self)
            else:
                return visitor.visitChildren(self)


    class OpenSeqStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOpenSeqStmt" ):
                listener.enterOpenSeqStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOpenSeqStmt" ):
                listener.exitOpenSeqStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOpenSeqStmt" ):
                return visitor.visitOpenSeqStmt(self)
            else:
                return visitor.visitChildren(self)


    class GetStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)
        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGetStmt" ):
                listener.enterGetStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGetStmt" ):
                listener.exitGetStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGetStmt" ):
                return visitor.visitGetStmt(self)
            else:
                return visitor.visitChildren(self)


    class PutStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPutStmt" ):
                listener.enterPutStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPutStmt" ):
                listener.exitPutStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPutStmt" ):
                return visitor.visitPutStmt(self)
            else:
                return visitor.visitChildren(self)


    class CloseStmtContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCloseStmt" ):
                listener.enterCloseStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCloseStmt" ):
                listener.exitCloseStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCloseStmt" ):
                return visitor.visitCloseStmt(self)
            else:
                return visitor.visitChildren(self)



    def statement(self):

        localctx = RSTSBasicParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_statement)
        self._la = 0 # Token type
        try:
            self.state = 124
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,11,self._ctx)
            if la_ == 1:
                localctx = RSTSBasicParser.PrintStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 35
                self.match(RSTSBasicParser.T__1)
                self.state = 36
                self.expression(0)
                self.state = 43
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,4,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 41
                        self._errHandler.sync(self)
                        token = self._input.LA(1)
                        if token in [3]:
                            self.state = 37
                            self.match(RSTSBasicParser.T__2)
                            self.state = 38
                            self.expression(0)
                            pass
                        elif token in [4]:
                            self.state = 39
                            self.match(RSTSBasicParser.T__3)
                            self.state = 40
                            self.expression(0)
                            pass
                        else:
                            raise NoViableAltException(self)
                 
                    self.state = 45
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

                self.state = 47
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==4:
                    self.state = 46
                    self.match(RSTSBasicParser.T__3)


                pass

            elif la_ == 2:
                localctx = RSTSBasicParser.LetStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 50
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==5:
                    self.state = 49
                    self.match(RSTSBasicParser.T__4)


                self.state = 52
                self.variable()
                self.state = 53
                self.match(RSTSBasicParser.T__5)
                self.state = 54
                self.expression(0)
                pass

            elif la_ == 3:
                localctx = RSTSBasicParser.GotoStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 56
                self.match(RSTSBasicParser.T__6)
                self.state = 57
                self.lineNumber()
                pass

            elif la_ == 4:
                localctx = RSTSBasicParser.IfStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 58
                self.match(RSTSBasicParser.T__7)
                self.state = 59
                self.expression(0)
                self.state = 60
                self.match(RSTSBasicParser.T__8)
                self.state = 61
                self.statement()
                self.state = 64
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
                if la_ == 1:
                    self.state = 62
                    self.match(RSTSBasicParser.T__9)
                    self.state = 63
                    self.statement()


                pass

            elif la_ == 5:
                localctx = RSTSBasicParser.EndStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 66
                self.match(RSTSBasicParser.T__10)
                pass

            elif la_ == 6:
                localctx = RSTSBasicParser.RemStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 67
                self.match(RSTSBasicParser.T__11)
                self.state = 71
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,8,self._ctx)
                while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1+1:
                        self.state = 68
                        self.matchWildcard() 
                    self.state = 73
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,8,self._ctx)

                self.state = 74
                _la = self._input.LA(1)
                if not(_la==-1 or _la==47):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass

            elif la_ == 7:
                localctx = RSTSBasicParser.OpenSeqStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 75
                self.match(RSTSBasicParser.T__12)
                self.state = 76
                self.expression(0)
                self.state = 77
                self.match(RSTSBasicParser.T__13)
                self.state = 78
                _la = self._input.LA(1)
                if not(_la==15 or _la==16):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 79
                self.match(RSTSBasicParser.T__16)
                self.state = 80
                self.match(RSTSBasicParser.T__17)
                self.state = 81
                self.match(RSTSBasicParser.T__18)
                self.state = 82
                self.match(RSTSBasicParser.INT)
                pass

            elif la_ == 8:
                localctx = RSTSBasicParser.OpenIdxStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 84
                self.match(RSTSBasicParser.T__12)
                self.state = 85
                self.expression(0)
                self.state = 86
                self.match(RSTSBasicParser.T__16)
                self.state = 87
                self.match(RSTSBasicParser.T__17)
                self.state = 88
                self.match(RSTSBasicParser.T__18)
                self.state = 89
                self.match(RSTSBasicParser.INT)
                self.state = 90
                self.match(RSTSBasicParser.T__2)
                self.state = 91
                self.match(RSTSBasicParser.T__19)
                self.state = 92
                self.match(RSTSBasicParser.T__2)
                self.state = 93
                self.match(RSTSBasicParser.T__20)
                self.state = 94
                self.match(RSTSBasicParser.T__21)
                self.state = 95
                self.variable()
                pass

            elif la_ == 9:
                localctx = RSTSBasicParser.CloseStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 9)
                self.state = 97
                self.match(RSTSBasicParser.T__22)
                self.state = 98
                self.match(RSTSBasicParser.T__18)
                self.state = 99
                self.match(RSTSBasicParser.INT)
                pass

            elif la_ == 10:
                localctx = RSTSBasicParser.PutStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 10)
                self.state = 100
                self.match(RSTSBasicParser.T__23)
                self.state = 101
                self.match(RSTSBasicParser.T__18)
                self.state = 102
                self.match(RSTSBasicParser.INT)
                pass

            elif la_ == 11:
                localctx = RSTSBasicParser.GetStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 11)
                self.state = 103
                self.match(RSTSBasicParser.T__24)
                self.state = 104
                self.match(RSTSBasicParser.T__18)
                self.state = 105
                self.match(RSTSBasicParser.INT)
                self.state = 109
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==3:
                    self.state = 106
                    self.match(RSTSBasicParser.T__2)
                    self.state = 107
                    self.match(RSTSBasicParser.T__21)
                    self.state = 108
                    self.variable()


                pass

            elif la_ == 12:
                localctx = RSTSBasicParser.CallStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 12)
                self.state = 111
                self.match(RSTSBasicParser.T__25)
                self.state = 112
                self.match(RSTSBasicParser.STRING)
                pass

            elif la_ == 13:
                localctx = RSTSBasicParser.InputStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 13)
                self.state = 113
                self.match(RSTSBasicParser.T__14)
                self.state = 114
                self.variable()
                pass

            elif la_ == 14:
                localctx = RSTSBasicParser.DimStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 14)
                self.state = 115
                self.match(RSTSBasicParser.T__26)
                self.state = 116
                self.variable()
                self.state = 121
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==3:
                    self.state = 117
                    self.match(RSTSBasicParser.T__2)
                    self.state = 118
                    self.variable()
                    self.state = 123
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_expression

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class StrExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(RSTSBasicParser.STRING, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStrExpr" ):
                listener.enterStrExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStrExpr" ):
                listener.exitStrExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStrExpr" ):
                return visitor.visitStrExpr(self)
            else:
                return visitor.visitChildren(self)


    class FloatExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def FLOAT(self):
            return self.getToken(RSTSBasicParser.FLOAT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFloatExpr" ):
                listener.enterFloatExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFloatExpr" ):
                listener.exitFloatExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFloatExpr" ):
                return visitor.visitFloatExpr(self)
            else:
                return visitor.visitChildren(self)


    class VarExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self):
            return self.getTypedRuleContext(RSTSBasicParser.VariableContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVarExpr" ):
                listener.enterVarExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVarExpr" ):
                listener.exitVarExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVarExpr" ):
                return visitor.visitVarExpr(self)
            else:
                return visitor.visitChildren(self)


    class IntExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self):
            return self.getToken(RSTSBasicParser.INT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIntExpr" ):
                listener.enterIntExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIntExpr" ):
                listener.exitIntExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIntExpr" ):
                return visitor.visitIntExpr(self)
            else:
                return visitor.visitChildren(self)


    class AddSubExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.left = None # ExpressionContext
            self.op = None # Token
            self.right = None # ExpressionContext
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddSubExpr" ):
                listener.enterAddSubExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddSubExpr" ):
                listener.exitAddSubExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddSubExpr" ):
                return visitor.visitAddSubExpr(self)
            else:
                return visitor.visitChildren(self)


    class ChrExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChrExpr" ):
                listener.enterChrExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChrExpr" ):
                listener.exitChrExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitChrExpr" ):
                return visitor.visitChrExpr(self)
            else:
                return visitor.visitChildren(self)


    class ParensExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParensExpr" ):
                listener.enterParensExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParensExpr" ):
                listener.exitParensExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParensExpr" ):
                return visitor.visitParensExpr(self)
            else:
                return visitor.visitChildren(self)


    class RelExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.left = None # ExpressionContext
            self.op = None # Token
            self.right = None # ExpressionContext
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelExpr" ):
                listener.enterRelExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelExpr" ):
                listener.exitRelExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelExpr" ):
                return visitor.visitRelExpr(self)
            else:
                return visitor.visitChildren(self)


    class MulDivExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.left = None # ExpressionContext
            self.op = None # Token
            self.right = None # ExpressionContext
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RSTSBasicParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMulDivExpr" ):
                listener.enterMulDivExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMulDivExpr" ):
                listener.exitMulDivExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMulDivExpr" ):
                return visitor.visitMulDivExpr(self)
            else:
                return visitor.visitChildren(self)


    class InkeyExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RSTSBasicParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInkeyExpr" ):
                listener.enterInkeyExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInkeyExpr" ):
                listener.exitInkeyExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInkeyExpr" ):
                return visitor.visitInkeyExpr(self)
            else:
                return visitor.visitChildren(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = RSTSBasicParser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 8
        self.enterRecursionRule(localctx, 8, self.RULE_expression, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 141
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [37]:
                localctx = RSTSBasicParser.InkeyExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 127
                self.match(RSTSBasicParser.T__36)
                pass
            elif token in [38]:
                localctx = RSTSBasicParser.ChrExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 128
                self.match(RSTSBasicParser.T__37)
                self.state = 129
                self.match(RSTSBasicParser.T__38)
                self.state = 130
                self.expression(0)
                self.state = 131
                self.match(RSTSBasicParser.T__39)
                pass
            elif token in [43]:
                localctx = RSTSBasicParser.IntExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 133
                self.match(RSTSBasicParser.INT)
                pass
            elif token in [44]:
                localctx = RSTSBasicParser.FloatExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 134
                self.match(RSTSBasicParser.FLOAT)
                pass
            elif token in [45]:
                localctx = RSTSBasicParser.StrExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 135
                self.match(RSTSBasicParser.STRING)
                pass
            elif token in [46]:
                localctx = RSTSBasicParser.VarExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 136
                self.variable()
                pass
            elif token in [39]:
                localctx = RSTSBasicParser.ParensExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 137
                self.match(RSTSBasicParser.T__38)
                self.state = 138
                self.expression(0)
                self.state = 139
                self.match(RSTSBasicParser.T__39)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 154
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,14,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 152
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,13,self._ctx)
                    if la_ == 1:
                        localctx = RSTSBasicParser.MulDivExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 143
                        if not self.precpred(self._ctx, 10):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 10)")
                        self.state = 144
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==28 or _la==29):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 145
                        localctx.right = self.expression(11)
                        pass

                    elif la_ == 2:
                        localctx = RSTSBasicParser.AddSubExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 146
                        if not self.precpred(self._ctx, 9):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 9)")
                        self.state = 147
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==30 or _la==31):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 148
                        localctx.right = self.expression(10)
                        pass

                    elif la_ == 3:
                        localctx = RSTSBasicParser.RelExprContext(self, RSTSBasicParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 149
                        if not self.precpred(self._ctx, 8):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 8)")
                        self.state = 150
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 133143986240) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 151
                        localctx.right = self.expression(9)
                        pass

             
                self.state = 156
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class VariableContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(RSTSBasicParser.ID, 0)

        def expression(self):
            return self.getTypedRuleContext(RSTSBasicParser.ExpressionContext,0)


        def getRuleIndex(self):
            return RSTSBasicParser.RULE_variable

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVariable" ):
                listener.enterVariable(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVariable" ):
                listener.exitVariable(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariable" ):
                return visitor.visitVariable(self)
            else:
                return visitor.visitChildren(self)




    def variable(self):

        localctx = RSTSBasicParser.VariableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_variable)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 157
            self.match(RSTSBasicParser.ID)
            self.state = 159
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
            if la_ == 1:
                self.state = 158
                _la = self._input.LA(1)
                if not(_la==41 or _la==42):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


            self.state = 165
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,16,self._ctx)
            if la_ == 1:
                self.state = 161
                self.match(RSTSBasicParser.T__38)
                self.state = 162
                self.expression(0)
                self.state = 163
                self.match(RSTSBasicParser.T__39)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[4] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 10)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 9)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 8)
         




