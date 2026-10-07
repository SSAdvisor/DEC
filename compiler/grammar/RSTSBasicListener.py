# Generated from compiler/grammar/RSTSBasic.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .RSTSBasicParser import RSTSBasicParser
else:
    from RSTSBasicParser import RSTSBasicParser

# This class defines a complete listener for a parse tree produced by RSTSBasicParser.
class RSTSBasicListener(ParseTreeListener):

    # Enter a parse tree produced by RSTSBasicParser#program.
    def enterProgram(self, ctx:RSTSBasicParser.ProgramContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#program.
    def exitProgram(self, ctx:RSTSBasicParser.ProgramContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#line.
    def enterLine(self, ctx:RSTSBasicParser.LineContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#line.
    def exitLine(self, ctx:RSTSBasicParser.LineContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#lineNumber.
    def enterLineNumber(self, ctx:RSTSBasicParser.LineNumberContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#lineNumber.
    def exitLineNumber(self, ctx:RSTSBasicParser.LineNumberContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#printStmt.
    def enterPrintStmt(self, ctx:RSTSBasicParser.PrintStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#printStmt.
    def exitPrintStmt(self, ctx:RSTSBasicParser.PrintStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#letStmt.
    def enterLetStmt(self, ctx:RSTSBasicParser.LetStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#letStmt.
    def exitLetStmt(self, ctx:RSTSBasicParser.LetStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#gotoStmt.
    def enterGotoStmt(self, ctx:RSTSBasicParser.GotoStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#gotoStmt.
    def exitGotoStmt(self, ctx:RSTSBasicParser.GotoStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#ifStmt.
    def enterIfStmt(self, ctx:RSTSBasicParser.IfStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#ifStmt.
    def exitIfStmt(self, ctx:RSTSBasicParser.IfStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#endStmt.
    def enterEndStmt(self, ctx:RSTSBasicParser.EndStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#endStmt.
    def exitEndStmt(self, ctx:RSTSBasicParser.EndStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#remStmt.
    def enterRemStmt(self, ctx:RSTSBasicParser.RemStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#remStmt.
    def exitRemStmt(self, ctx:RSTSBasicParser.RemStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#openSeqStmt.
    def enterOpenSeqStmt(self, ctx:RSTSBasicParser.OpenSeqStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#openSeqStmt.
    def exitOpenSeqStmt(self, ctx:RSTSBasicParser.OpenSeqStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#openIdxStmt.
    def enterOpenIdxStmt(self, ctx:RSTSBasicParser.OpenIdxStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#openIdxStmt.
    def exitOpenIdxStmt(self, ctx:RSTSBasicParser.OpenIdxStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#closeStmt.
    def enterCloseStmt(self, ctx:RSTSBasicParser.CloseStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#closeStmt.
    def exitCloseStmt(self, ctx:RSTSBasicParser.CloseStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#putStmt.
    def enterPutStmt(self, ctx:RSTSBasicParser.PutStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#putStmt.
    def exitPutStmt(self, ctx:RSTSBasicParser.PutStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#getStmt.
    def enterGetStmt(self, ctx:RSTSBasicParser.GetStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#getStmt.
    def exitGetStmt(self, ctx:RSTSBasicParser.GetStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#callStmt.
    def enterCallStmt(self, ctx:RSTSBasicParser.CallStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#callStmt.
    def exitCallStmt(self, ctx:RSTSBasicParser.CallStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#inputStmt.
    def enterInputStmt(self, ctx:RSTSBasicParser.InputStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#inputStmt.
    def exitInputStmt(self, ctx:RSTSBasicParser.InputStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#dimStmt.
    def enterDimStmt(self, ctx:RSTSBasicParser.DimStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#dimStmt.
    def exitDimStmt(self, ctx:RSTSBasicParser.DimStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#strExpr.
    def enterStrExpr(self, ctx:RSTSBasicParser.StrExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#strExpr.
    def exitStrExpr(self, ctx:RSTSBasicParser.StrExprContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#floatExpr.
    def enterFloatExpr(self, ctx:RSTSBasicParser.FloatExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#floatExpr.
    def exitFloatExpr(self, ctx:RSTSBasicParser.FloatExprContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#varExpr.
    def enterVarExpr(self, ctx:RSTSBasicParser.VarExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#varExpr.
    def exitVarExpr(self, ctx:RSTSBasicParser.VarExprContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#intExpr.
    def enterIntExpr(self, ctx:RSTSBasicParser.IntExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#intExpr.
    def exitIntExpr(self, ctx:RSTSBasicParser.IntExprContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#addSubExpr.
    def enterAddSubExpr(self, ctx:RSTSBasicParser.AddSubExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#addSubExpr.
    def exitAddSubExpr(self, ctx:RSTSBasicParser.AddSubExprContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#chrExpr.
    def enterChrExpr(self, ctx:RSTSBasicParser.ChrExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#chrExpr.
    def exitChrExpr(self, ctx:RSTSBasicParser.ChrExprContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#parensExpr.
    def enterParensExpr(self, ctx:RSTSBasicParser.ParensExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#parensExpr.
    def exitParensExpr(self, ctx:RSTSBasicParser.ParensExprContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#relExpr.
    def enterRelExpr(self, ctx:RSTSBasicParser.RelExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#relExpr.
    def exitRelExpr(self, ctx:RSTSBasicParser.RelExprContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#mulDivExpr.
    def enterMulDivExpr(self, ctx:RSTSBasicParser.MulDivExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#mulDivExpr.
    def exitMulDivExpr(self, ctx:RSTSBasicParser.MulDivExprContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#inkeyExpr.
    def enterInkeyExpr(self, ctx:RSTSBasicParser.InkeyExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#inkeyExpr.
    def exitInkeyExpr(self, ctx:RSTSBasicParser.InkeyExprContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#variable.
    def enterVariable(self, ctx:RSTSBasicParser.VariableContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#variable.
    def exitVariable(self, ctx:RSTSBasicParser.VariableContext):
        pass



del RSTSBasicParser