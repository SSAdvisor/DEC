# Generated from RSTSBasic.g4 by ANTLR 4.13.1
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


    # Visit a parse tree produced by RSTSBasicParser#lineNumber.
    def visitLineNumber(self, ctx:RSTSBasicParser.LineNumberContext):
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


    # Visit a parse tree produced by RSTSBasicParser#ifStmt.
    def visitIfStmt(self, ctx:RSTSBasicParser.IfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#endStmt.
    def visitEndStmt(self, ctx:RSTSBasicParser.EndStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#remStmt.
    def visitRemStmt(self, ctx:RSTSBasicParser.RemStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#openSeqStmt.
    def visitOpenSeqStmt(self, ctx:RSTSBasicParser.OpenSeqStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#openIdxStmt.
    def visitOpenIdxStmt(self, ctx:RSTSBasicParser.OpenIdxStmtContext):
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


    # Visit a parse tree produced by RSTSBasicParser#strExpr.
    def visitStrExpr(self, ctx:RSTSBasicParser.StrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#floatExpr.
    def visitFloatExpr(self, ctx:RSTSBasicParser.FloatExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#varExpr.
    def visitVarExpr(self, ctx:RSTSBasicParser.VarExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#intExpr.
    def visitIntExpr(self, ctx:RSTSBasicParser.IntExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSTSBasicParser#addSubExpr.
    def visitAddSubExpr(self, ctx:RSTSBasicParser.AddSubExprContext):
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


    # Visit a parse tree produced by RSTSBasicParser#variable.
    def visitVariable(self, ctx:RSTSBasicParser.VariableContext):
        return self.visitChildren(ctx)



del RSTSBasicParser