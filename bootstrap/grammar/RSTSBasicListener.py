# Generated from bootstrap/grammar/RSTSBasic.g4 by ANTLR 4.13.1
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


    # Enter a parse tree produced by RSTSBasicParser#labelDef.
    def enterLabelDef(self, ctx:RSTSBasicParser.LabelDefContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#labelDef.
    def exitLabelDef(self, ctx:RSTSBasicParser.LabelDefContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#lineNumber.
    def enterLineNumber(self, ctx:RSTSBasicParser.LineNumberContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#lineNumber.
    def exitLineNumber(self, ctx:RSTSBasicParser.LineNumberContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#target.
    def enterTarget(self, ctx:RSTSBasicParser.TargetContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#target.
    def exitTarget(self, ctx:RSTSBasicParser.TargetContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#dataType.
    def enterDataType(self, ctx:RSTSBasicParser.DataTypeContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#dataType.
    def exitDataType(self, ctx:RSTSBasicParser.DataTypeContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#mapItem.
    def enterMapItem(self, ctx:RSTSBasicParser.MapItemContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#mapItem.
    def exitMapItem(self, ctx:RSTSBasicParser.MapItemContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#programStmt.
    def enterProgramStmt(self, ctx:RSTSBasicParser.ProgramStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#programStmt.
    def exitProgramStmt(self, ctx:RSTSBasicParser.ProgramStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#declareStmt.
    def enterDeclareStmt(self, ctx:RSTSBasicParser.DeclareStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#declareStmt.
    def exitDeclareStmt(self, ctx:RSTSBasicParser.DeclareStmtContext):
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


    # Enter a parse tree produced by RSTSBasicParser#gosubStmt.
    def enterGosubStmt(self, ctx:RSTSBasicParser.GosubStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#gosubStmt.
    def exitGosubStmt(self, ctx:RSTSBasicParser.GosubStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#returnStmt.
    def enterReturnStmt(self, ctx:RSTSBasicParser.ReturnStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#returnStmt.
    def exitReturnStmt(self, ctx:RSTSBasicParser.ReturnStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#randomizeStmt.
    def enterRandomizeStmt(self, ctx:RSTSBasicParser.RandomizeStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#randomizeStmt.
    def exitRandomizeStmt(self, ctx:RSTSBasicParser.RandomizeStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#forStmt.
    def enterForStmt(self, ctx:RSTSBasicParser.ForStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#forStmt.
    def exitForStmt(self, ctx:RSTSBasicParser.ForStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#nextStmt.
    def enterNextStmt(self, ctx:RSTSBasicParser.NextStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#nextStmt.
    def exitNextStmt(self, ctx:RSTSBasicParser.NextStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#readStmt.
    def enterReadStmt(self, ctx:RSTSBasicParser.ReadStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#readStmt.
    def exitReadStmt(self, ctx:RSTSBasicParser.ReadStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#dataStmt.
    def enterDataStmt(self, ctx:RSTSBasicParser.DataStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#dataStmt.
    def exitDataStmt(self, ctx:RSTSBasicParser.DataStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#restoreStmt.
    def enterRestoreStmt(self, ctx:RSTSBasicParser.RestoreStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#restoreStmt.
    def exitRestoreStmt(self, ctx:RSTSBasicParser.RestoreStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#ifStmt.
    def enterIfStmt(self, ctx:RSTSBasicParser.IfStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#ifStmt.
    def exitIfStmt(self, ctx:RSTSBasicParser.IfStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#ifBlockStmt.
    def enterIfBlockStmt(self, ctx:RSTSBasicParser.IfBlockStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#ifBlockStmt.
    def exitIfBlockStmt(self, ctx:RSTSBasicParser.IfBlockStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#thenStmt.
    def enterThenStmt(self, ctx:RSTSBasicParser.ThenStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#thenStmt.
    def exitThenStmt(self, ctx:RSTSBasicParser.ThenStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#elseStmt.
    def enterElseStmt(self, ctx:RSTSBasicParser.ElseStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#elseStmt.
    def exitElseStmt(self, ctx:RSTSBasicParser.ElseStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#endIfStmt.
    def enterEndIfStmt(self, ctx:RSTSBasicParser.EndIfStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#endIfStmt.
    def exitEndIfStmt(self, ctx:RSTSBasicParser.EndIfStmtContext):
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


    # Enter a parse tree produced by RSTSBasicParser#bangRemStmt.
    def enterBangRemStmt(self, ctx:RSTSBasicParser.BangRemStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#bangRemStmt.
    def exitBangRemStmt(self, ctx:RSTSBasicParser.BangRemStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#onErrorStmt.
    def enterOnErrorStmt(self, ctx:RSTSBasicParser.OnErrorStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#onErrorStmt.
    def exitOnErrorStmt(self, ctx:RSTSBasicParser.OnErrorStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#resumeStmt.
    def enterResumeStmt(self, ctx:RSTSBasicParser.ResumeStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#resumeStmt.
    def exitResumeStmt(self, ctx:RSTSBasicParser.ResumeStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#mapStmt.
    def enterMapStmt(self, ctx:RSTSBasicParser.MapStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#mapStmt.
    def exitMapStmt(self, ctx:RSTSBasicParser.MapStmtContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#openAnyStmt.
    def enterOpenAnyStmt(self, ctx:RSTSBasicParser.OpenAnyStmtContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#openAnyStmt.
    def exitOpenAnyStmt(self, ctx:RSTSBasicParser.OpenAnyStmtContext):
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


    # Enter a parse tree produced by RSTSBasicParser#printItem.
    def enterPrintItem(self, ctx:RSTSBasicParser.PrintItemContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#printItem.
    def exitPrintItem(self, ctx:RSTSBasicParser.PrintItemContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#dataItem.
    def enterDataItem(self, ctx:RSTSBasicParser.DataItemContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#dataItem.
    def exitDataItem(self, ctx:RSTSBasicParser.DataItemContext):
        pass


    # Enter a parse tree produced by RSTSBasicParser#openClause.
    def enterOpenClause(self, ctx:RSTSBasicParser.OpenClauseContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#openClause.
    def exitOpenClause(self, ctx:RSTSBasicParser.OpenClauseContext):
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


    # Enter a parse tree produced by RSTSBasicParser#unaryExpr.
    def enterUnaryExpr(self, ctx:RSTSBasicParser.UnaryExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#unaryExpr.
    def exitUnaryExpr(self, ctx:RSTSBasicParser.UnaryExprContext):
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


    # Enter a parse tree produced by RSTSBasicParser#logicalExpr.
    def enterLogicalExpr(self, ctx:RSTSBasicParser.LogicalExprContext):
        pass

    # Exit a parse tree produced by RSTSBasicParser#logicalExpr.
    def exitLogicalExpr(self, ctx:RSTSBasicParser.LogicalExprContext):
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