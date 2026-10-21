import sys
import json
import struct
from antlr4 import *
from grammar.RSTSBasicLexer import RSTSBasicLexer
from grammar.RSTSBasicParser import RSTSBasicParser
from grammar.RSTSBasicVisitor import RSTSBasicVisitor

class CodeGenVisitor(RSTSBasicVisitor):
    def __init__(self, module_name="MAIN"):
        self.bytecode = []
        self.maps = {}
        self.symbols = []
        self.relocations = []
        self.string_pool = []
        self.variables = {}
        self.module_name = module_name
        self.line_offsets = {}
        self.for_stack = []
        self.block_if_stack = []
        self.data_items = []
        
    def get_var_index(self, name):
        if name not in self.variables:
            self.variables[name] = len(self.variables)
        return self.variables[name]

    def get_target_key(self, target_ctx):
        txt = target_ctx.getText()
        return int(txt) if txt.isdigit() else txt

    def collect_data_items(self, tree):
        # Pre-scan the AST for all DATA statements
        def scan(node):
            if isinstance(node, RSTSBasicParser.DataStmtContext):
                for item in node.dataItem():
                    txt = item.getText()
                    if txt.startswith('"') and txt.endswith('"'):
                        self.data_items.append({"type": 2, "val": txt[1:-1]})
                    elif '.' in txt:
                        self.data_items.append({"type": 1, "val": float(txt)})
                    else:
                        self.data_items.append({"type": 0, "val": int(txt.replace('%', ''))})
            if hasattr(node, 'children') and node.children:
                for child in node.children:
                    scan(child)
        scan(tree)

    def visitProgram(self, ctx:RSTSBasicParser.ProgramContext):
        self.symbols.append({"name": f"{self.module_name}_START", "type": "EXPORT", "offset": 0})
        
        # Pre-scan for DATA statements
        self.collect_data_items(ctx)
        if self.data_items:
            self.bytecode.append(0x76) # OP_INIT_DATA
            count = len(self.data_items)
            self.bytecode.append(count & 0xFF)
            self.bytecode.append((count >> 8) & 0xFF)
            for item in self.data_items:
                self.bytecode.append(item['type'])
                if item['type'] == 0:
                    self.bytecode.extend(struct.pack('<i', item['val']))
                elif item['type'] == 1:
                    self.bytecode.extend(struct.pack('<f', item['val']))
                elif item['type'] == 2:
                    s_bytes = item['val'].encode('utf-8')[:255]
                    self.bytecode.append(len(s_bytes))
                    self.bytecode.extend(s_bytes)

        for child in ctx.children:
            self.visit(child)
            
        if self.module_name == "MAIN":
            self.bytecode.append(0x00) # OP_HALT
        else:
            self.bytecode.append(0x41) # OP_RET
            
        # Resolve JMPs
        for rel in self.relocations:
            if rel['type'] in ['JMP', 'JMP_Z', 'ON_ERROR', 'RESUME']:
                target_line = rel['target_line']
                if target_line in self.line_offsets:
                    offset = self.line_offsets[target_line]
                    loc = rel['offset']
                    self.bytecode[loc] = offset & 0xFF
                    self.bytecode[loc+1] = (offset >> 8) & 0xFF
                else:
                    print(f"Warning: unresolved jump to {target_line}")
                    
        return self.generate_bobj()

    def visitLine(self, ctx:RSTSBasicParser.LineContext):
        start_idx = 0
        if ctx.lineNumber():
            line_num = int(ctx.lineNumber().INT().getText())
            self.line_offsets[line_num] = len(self.bytecode)
            start_idx = 1
        elif ctx.labelDef():
            label_name = ctx.labelDef().ID().getText()
            self.line_offsets[label_name] = len(self.bytecode)
            start_idx = 1
        for i in range(start_idx, ctx.getChildCount()):
            self.visit(ctx.getChild(i))

    def visitProgramStmt(self, ctx:RSTSBasicParser.ProgramStmtContext):
        pass

    def visitDeclareStmt(self, ctx:RSTSBasicParser.DeclareStmtContext):
        for var in ctx.variable():
            self.get_var_index(var.getText().split('(')[0])

    def visitEndStmt(self, ctx:RSTSBasicParser.EndStmtContext):
        self.bytecode.append(0x00) # OP_HALT

    def visitRandomizeStmt(self, ctx:RSTSBasicParser.RandomizeStmtContext):
        pass

    def visitGotoStmt(self, ctx:RSTSBasicParser.GotoStmtContext):
        self.bytecode.append(0x30) # OP_JMP
        target = self.get_target_key(ctx.target())
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP",
            "target_line": target
        })
        self.bytecode.extend([0, 0])

    def visitGosubStmt(self, ctx:RSTSBasicParser.GosubStmtContext):
        self.bytecode.append(0x40) # OP_CALL
        target = self.get_target_key(ctx.target())
        self.relocations.append({
            "offset": len(self.bytecode),
            "type": "JMP",
            "target_line": target
        })
        self.bytecode.extend([0, 0])

    def visitReturnStmt(self, ctx:RSTSBasicParser.ReturnStmtContext):
        self.bytecode.append(0x41) # OP_RET

    def visitIfStmt(self, ctx:RSTSBasicParser.IfStmtContext):
        self.visit(ctx.expression())
        self.bytecode.append(0x31) # OP_JMP_Z
        jmp_loc = len(self.bytecode)
        self.bytecode.extend([0, 0])
        
        if ctx.thenStmt:
            self.visit(ctx.thenStmt)
        else:
            target = self.get_target_key(ctx.thenTarget)
            self.bytecode.append(0x30) # OP_JMP
            self.relocations.append({
                "offset": len(self.bytecode),
                "type": "JMP",
                "target_line": target
            })
            self.bytecode.extend([0, 0])
            
        if ctx.elseStmt or ctx.elseTarget:
            self.bytecode.append(0x30) # OP_JMP
            end_loc = len(self.bytecode)
            self.bytecode.extend([0, 0])
            
            else_offset = len(self.bytecode)
            self.bytecode[jmp_loc] = else_offset & 0xFF
            self.bytecode[jmp_loc+1] = (else_offset >> 8) & 0xFF
            
            if ctx.elseStmt:
                self.visit(ctx.elseStmt)
            else:
                target = self.get_target_key(ctx.elseTarget)
                self.bytecode.append(0x30) # OP_JMP
                self.relocations.append({
                    "offset": len(self.bytecode),
                    "type": "JMP",
                    "target_line": target
                })
                self.bytecode.extend([0, 0])
                
            end_offset = len(self.bytecode)
            self.bytecode[end_loc] = end_offset & 0xFF
            self.bytecode[end_loc+1] = (end_offset >> 8) & 0xFF
        else:
            end_offset = len(self.bytecode)
            self.bytecode[jmp_loc] = end_offset & 0xFF
            self.bytecode[jmp_loc+1] = (end_offset >> 8) & 0xFF

    def visitIfBlockStmt(self, ctx:RSTSBasicParser.IfBlockStmtContext):
        self.visit(ctx.expression())
        self.bytecode.append(0x31) # OP_JMP_Z
        jmp_loc = len(self.bytecode)
        self.bytecode.extend([0, 0])
        self.block_if_stack.append({'type': 'IF', 'jmp_loc': jmp_loc})

    def visitThenStmt(self, ctx:RSTSBasicParser.ThenStmtContext):
        if ctx.statement():
            self.visit(ctx.statement())

    def visitElseStmt(self, ctx:RSTSBasicParser.ElseStmtContext):
        if self.block_if_stack:
            top = self.block_if_stack.pop()
            self.bytecode.append(0x30) # OP_JMP past END IF
            end_loc = len(self.bytecode)
            self.bytecode.extend([0, 0])
            
            else_offset = len(self.bytecode)
            self.bytecode[top['jmp_loc']] = else_offset & 0xFF
            self.bytecode[top['jmp_loc'] + 1] = (else_offset >> 8) & 0xFF
            self.block_if_stack.append({'type': 'ELSE', 'end_loc': end_loc})
        if ctx.statement():
            self.visit(ctx.statement())

    def visitEndIfStmt(self, ctx:RSTSBasicParser.EndIfStmtContext):
        if self.block_if_stack:
            top = self.block_if_stack.pop()
            end_offset = len(self.bytecode)
            loc = top['jmp_loc'] if top['type'] == 'IF' else top['end_loc']
            self.bytecode[loc] = end_offset & 0xFF
            self.bytecode[loc + 1] = (end_offset >> 8) & 0xFF

    def visitForStmt(self, ctx:RSTSBasicParser.ForStmtContext):
        var_name = ctx.variable().getText().split('(')[0]
        var_idx = self.get_var_index(var_name)
        
        # fromExpr
        self.visit(ctx.fromExpr)
        self.bytecode.append(0x13) # OP_STORE_V
        self.bytecode.append(var_idx & 0xFF)
        self.bytecode.append((var_idx >> 8) & 0xFF)
        
        loop_start = len(self.bytecode)
        # Load var
        self.bytecode.append(0x14) # OP_LOAD_V
        self.bytecode.append(var_idx & 0xFF)
        self.bytecode.append((var_idx >> 8) & 0xFF)
        
        # Evaluate toExpr
        self.visit(ctx.toExpr)
        
        # Check var <= toExpr (NOT var > toExpr)
        self.bytecode.append(0x27) # OP_GT
        self.bytecode.append(0x10); self.bytecode.extend([0, 0]) # push 0
        self.bytecode.append(0x24) # OP_EQ
        self.bytecode.append(0x31) # OP_JMP_Z
        exit_jmp_loc = len(self.bytecode)
        self.bytecode.extend([0, 0])
        
        self.for_stack.append({
            'var_idx': var_idx,
            'loop_start': loop_start,
            'exit_jmp_loc': exit_jmp_loc,
            'stepExpr': ctx.stepExpr
        })

    def visitNextStmt(self, ctx:RSTSBasicParser.NextStmtContext):
        if self.for_stack:
            info = self.for_stack.pop()
            var_idx = info['var_idx']
            # Load var
            self.bytecode.append(0x14) # OP_LOAD_V
            self.bytecode.append(var_idx & 0xFF)
            self.bytecode.append((var_idx >> 8) & 0xFF)
            
            # Step
            if info['stepExpr']:
                self.visit(info['stepExpr'])
            else:
                self.bytecode.append(0x10); self.bytecode.extend([1, 0]) # push 1
                
            # Add
            self.bytecode.append(0x20) # OP_ADD
            # Store var
            self.bytecode.append(0x13) # OP_STORE_V
            self.bytecode.append(var_idx & 0xFF)
            self.bytecode.append((var_idx >> 8) & 0xFF)
            
            # Jump back to loop_start
            self.bytecode.append(0x30) # OP_JMP
            loop_start = info['loop_start']
            self.bytecode.append(loop_start & 0xFF)
            self.bytecode.append((loop_start >> 8) & 0xFF)
            
            # Patch exit_jmp_loc
            end_offset = len(self.bytecode)
            self.bytecode[info['exit_jmp_loc']] = end_offset & 0xFF
            self.bytecode[info['exit_jmp_loc'] + 1] = (end_offset >> 8) & 0xFF

    def visitReadStmt(self, ctx:RSTSBasicParser.ReadStmtContext):
        for var in ctx.variable():
            var_name = var.getText().split('(')[0]
            var_idx = self.get_var_index(var_name)
            self.bytecode.append(0x77) # OP_READ
            self.bytecode.append(var_idx & 0xFF)
            self.bytecode.append((var_idx >> 8) & 0xFF)

    def visitDataStmt(self, ctx:RSTSBasicParser.DataStmtContext):
        pass

    def visitRestoreStmt(self, ctx:RSTSBasicParser.RestoreStmtContext):
        channel = 0
        key_idx = 0
        if ctx.INT():
            channel = int(ctx.INT(0).getText().replace('%', ''))
            if len(ctx.INT()) > 1:
                key_idx = int(ctx.INT(1).getText().replace('%', ''))
        self.bytecode.append(0x64) # OP_RMS_REST
        self.bytecode.append(channel & 0xFF)
        self.bytecode.append(key_idx & 0xFF)

    def visitInputStmt(self, ctx:RSTSBasicParser.InputStmtContext):
        if ctx.INT():
            channel = int(ctx.INT().getText().replace('%', ''))
            var_ctx = ctx.variable()
            var_name = var_ctx.getText().split('(')[0]
            idx = self.get_var_index(var_name)
            self.bytecode.append(0x7B) # OP_INPUT_LINE_CH
            self.bytecode.append(channel & 0xFF)
            self.bytecode.append(idx & 0xFF)
            self.bytecode.append((idx >> 8) & 0xFF)
            return

        if ctx.STRING():
            val = ctx.STRING().getText().strip('"')
            self.bytecode.append(0x12) # OP_PUSH_S
            self.bytecode.append(len(val) & 0xFF)
            for char in val:
                self.bytecode.append(ord(char))
            self.bytecode.append(0x51) # OP_PRINT_NO_NL
        var_ctx = ctx.variable()
        var_name = var_ctx.getText().split('(')[0]
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

    def visitBangRemStmt(self, ctx:RSTSBasicParser.BangRemStmtContext):
        pass

    def visitRemStmt(self, ctx:RSTSBasicParser.RemStmtContext):
        pass

    def visitMapStmt(self, ctx:RSTSBasicParser.MapStmtContext):
        map_name = ctx.variable().getText()
        var_indices = []
        for mapItem in ctx.mapItem():
            var_name = mapItem.variable().getText()
            var_indices.append(self.get_var_index(var_name))
        self.maps[map_name] = var_indices

    def visitOnErrorStmt(self, ctx:RSTSBasicParser.OnErrorStmtContext):
        target = self.get_target_key(ctx.target())
        err_var_idx = self.get_var_index("ERR")
        if target == 0 or target == "0":
            self.bytecode.append(0x78) # OP_ON_ERROR
            self.bytecode.extend([0, 0, 0, 0])
        else:
            self.bytecode.append(0x78) # OP_ON_ERROR
            self.relocations.append({
                "offset": len(self.bytecode),
                "type": "ON_ERROR",
                "target_line": target
            })
            self.bytecode.extend([0, 0])
            self.bytecode.append(err_var_idx & 0xFF)
            self.bytecode.append((err_var_idx >> 8) & 0xFF)

    def visitResumeStmt(self, ctx:RSTSBasicParser.ResumeStmtContext):
        self.bytecode.append(0x79) # OP_RESUME
        if ctx.target():
            target = self.get_target_key(ctx.target())
            self.relocations.append({
                "offset": len(self.bytecode),
                "type": "RESUME",
                "target_line": target
            })
            self.bytecode.extend([0, 0])
        else:
            self.bytecode.extend([0, 0])

    def visitPrintStmt(self, ctx:RSTSBasicParser.PrintStmtContext):
        channel = 0
        if ctx.INT():
            channel = int(ctx.INT().getText().replace('%', ''))
            
        if ctx.formatExpr:
            self.visit(ctx.formatExpr)
            items = ctx.printItem()
            for item in items:
                self.visit(item)
            self.bytecode.append(0x53) # OP_PRINT_USING
            self.bytecode.append(channel & 0xFF)
            self.bytecode.append(len(items) & 0xFF)
            return

        items = ctx.printItem()
        if not items:
            self.bytecode.append(0x12) # OP_PUSH_S
            self.bytecode.append(0) # len 0
            self.bytecode.append(0x52) # OP_PRINT_CH
            self.bytecode.append(channel & 0xFF)
            self.bytecode.append(1) # with NL
            return

        for i, item in enumerate(items):
            self.visit(item)
            is_last = (i == len(items) - 1)
            ends_with_delim = ctx.getChild(ctx.getChildCount() - 1).getText() in [';', ',']
            nl = 1 if (is_last and not ends_with_delim) else 0
            self.bytecode.append(0x52) # OP_PRINT_CH
            self.bytecode.append(channel & 0xFF)
            self.bytecode.append(nl & 0xFF)

    def visitInkeyExpr(self, ctx:RSTSBasicParser.InkeyExprContext):
        self.bytecode.append(0x72) # OP_GETCH

    def visitChrExpr(self, ctx:RSTSBasicParser.ChrExprContext):
        self.visit(ctx.expression())
        self.bytecode.append(0x73) # OP_CHR

    def visitOpenAnyStmt(self, ctx:RSTSBasicParser.OpenAnyStmtContext):
        self.visit(ctx.expression()) # Push filename
        is_indexed = False
        primary_key_var = None
        for clause in ctx.openClause():
            text = clause.getText()
            if 'INDEXED' in text:
                is_indexed = True
            if 'PRIMARY' in text:
                primary_key_var = clause.variable().getText()

        mode_text = ""
        for i in range(ctx.getChildCount()):
            if ctx.getChild(i).getText() == 'FOR':
                mode_text = ctx.getChild(i+1).getText()
        
        mode = 0 # INPUT
        if mode_text == 'OUTPUT': mode = 1
        elif mode_text == 'MODIFY': mode = 2
        
        if is_indexed:
            if mode_text == 'OUTPUT':
                mode = 3 # Indexed Write/Recreate
            elif mode_text == 'INPUT':
                mode = 2 # Indexed Read
            else:
                mode = 2 # Indexed Modify/Read

        map_name = None
        for clause in ctx.openClause():
            if 'MAP' in clause.getText():
                map_name = clause.variable().getText()
                
        channel = int(ctx.INT().getText().replace('%', ''))
        self.bytecode.append(0x60) # OP_RMS_OPEN
        self.bytecode.append(channel & 0xFF)
        self.bytecode.append(mode & 0xFF)
        if (mode == 2 or mode == 3) and primary_key_var:
            var_idx = self.get_var_index(primary_key_var)
            self.bytecode.append(var_idx & 0xFF)
            self.bytecode.append((var_idx >> 8) & 0xFF)
        elif mode == 2 or mode == 3:
            self.bytecode.extend([0, 0])
            
        mapped_vars = []
        if map_name and map_name in self.maps:
            mapped_vars = self.maps[map_name]
            
        self.bytecode.append(len(mapped_vars) & 0xFF)
        for v in mapped_vars:
            self.bytecode.append(v & 0xFF)
            self.bytecode.append((v >> 8) & 0xFF)

    def visitCloseStmt(self, ctx:RSTSBasicParser.CloseStmtContext):
        for int_tok in ctx.INT():
            channel = int(int_tok.getText().replace('%', ''))
            self.bytecode.append(0x63) # OP_RMS_CLOS
            self.bytecode.append(channel & 0xFF)

    def visitPutStmt(self, ctx:RSTSBasicParser.PutStmtContext):
        channel = int(ctx.INT().getText().replace('%', ''))
        self.bytecode.append(0x62) # OP_RMS_PUT
        self.bytecode.append(channel & 0xFF)

    def visitGetStmt(self, ctx:RSTSBasicParser.GetStmtContext):
        channel = int(ctx.INT(0).getText().replace('%', ''))
        has_key = 1 if ctx.expression() else 0
        self.bytecode.append(0x61) # OP_RMS_GET
        self.bytecode.append(channel & 0xFF)
        self.bytecode.append(has_key)
        if has_key:
            var_name = ctx.expression().getText()
            var_idx = self.get_var_index(var_name)
            self.bytecode.append(var_idx & 0xFF)
            self.bytecode.append((var_idx >> 8) & 0xFF)

    def visitDimStmt(self, ctx:RSTSBasicParser.DimStmtContext):
        for var_ctx in ctx.variable():
            var_name = var_ctx.getText().split('(')[0]
            idx = self.get_var_index(var_name)
            self.visit(var_ctx.expression(0))
            self.bytecode.append(0x15) # OP_DIM
            self.bytecode.append(idx & 0xFF)
            self.bytecode.append((idx >> 8) & 0xFF)

    def visitLetStmt(self, ctx:RSTSBasicParser.LetStmtContext):
        self.visit(ctx.expression())
        var_ctx = ctx.variable()
        var_name = var_ctx.getText().split('(')[0]
        idx = self.get_var_index(var_name)
        if var_ctx.expression(): # Array access
            self.visit(var_ctx.expression(0))
            self.bytecode.append(0x16) # OP_STORE_A
        else:
            self.bytecode.append(0x13) # OP_STORE_V
        self.bytecode.append(idx & 0xFF)
        self.bytecode.append((idx >> 8) & 0xFF)

    def visitMulDivExpr(self, ctx:RSTSBasicParser.MulDivExprContext):
        self.visit(ctx.left)
        self.visit(ctx.right)
        if ctx.op.text == '*': self.bytecode.append(0x22)
        else: self.bytecode.append(0x23)

    def visitAddSubExpr(self, ctx:RSTSBasicParser.AddSubExprContext):
        self.visit(ctx.left)
        self.visit(ctx.right)
        if ctx.op.text == '+': self.bytecode.append(0x20)
        else: self.bytecode.append(0x21)

    def visitUnaryExpr(self, ctx:RSTSBasicParser.UnaryExprContext):
        if ctx.op.text == '-':
            self.bytecode.append(0x10); self.bytecode.extend([0, 0]) # push 0
            self.visit(ctx.expression())
            self.bytecode.append(0x21) # OP_SUB (0 - expr)
        else:
            self.visit(ctx.expression())

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

    def visitLogicalExpr(self, ctx:RSTSBasicParser.LogicalExprContext):
        self.visit(ctx.left)
        self.visit(ctx.right)
        if ctx.op.text == 'AND':
            self.bytecode.append(0x28) # OP_AND
        else:
            self.bytecode.append(0x29) # OP_OR

    def visitIntExpr(self, ctx:RSTSBasicParser.IntExprContext):
        val = int(ctx.INT().getText().replace("%", ""))
        self.bytecode.append(0x10) # OP_PUSH_I
        self.bytecode.append(val & 0xFF)
        self.bytecode.append((val >> 8) & 0xFF)

    def visitFloatExpr(self, ctx:RSTSBasicParser.FloatExprContext):
        val = float(ctx.FLOAT().getText())
        self.bytecode.append(0x11) # OP_PUSH_F
        self.bytecode.extend(struct.pack('<f', val))

    def visitStrExpr(self, ctx:RSTSBasicParser.StrExprContext):
        val = ctx.STRING().getText().strip('"')
        val = val.replace('\\n', '\n').replace('\\033', '\033').replace('\\e', '\033').replace('\\t', '\t')
        self.bytecode.append(0x12) # OP_PUSH_S
        self.bytecode.append(len(val) & 0xFF)
        for char in val:
            self.bytecode.append(ord(char))

    def visitVarExpr(self, ctx:RSTSBasicParser.VarExprContext):
        var_ctx = ctx.variable()
        var_name = var_ctx.getText().split('(')[0]
        if var_name in ["DATE$", "DATE"]:
            if var_ctx.expression():
                self.visit(var_ctx.expression(0))
            else:
                self.bytecode.append(0x10); self.bytecode.extend([0, 0])
            self.bytecode.append(0x7A) # OP_DATE_STR
            return
        if var_name == "RND":
            self.bytecode.append(0x74) # OP_RND
            return
        if var_name == "INT" and var_ctx.expression():
            self.visit(var_ctx.expression(0))
            self.bytecode.append(0x75) # OP_INT
            return
        if var_name == "LEN" and var_ctx.expression():
            self.visit(var_ctx.expression(0))
            self.bytecode.append(0x7C) # OP_LEN
            return
        if var_name in ["MID$", "MID"] and len(var_ctx.expression()) >= 3:
            self.visit(var_ctx.expression(0))
            self.visit(var_ctx.expression(1))
            self.visit(var_ctx.expression(2))
            self.bytecode.append(0x7D) # OP_MID
            return
        if var_name in ["LEFT$", "LEFT"] and len(var_ctx.expression()) >= 2:
            self.visit(var_ctx.expression(0))
            self.visit(var_ctx.expression(1))
            self.bytecode.append(0x7E) # OP_LEFT
            return
        if var_name in ["RIGHT$", "RIGHT"] and len(var_ctx.expression()) >= 2:
            self.visit(var_ctx.expression(0))
            self.visit(var_ctx.expression(1))
            self.bytecode.append(0x7F) # OP_RIGHT
            return
        if var_name == "INSTR" and len(var_ctx.expression()) >= 2:
            if len(var_ctx.expression()) == 2:
                self.bytecode.append(0x10); self.bytecode.extend([1, 0]) # default start=1
                self.visit(var_ctx.expression(0))
                self.visit(var_ctx.expression(1))
            else:
                self.visit(var_ctx.expression(0))
                self.visit(var_ctx.expression(1))
                self.visit(var_ctx.expression(2))
            self.bytecode.append(0x80) # OP_INSTR
            return
        if var_name == "VAL" and var_ctx.expression():
            self.visit(var_ctx.expression(0))
            self.bytecode.append(0x81) # OP_VAL
            return
        if var_name in ["STR$", "STR"] and var_ctx.expression():
            self.visit(var_ctx.expression(0))
            self.bytecode.append(0x82) # OP_STR
            return
        if var_name in ["ASCII", "ASC"] and var_ctx.expression():
            self.visit(var_ctx.expression(0))
            self.bytecode.append(0x83) # OP_ASCII
            return
        if var_name in ["COMMAND$", "COMMAND"]:
            self.bytecode.append(0x85) # OP_COMMAND_STR
            return
        if var_name in ["TIME$", "TIME"]:
            if var_ctx.expression():
                self.visit(var_ctx.expression(0))
            else:
                self.bytecode.append(0x10); self.bytecode.extend([0, 0])
            self.bytecode.append(0x86) # OP_TIME_STR
            return
        if var_name == "SYS" and var_ctx.expression():
            self.visit(var_ctx.expression(0))
            self.bytecode.append(0x84) # OP_SYS
            return

        idx = self.get_var_index(var_name)
        if var_ctx.expression():
            self.visit(var_ctx.expression(0))
            self.bytecode.append(0x17) # OP_LOAD_A
        else:
            self.bytecode.append(0x14) # OP_LOAD_V
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
        print("Usage: basicc.py <input.bas> [-o output.obj] [--module NAME]")
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
    obj = visitor.visit(tree)
    
    output_file = "out.obj"
    if "-o" in sys.argv:
        output_file = sys.argv[sys.argv.index("-o") + 1]
        
    with open(output_file, 'w') as f:
        json.dump(obj, f, indent=2)
        
    if output_file.lower().endswith('.obj'):
        bin_file = output_file[:-4] + '.bin'
    else:
        bin_file = output_file + '.bin'
    with open(bin_file, 'wb') as f:
        f.write(bytearray(visitor.bytecode))
        
    print(f"Compiled {input_file} to {output_file} and {bin_file}")

if __name__ == '__main__':
    main()
