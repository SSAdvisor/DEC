import sys
import json
from antlr4 import *
from grammar.RSTSBasicLexer import RSTSBasicLexer
from grammar.RSTSBasicParser import RSTSBasicParser
from grammar.RSTSBasicVisitor import RSTSBasicVisitor

class CodeGenVisitor(RSTSBasicVisitor):
    def __init__(self, module_name="MAIN"):
        self.bytecode = []
        self.symbols = []
        self.relocations = []
        self.string_pool = []
        self.variables = {}
        self.module_name = module_name
        self.line_offsets = {}
        
    def get_var_index(self, name):
        if name not in self.variables:
            self.variables[name] = len(self.variables)
        return self.variables[name]

    def visitProgram(self, ctx:RSTSBasicParser.ProgramContext):
        self.symbols.append({"name": f"{self.module_name}_START", "type": "EXPORT", "offset": 0})
        for child in ctx.children:
            self.visit(child)
        if self.module_name == "MAIN":
            self.bytecode.append(0x00) # OP_HALT
        else:
            self.bytecode.append(0x41) # OP_RET
            
        # Resolve JMPs
        for rel in self.relocations:
            if rel['type'] in ['JMP', 'JMP_Z']:
                target_line = rel['target_line']
                if target_line in self.line_offsets:
                    offset = self.line_offsets[target_line]
                    loc = rel['offset']
                    self.bytecode[loc] = offset & 0xFF
                    self.bytecode[loc+1] = (offset >> 8) & 0xFF
                else:
                    print(f"Warning: unresolved jump to line {target_line}")
                    
        return self.generate_bobj()

    def visitLine(self, ctx:RSTSBasicParser.LineContext):
        if ctx.lineNumber():
            line_num = int(ctx.lineNumber().INT().getText())
            self.line_offsets[line_num] = len(self.bytecode)
        for i in range(1, ctx.getChildCount()):
            self.visit(ctx.getChild(i))
            
    def visitGotoStmt(self, ctx:RSTSBasicParser.GotoStmtContext):
        self.bytecode.append(0x30) # OP_JMP
        target_line = int(ctx.lineNumber().getText())
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP",
            "target_line": target_line
        })
        self.bytecode.extend([0, 0])

    def visitIfStmt(self, ctx:RSTSBasicParser.IfStmtContext):
        self.visit(ctx.expression())
        self.bytecode.append(0x31) # OP_JMP_Z
        jmp_loc = len(self.bytecode)
        self.bytecode.extend([0, 0])
        self.visit(ctx.statement(0))
        
        if ctx.getChildCount() > 4: # Has ELSE
            self.bytecode.append(0x30) # OP_JMP
            end_loc = len(self.bytecode)
            self.bytecode.extend([0, 0])
            
            else_offset = len(self.bytecode)
            self.bytecode[jmp_loc] = else_offset & 0xFF
            self.bytecode[jmp_loc+1] = (else_offset >> 8) & 0xFF
            
            self.visit(ctx.statement(1))
            
            end_offset = len(self.bytecode)
            self.bytecode[end_loc] = end_offset & 0xFF
            self.bytecode[end_loc+1] = (end_offset >> 8) & 0xFF
        else:
            end_offset = len(self.bytecode)
            self.bytecode[jmp_loc] = end_offset & 0xFF
            self.bytecode[jmp_loc+1] = (end_offset >> 8) & 0xFF

    def visitInputStmt(self, ctx:RSTSBasicParser.InputStmtContext):
        var_name = ctx.variable().getText()
        idx = self.get_var_index(var_name)
        if var_name.endswith('$'):
            self.bytecode.append(0x71) # OP_INPUT_S
        else:
            self.bytecode.append(0x70) # OP_INPUT_I
        self.bytecode.append(idx & 0xFF)
        self.bytecode.append((idx >> 8) & 0xFF)

    def visitCallStmt(self, ctx:RSTSBasicParser.CallStmtContext):
        module_name = ctx.STRING().getText().strip('"')
        self.bytecode.append(0x42) # OP_CALL_OVL
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "CALL_OVL",
            "target": module_name
        })
        self.bytecode.extend([0, 0])

    def visitPrintStmt(self, ctx:RSTSBasicParser.PrintStmtContext):
        for expr in ctx.expression():
            self.visit(expr)
            self.bytecode.append(0x50) # OP_PRINT
            
    def visitOpenSeqStmt(self, ctx:RSTSBasicParser.OpenSeqStmtContext):
        self.visit(ctx.expression())
        mode = 1 if ctx.getChild(3).getText() == 'OUTPUT' else 0
        channel = int(ctx.INT().getText())
        self.bytecode.append(0x60)
        self.bytecode.append(channel & 0xFF)
        self.bytecode.append(mode & 0xFF)
        
    def visitOpenIdxStmt(self, ctx:RSTSBasicParser.OpenIdxStmtContext):
        self.visit(ctx.expression())
        channel = int(ctx.INT().getText())
        var_idx = self.get_var_index(ctx.variable().getText())
        self.bytecode.append(0x60)
        self.bytecode.append(channel & 0xFF)
        self.bytecode.append(2)
        self.bytecode.append(var_idx & 0xFF)
        self.bytecode.append((var_idx >> 8) & 0xFF)
        
    def visitCloseStmt(self, ctx:RSTSBasicParser.CloseStmtContext):
        channel = int(ctx.INT().getText())
        self.bytecode.append(0x63)
        self.bytecode.append(channel & 0xFF)
        
    def visitPutStmt(self, ctx:RSTSBasicParser.PutStmtContext):
        channel = int(ctx.INT().getText())
        self.bytecode.append(0x62)
        self.bytecode.append(channel & 0xFF)
        
    def visitGetStmt(self, ctx:RSTSBasicParser.GetStmtContext):
        channel = int(ctx.INT().getText())
        has_key = 1 if ctx.variable() else 0
        self.bytecode.append(0x61)
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
        if ctx.op.text == '+': self.bytecode.append(0x20)
        else: self.bytecode.append(0x21)

    def visitRelExpr(self, ctx:RSTSBasicParser.RelExprContext):
        self.visit(ctx.left)
        self.visit(ctx.right)
        op = ctx.op.text
        if op == '=': self.bytecode.append(0x24)
        elif op == '<>': self.bytecode.append(0x25)
        elif op == '<': self.bytecode.append(0x26)
        elif op == '>': self.bytecode.append(0x27)
        elif op == '<=': 
            self.bytecode.append(0x27) # OP_GT
            self.bytecode.append(0x10); self.bytecode.extend([0, 0]) # push 0
            self.bytecode.append(0x24) # OP_EQ (NOT GT)
        elif op == '>=': 
            self.bytecode.append(0x26) # OP_LT
            self.bytecode.append(0x10); self.bytecode.extend([0, 0]) # push 0
            self.bytecode.append(0x24) # OP_EQ (NOT LT)
            
    def visitIntExpr(self, ctx:RSTSBasicParser.IntExprContext):
        val = int(ctx.INT().getText())
        self.bytecode.append(0x10)
        self.bytecode.append(val & 0xFF)
        self.bytecode.append((val >> 8) & 0xFF)

    def visitStrExpr(self, ctx:RSTSBasicParser.StrExprContext):
        val = ctx.STRING().getText().strip('"')
        self.bytecode.append(0x12) # OP_PUSH_S
        self.bytecode.append(len(val) & 0xFF)
        for char in val:
            self.bytecode.append(ord(char))

    def visitVarExpr(self, ctx:RSTSBasicParser.VarExprContext):
        var_name = ctx.variable().getText()
        idx = self.get_var_index(var_name)
        self.bytecode.append(0x14)
        self.bytecode.append(idx & 0xFF)
        self.bytecode.append((idx >> 8) & 0xFF)

    def visitParensExpr(self, ctx:RSTSBasicParser.ParensExprContext):
        self.visit(ctx.expression())

    def generate_bobj(self):
        return {
            "version": 1,
            "module": self.module_name,
            "symbols": self.symbols,
            "relocations": self.relocations,
            "strings": self.string_pool,
            "bytecode": self.bytecode
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: basicc.py <input.bas> [-o output.bobj] [--module NAME]")
        sys.exit(1)
        
    module_name = "MAIN"
    if "--module" in sys.argv:
        idx = sys.argv.index("--module")
        module_name = sys.argv[idx + 1]
        sys.argv.pop(idx)
        sys.argv.pop(idx)
        
    input_file = sys.argv[1]
    input_stream = FileStream(input_file)
    lexer = RSTSBasicLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = RSTSBasicParser(stream)
    tree = parser.program()
    
    visitor = CodeGenVisitor(module_name)
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
