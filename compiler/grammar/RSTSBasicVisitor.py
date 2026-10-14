# Generated from compiler/grammar/RSTSBasic.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .RSTSBasicParser import RSTSBasicParser
else:
    from RSTSBasicParser import RSTSBasicParser

# This class defines a complete generic visitor for a parse tree produced by RSTSBasicParser.

class RSTSBasicVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by RSTSBasicParser#program.
    def visitProgram(self, ctx:RSTSBasicParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#line.
    def visitLine(self, ctx:RSTSBasicParser.LineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#labelDef.
    def visitLabelDef(self, ctx:RSTSBasicParser.LabelDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#lineNumber.
    def visitLineNumber(self, ctx:RSTSBasicParser.LineNumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#target.
    def visitTarget(self, ctx:RSTSBasicParser.TargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#dataType.
    def visitDataType(self, ctx:RSTSBasicParser.DataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#mapItem.
    def visitMapItem(self, ctx:RSTSBasicParser.MapItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#programStmt.
    def visitProgramStmt(self, ctx:RSTSBasicParser.ProgramStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#declareStmt.
    def visitDeclareStmt(self, ctx:RSTSBasicParser.DeclareStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#printStmt.
    def visitPrintStmt(self, ctx:RSTSBasicParser.PrintStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#letStmt.
    def visitLetStmt(self, ctx:RSTSBasicParser.LetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#gotoStmt.
    def visitGotoStmt(self, ctx:RSTSBasicParser.GotoStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#randomizeStmt.
    def visitRandomizeStmt(self, ctx:RSTSBasicParser.RandomizeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#forStmt.
    def visitForStmt(self, ctx:RSTSBasicParser.ForStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#nextStmt.
    def visitNextStmt(self, ctx:RSTSBasicParser.NextStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#readStmt.
    def visitReadStmt(self, ctx:RSTSBasicParser.ReadStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#dataStmt.
    def visitDataStmt(self, ctx:RSTSBasicParser.DataStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#restoreStmt.
    def visitRestoreStmt(self, ctx:RSTSBasicParser.RestoreStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#ifStmt.
    def visitIfStmt(self, ctx:RSTSBasicParser.IfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#ifBlockStmt.
    def visitIfBlockStmt(self, ctx:RSTSBasicParser.IfBlockStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#thenStmt.
    def visitThenStmt(self, ctx:RSTSBasicParser.ThenStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#elseStmt.
    def visitElseStmt(self, ctx:RSTSBasicParser.ElseStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#endIfStmt.
    def visitEndIfStmt(self, ctx:RSTSBasicParser.EndIfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#endStmt.
    def visitEndStmt(self, ctx:RSTSBasicParser.EndStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#remStmt.
    def visitRemStmt(self, ctx:RSTSBasicParser.RemStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#bangRemStmt.
    def visitBangRemStmt(self, ctx:RSTSBasicParser.BangRemStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#onErrorStmt.
    def visitOnErrorStmt(self, ctx:RSTSBasicParser.OnErrorStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#resumeStmt.
    def visitResumeStmt(self, ctx:RSTSBasicParser.ResumeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#mapStmt.
    def visitMapStmt(self, ctx:RSTSBasicParser.MapStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#openAnyStmt.
    def visitOpenAnyStmt(self, ctx:RSTSBasicParser.OpenAnyStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#closeStmt.
    def visitCloseStmt(self, ctx:RSTSBasicParser.CloseStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#putStmt.
    def visitPutStmt(self, ctx:RSTSBasicParser.PutStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#getStmt.
    def visitGetStmt(self, ctx:RSTSBasicParser.GetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#callStmt.
    def visitCallStmt(self, ctx:RSTSBasicParser.CallStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#inputStmt.
    def visitInputStmt(self, ctx:RSTSBasicParser.InputStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#dimStmt.
    def visitDimStmt(self, ctx:RSTSBasicParser.DimStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#printItem.
    def visitPrintItem(self, ctx:RSTSBasicParser.PrintItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#dataItem.
    def visitDataItem(self, ctx:RSTSBasicParser.DataItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#openClause.
    def visitOpenClause(self, ctx:RSTSBasicParser.OpenClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#strExpr.
    def visitStrExpr(self, ctx:RSTSBasicParser.StrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#floatExpr.
    def visitFloatExpr(self, ctx:RSTSBasicParser.FloatExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#varExpr.
    def visitVarExpr(self, ctx:RSTSBasicParser.VarExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#unaryExpr.
    def visitUnaryExpr(self, ctx:RSTSBasicParser.UnaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#intExpr.
    def visitIntExpr(self, ctx:RSTSBasicParser.IntExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#addSubExpr.
    def visitAddSubExpr(self, ctx:RSTSBasicParser.AddSubExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#logicalExpr.
    def visitLogicalExpr(self, ctx:RSTSBasicParser.LogicalExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#chrExpr.
    def visitChrExpr(self, ctx:RSTSBasicParser.ChrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#parensExpr.
    def visitParensExpr(self, ctx:RSTSBasicParser.ParensExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#relExpr.
    def visitRelExpr(self, ctx:RSTSBasicParser.RelExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#mulDivExpr.
    def visitMulDivExpr(self, ctx:RSTSBasicParser.MulDivExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#inkeyExpr.
    def visitInkeyExpr(self, ctx:RSTSBasicParser.InkeyExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#variable.
    def visitVariable(self, ctx:RSTSBasicParser.VariableContext):
        return self.visitChildren(ctx)



del RSTSBasicParser