import sys
import json
from antlr4 import *
from grammar.RSTSBasicLexer import RSTSBasicLexer
from grammar.RSTSBasicParser import RSTSBasicParser
from grammar.RSTSBasicVisitor import RSTSBasicVisitor

class CodeGenVisitor(RSTSBasicVisitor):
    def __init__(self):
        self.bytecode = []
        self.symbols = []
        self.relocations = []
        self.string_pool = []
        self.variables = {}
        
    def get_var_index(self, name):
        if name not in self.variables:
            self.variables[name] = len(self.variables)
        return self.variables[name]

    def get_string_index(self, text):
        if text not in self.string_pool:
            self.string_pool.append(text)
        return self.string_pool.index(text)

    def visitProgram(self, ctx:RSTSBasicParser.ProgramContext):
        self.symbols.append({"name": "MAIN_START", "type": "EXPORT", "offset": 0})
        for child in ctx.children:
            self.visit(child)
        self.bytecode.append(0x00) # OP_HALT
        return self.generate_bobj()
        
    def visitPrintStmt(self, ctx:RSTSBasicParser.PrintStmtContext):
        for expr in ctx.expression():
            self.visit(expr)
            self.bytecode.append(0x50) # OP_PRINT
            
    def visitOpenSeqStmt(self, ctx:RSTSBasicParser.OpenSeqStmtContext):
        self.visit(ctx.expression()) # Filename
        mode = 1 if ctx.getChild(3).getText() == 'OUTPUT' else 0
        channel = int(ctx.INT().getText())
        self.bytecode.append(0x60) # OP_RMS_OPEN
        self.bytecode.append(channel & 0xFF)
        self.bytecode.append(mode & 0xFF) # Mode (0: SeqIn, 1: SeqOut)
        
    def visitOpenIdxStmt(self, ctx:RSTSBasicParser.OpenIdxStmtContext):
        self.visit(ctx.expression()) # Filename
        channel = int(ctx.INT().getText())
        var_idx = self.get_var_index(ctx.variable().getText())
        self.bytecode.append(0x60) # OP_RMS_OPEN
        self.bytecode.append(channel & 0xFF)
        self.bytecode.append(2) # Mode (2: Indexed)
        self.bytecode.append(var_idx & 0xFF)
        self.bytecode.append((var_idx >> 8) & 0xFF)
        
    def visitCloseStmt(self, ctx:RSTSBasicParser.CloseStmtContext):
        channel = int(ctx.INT().getText())
        self.bytecode.append(0x63) # OP_RMS_CLOS
        self.bytecode.append(channel & 0xFF)
        
    def visitPutStmt(self, ctx:RSTSBasicParser.PutStmtContext):
        channel = int(ctx.INT().getText())
        self.bytecode.append(0x62) # OP_RMS_PUT
        self.bytecode.append(channel & 0xFF)
        
    def visitGetStmt(self, ctx:RSTSBasicParser.GetStmtContext):
        channel = int(ctx.INT().getText())
        has_key = 1 if ctx.variable() else 0
        self.bytecode.append(0x61) # OP_RMS_GET
        self.bytecode.append(channel & 0xFF)
        self.bytecode.append(has_key)
        if has_key:
            var_idx = self.get_var_index(ctx.variable().getText())
            self.bytecode.append(var_idx & 0xFF)
            self.bytecode.append((var_idx >> 8) & 0xFF)
        
    def visitLetStmt(self, ctx:RSTSBasicParser.LetStmtContext):
        self.visit(ctx.expression())
        var_name = ctx.variable().getText()
        idx = self.get_var_index(var_name)
        self.bytecode.append(0x13) # OP_STORE_V
        self.bytecode.append(idx & 0xFF)
        self.bytecode.append((idx >> 8) & 0xFF)
        
    def visitAddSubExpr(self, ctx:RSTSBasicParser.AddSubExprContext):
        self.visit(ctx.left)
        self.visit(ctx.right)
        if ctx.op.text == '+':
            self.bytecode.append(0x20) # OP_ADD
        else:
            self.bytecode.append(0x21) # OP_SUB
            
    def visitIntExpr(self, ctx:RSTSBasicParser.IntExprContext):
        val = int(ctx.INT().getText())
        self.bytecode.append(0x10) # OP_PUSH_I
        self.bytecode.append(val & 0xFF)
        self.bytecode.append((val >> 8) & 0xFF)

    def visitStrExpr(self, ctx:RSTSBasicParser.StrExprContext):
        val = ctx.STRING().getText()
        idx = self.get_string_index(val)
        self.bytecode.append(0x12) # OP_PUSH_S
        self.bytecode.append(idx & 0xFF)
        self.bytecode.append((idx >> 8) & 0xFF)

    def visitVarExpr(self, ctx:RSTSBasicParser.VarExprContext):
        var_name = ctx.variable().getText()
        idx = self.get_var_index(var_name)
        self.bytecode.append(0x14) # OP_LOAD_V
        self.bytecode.append(idx & 0xFF)
        self.bytecode.append((idx >> 8) & 0xFF)

    def generate_bobj(self):
        return {
            "version": 1,
            "module": "MAIN",
            "symbols": self.symbols,
            "relocations": self.relocations,
            "strings": self.string_pool,
            "bytecode": self.bytecode
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: basicc.py <input.bas> [-o output.bobj]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    input_stream = FileStream(input_file)
    lexer = RSTSBasicLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = RSTSBasicParser(stream)
    tree = parser.program()
    
    visitor = CodeGenVisitor()
    bobj = visitor.visit(tree)
    
    output_file = "out.bobj"
    if "-o" in sys.argv:
        output_file = sys.argv[sys.argv.index("-o") + 1]
        
    with open(output_file, 'w') as f:
        json.dump(bobj, f, indent=2)
        
    bin_file = output_file.replace('.bobj', '.bin')
    with open(bin_file, 'wb') as f:
        f.write(bytearray(visitor.bytecode))
        
    print(f"Compiled {input_file} to {output_file} and {bin_file}")

if __name__ == '__main__':
    main()
