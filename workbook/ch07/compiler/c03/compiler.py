#!/usr/bin/env python3
# DOESN'T WORK!!!
import sys
import os
import json
from typing import Tuple, Optional, List, Callable, Any
from abc import ABC, abstractmethod



class Lexer:
    def __init__(self, code: str):
        self.code = code.strip()
        self.tokens = []
        self.pos = 0
        self.keywords = {"begin", "end", "end.", "if", "then", "while", "do", "var", "call", "procedure", "!", "?"}
        self.operators = {"<=", ">=", "<", ">", "=", "+", "-", "*", "/", "(", ")", ":=", ";", ","}
        self.tokenize()

    def tokenize(self):
        while self.pos < len(self.code):
            if self.code[self.pos].isspace():
                self.pos += 1
                continue
            if self.pos + 4 <= len(self.code) and self.code[self.pos:self.pos+4] == "end.":
                self.tokens.append(("end.", "kw"))
                self.pos += 4
                continue
            if self.code[self.pos].isalpha():
                token = self.read_alpha()
                kind = "kw" if token in self.keywords else "id"
            elif self.code[self.pos].isdigit():
                token = self.read_digit()
                kind = "num"
            elif self.code[self.pos] in "<>=+-*/();,?!" or self.code[self.pos:self.pos+2] in {":=", "<=", ">="}:
                token = self.read_operator()
                kind = "kw" if token in {"!", "?"} else "asgn" if token == ":=" else "semi" if token == ";" else "comma" if token == "," else "op"
            else:
                raise SyntaxError(f"Unexpected character: '{self.code[self.pos]}'")
            self.tokens.append((token, kind))

    def read_alpha(self):
        start = self.pos
        while self.pos < len(self.code) and self.code[self.pos].isalpha():
            self.pos += 1
        return self.code[start:self.pos]

    def read_digit(self):
        start = self.pos
        while self.pos < len(self.code) and self.code[self.pos].isdigit():
            self.pos += 1
        return self.code[start:self.pos]

    def read_operator(self):
        if self.pos + 1 < len(self.code):
            two_char = self.code[self.pos:self.pos+2]
            if two_char in {"<=", ">=", ":="}:
                self.pos += 2
                return two_char
        token = self.code[self.pos]
        self.pos += 1
        return token



class ASTNode(ABC):
    @abstractmethod
    def accept(self, visitor): pass

    @abstractmethod
    def to_dict(self): pass


class BlockNode(ASTNode):
    def __init__(self, variables: List[str], procedures: List[Tuple[str, 'BlockNode']], statement: ASTNode):
        self.variables = variables
        self.procedures = procedures
        self.statement = statement

    def accept(self, visitor): return visitor.visit_block(self)

    def to_dict(self):
        return {
            "type": "Block",
            "variables": self.variables,
            "procedures": [{"name": n, "body": b.to_dict()} for n,b in self.procedures],
            "statement": self.statement.to_dict() if self.statement else None
        }


class AssignNode(ASTNode):
    def __init__(self, var_name: str, expression: ASTNode):
        self.var_name = var_name
        self.expression = expression

    def accept(self, visitor): return visitor.visit_assign(self)

    def to_dict(self):
        return {"type": "Assign", "var": self.var_name, "expr": self.expression.to_dict()}


class CallNode(ASTNode):
    def __init__(self, proc_name: str):
        self.proc_name = proc_name

    def accept(self, visitor): return visitor.visit_call(self)

    def to_dict(self):
        return {"type": "Call", "proc": self.proc_name}


class CompoundNode(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

    def accept(self, visitor): return visitor.visit_compound(self)

    def to_dict(self):
        return {"type": "Compound", "statements": [s.to_dict() for s in self.statements]}


class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, statement: ASTNode):
        self.condition = condition
        self.statement = statement

    def accept(self, visitor): return visitor.visit_if(self)

    def to_dict(self):
        return {"type": "If", "cond": self.condition.to_dict(), "then": self.statement.to_dict()}


class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, statement: ASTNode):
        self.condition = condition
        self.statement = statement

    def accept(self, visitor): return visitor.visit_while(self)

    def to_dict(self):
        return {"type": "While", "cond": self.condition.to_dict(), "do": self.statement.to_dict()}


class ReadNode(ASTNode):
    def __init__(self, var_name: str):
        self.var_name = var_name

    def accept(self, visitor): return visitor.visit_read(self)

    def to_dict(self):
        return {"type": "Read", "var": self.var_name}


class WriteNode(ASTNode):
    def __init__(self, expression: ASTNode):
        self.expression = expression

    def accept(self, visitor): return visitor.visit_write(self)

    def to_dict(self):
        return {"type": "Write", "expr": self.expression.to_dict()}


class OddNode(ASTNode):
    def __init__(self, expression: ASTNode):
        self.expression = expression

    def accept(self, visitor): return visitor.visit_odd(self)

    def to_dict(self):
        return {"type": "Odd", "expr": self.expression.to_dict()}


class OperationNode(ASTNode):
    def __init__(self, left: ASTNode, operator: str, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor): return visitor.visit_operation(self)

    def to_dict(self):
        return {"type": "Op", "op": self.operator, "left": self.left.to_dict(), "right": self.right.to_dict()}


class NumberNode(ASTNode):
    def __init__(self, value: int):
        self.value = value

    def accept(self, visitor): return visitor.visit_number(self)

    def to_dict(self):
        return {"type": "Number", "value": self.value}


class VariableNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def accept(self, visitor): return visitor.visit_variable(self)

    def to_dict(self):
        return {"type": "Variable", "name": self.name}



class PackratParser:
    def __init__(self, tokens: List[Tuple[str, str]]):
        self.tokens = tokens
        self.cache = {}  # (rule, pos) -> (result, new_pos)

    def parse(self):
        result, pos = self.program(0)
        if result is None or pos != len(self.tokens):
            raise SyntaxError("Incomplete parse")
        return result

    def memoize(self, rule: str, pos: int, func: Callable[[int], Tuple[Any, int]]) -> Tuple[Any, int]:
        key = (rule, pos)
        if key in self.cache:
            print(f"DEBUG: Cache hit for {rule} at pos {pos}")
            return self.cache[key]
        result = func(pos)
        self.cache[key] = result
        return result

    def program(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _program(p: int) -> Tuple[Optional[ASTNode], int]:
            print(f"DEBUG: Entering program at pos {p}")
            block, p = self.block(p)
            if block is None:
                print(f"DEBUG: Failed to parse block at pos {p}")
                return None, p
            if p == len(self.tokens) or (p < len(self.tokens) and self.tokens[p] == ("end.", "kw")):
                if p < len(self.tokens):
                    print(f"DEBUG: Consumed end. at pos {p}")
                    p += 1
                return block, p
            print(f"DEBUG: Expected 'end.' or EOF at pos {p}, got {self.tokens[p] if p < len(self.tokens) else 'EOF'}")
            return None, p
        return self.memoize("program", pos, _program)

    def block(self, pos: int) -> Tuple[Optional[BlockNode], int]:
        def _block(p: int) -> Tuple[Optional[BlockNode], int]:
            print(f"DEBUG: Entering block at pos {p}")
            variables = []
            procedures = []
            if p < len(self.tokens) and self.tokens[p] == ("var", "kw"):
                print(f"DEBUG: Found 'var' at pos {p}")
                p += 1
                if p >= len(self.tokens) or self.tokens[p][1] != "id":
                    raise SyntaxError(f"Expected identifier after 'var' but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}")
                variables.append(self.tokens[p][0])
                print(f"DEBUG: Processing variable: '{variables[-1]}'")
                p += 1
                while p < len(self.tokens) and self.tokens[p] == (",", "comma"):
                    print(f"DEBUG: Consumed comma at pos {p}")
                    p += 1
                    if p >= len(self.tokens) or self.tokens[p][1] != "id" or self.tokens[p][0] in (";", ",", "end.", "end"):
                        raise SyntaxError(f"Expected identifier after comma but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}")
                    variables.append(self.tokens[p][0])
                    print(f"DEBUG: Processing variable: '{variables[-1]}'")
                    p += 1
                if p >= len(self.tokens) or self.tokens[p] != (";", "semi"):
                    raise SyntaxError(f"Expected semicolon but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}")
                print(f"DEBUG: Consumed semicolon at pos {p}")
                p += 1
            while p < len(self.tokens) and self.tokens[p] == ("procedure", "kw"):
                print(f"DEBUG: Found 'procedure' at pos {p}")
                p += 1
                if p >= len(self.tokens) or self.tokens[p][1] != "id":
                    raise SyntaxError(f"Expected identifier after 'procedure' but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}")
                proc_name = self.tokens[p][0]
                print(f"DEBUG: Processing procedure: '{proc_name}'")
                p += 1
                if p >= len(self.tokens) or self.tokens[p] != (";", "semi"):
                    raise SyntaxError(f"Expected semicolon after procedure name")
                print(f"DEBUG: Consumed semicolon at pos {p}")
                p += 1
                proc_body, p = self.block(p)
                if proc_body is None:
                    print(f"DEBUG: Failed to parse procedure body at pos {p}")
                    return None, p
                procedures.append((proc_name, proc_body))
                if p >= len(self.tokens) or self.tokens[p] != (";", "semi"):
                    raise SyntaxError(f"Expected semicolon after procedure body")
                print(f"DEBUG: Consumed semicolon after procedure at pos {p}")
                p += 1
            print(f"DEBUG: Parsing statement at pos {p}")
            statement, p = self.statement(p)
            if statement is None:
                print(f"DEBUG: Failed to parse statement at pos {p}")
                return None, p
            print(f"DEBUG: Block parsed successfully, returning at pos {p}")
            return BlockNode(variables, procedures, statement), p
        return self.memoize("block", pos, _block)

    def statement(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _statement(p: int) -> Tuple[Optional[ASTNode], int]:
            print(f"DEBUG: Entering statement at pos {p}")
            if p >= len(self.tokens):
                print(f"DEBUG: End of tokens reached at pos {p}")
                return None, p
            token, kind = self.tokens[p]
            if kind == "id":
                var_name = token
                p += 1
                if p >= len(self.tokens) or self.tokens[p] != (":=", "asgn"):
                    print(f"DEBUG: Expected ':=' after id at pos {p}")
                    return None, p
                p += 1
                expr, p = self.expression(p)
                if expr is None:
                    print(f"DEBUG: Failed to parse expression at pos {p}")
                    return None, p
                print(f"DEBUG: Parsed assignment at pos {p}")
                return AssignNode(var_name, expr), p
            elif token == "call" and kind == "kw":
                p += 1
                if p >= len(self.tokens) or self.tokens[p][1] != "id":
                    print(f"DEBUG: Expected id after 'call' at pos {p}")
                    return None, p
                proc_name = self.tokens[p][0]
                p += 1
                print(f"DEBUG: Parsed call at pos {p}")
                return CallNode(proc_name), p
            elif token == "?" and kind == "kw":
                p += 1
                if p >= len(self.tokens) or self.tokens[p][1] != "id":
                    print(f"DEBUG: Expected id after '?' at pos {p}")
                    return None, p
                var_name = self.tokens[p][0]
                p += 1
                print(f"DEBUG: Parsed read at pos {p}")
                return ReadNode(var_name), p
            elif token == "!" and kind == "kw":
                p += 1
                expr, p = self.expression(p)
                if expr is None:
                    print(f"DEBUG: Failed to parse expression after '!' at pos {p}")
                    return None, p
                print(f"DEBUG: Parsed write at pos {p}")
                return WriteNode(expr), p
            elif token == "begin" and kind == "kw":
                p += 1
                statements = []
                stmt, p = self.statement(p)
                if stmt is None:
                    print(f"DEBUG: Failed to parse first statement in begin at pos {p}")
                    return None, p
                statements.append(stmt)
                while p < len(self.tokens) and self.tokens[p] == (";", "semi"):
                    print(f"DEBUG: Consumed semicolon in begin at pos {p}")
                    p += 1
                    stmt, p = self.statement(p)
                    if stmt is None:
                        print(f"DEBUG: Failed to parse statement after semicolon at pos {p}")
                        break
                    statements.append(stmt)
                if p >= len(self.tokens) or self.tokens[p][0] not in ("end", "end."):
                    print(f"DEBUG: Expected 'end' or 'end.' at pos {p}, got {self.tokens[p] if p < len(self.tokens) else 'EOF'}")
                    return None, p
                print(f"DEBUG: Consumed end at pos {p}")
                p += 1
                print(f"DEBUG: Parsed compound statement at pos {p}")
                return CompoundNode(statements), p
            elif token == "if" and kind == "kw":
                p += 1
                cond, p = self.condition(p)
                if cond is None:
                    print(f"DEBUG: Failed to parse condition at pos {p}")
                    return None, p
                if p >= len(self.tokens) or self.tokens[p] != ("then", "kw"):
                    print(f"DEBUG: Expected 'then' at pos {p}")
                    return None, p
                p += 1
                stmt, p = self.statement(p)
                if stmt is None:
                    print(f"DEBUG: Failed to parse statement after then at pos {p}")
                    return None, p
                print(f"DEBUG: Parsed if statement at pos {p}")
                return IfNode(cond, stmt), p
            elif token == "while" and kind == "kw":
                p += 1
                cond, p = self.condition(p)
                if cond is None:
                    print(f"DEBUG: Failed to parse condition at pos {p}")
                    return None, p
                if p >= len(self.tokens) or self.tokens[p] != ("do", "kw"):
                    print(f"DEBUG: Expected 'do' at pos {p}")
                    return None, p
                p += 1
                stmt, p = self.statement(p)
                if stmt is None:
                    print(f"DEBUG: Failed to parse statement after do at pos {p}")
                    return None, p
                print(f"DEBUG: Parsed while statement at pos {p}")
                return WhileNode(cond, stmt), p
            print(f"DEBUG: No valid statement at pos {p}, token: {token}")
            return None, p
        return self.memoize("statement", pos, _statement)

    def condition(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _condition(p: int) -> Tuple[Optional[ASTNode], int]:
            print(f"DEBUG: Entering condition at pos {p}")
            left, p = self.expression(p)
            if left is None:
                print(f"DEBUG: Failed to parse left expression at pos {p}")
                return None, p
            if p >= len(self.tokens) or self.tokens[p][0] not in ("=", "<", ">", "<=", ">="):
                print(f"DEBUG: Expected comparison operator at pos {p}")
                return None, p
            op = self.tokens[p][0]
            p += 1
            right, p = self.expression(p)
            if right is None:
                print(f"DEBUG: Failed to parse right expression at pos {p}")
                return None, p
            print(f"DEBUG: Parsed condition at pos {p}")
            return OperationNode(op, left, right), p
        return self.memoize("condition", pos, _condition)

    def expression(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _expression(p: int) -> Tuple[Optional[ASTNode], int]:
            print(f"DEBUG: Entering expression at pos {p}")
            left, p = self.term(p)
            if left is None:
                print(f"DEBUG: Failed to parse term at pos {p}")
                return None, p
            while p < len(self.tokens) and self.tokens[p][0] in ("+", "-"):
                op = self.tokens[p][0]
                p += 1
                right, p = self.term(p)
                if right is None:
                    print(f"DEBUG: Failed to parse right term at pos {p}")
                    return None, p
                left = OperationNode(op, left, right)
            print(f"DEBUG: Parsed expression at pos {p}")
            return left, p
        return self.memoize("expression", pos, _expression)

    def term(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _term(p: int) -> Tuple[Optional[ASTNode], int]:
            print(f"DEBUG: Entering term at pos {p}")
            left, p = self.factor(p)
            if left is None:
                print(f"DEBUG: Failed to parse factor at pos {p}")
                return None, p
            while p < len(self.tokens) and self.tokens[p][0] in ("*", "/"):
                op = self.tokens[p][0]
                p += 1
                right, p = self.factor(p)
                if right is None:
                    print(f"DEBUG: Failed to parse right factor at pos {p}")
                    return None, p
                left = OperationNode(op, left, right)
            print(f"DEBUG: Parsed term at pos {p}")
            return left, p
        return self.memoize("term", pos, _term)

    def factor(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _factor(p: int) -> Tuple[Optional[ASTNode], int]:
            print(f"DEBUG: Entering factor at pos {p}")
            if p >= len(self.tokens):
                print(f"DEBUG: End of tokens reached at pos {p}")
                return None, p
            token, kind = self.tokens[p]
            if kind == "id":
                p += 1
                print(f"DEBUG: Parsed variable at pos {p}")
                return VariableNode(token), p
            elif kind == "num":
                p += 1
                print(f"DEBUG: Parsed number at pos {p}")
                return NumberNode(int(token)), p
            elif token == "(" and kind == "op":
                p += 1
                expr, p = self.expression(p)
                if expr is None or p >= len(self.tokens) or self.tokens[p] != (")", "op"):
                    print(f"DEBUG: Failed to parse parenthesized expression at pos {p}")
                    return None, p
                p += 1
                print(f"DEBUG: Parsed parenthesized expression at pos {p}")
                return expr, p
            print(f"DEBUG: No valid factor at pos {p}, token: {token}")
            return None, p
        return self.memoize("factor", pos, _factor)


class ASTVisitor(ABC):
    @abstractmethod
    def visit_block(self, node: BlockNode): pass
    @abstractmethod
    def visit_assign(self, node: AssignNode): pass
    @abstractmethod
    def visit_call(self, node: CallNode): pass
    @abstractmethod
    def visit_compound(self, node: CompoundNode): pass
    @abstractmethod
    def visit_if(self, node: IfNode): pass
    @abstractmethod
    def visit_while(self, node: WhileNode): pass
    @abstractmethod
    def visit_read(self, node: ReadNode): pass
    @abstractmethod
    def visit_write(self, node: WriteNode): pass
    @abstractmethod
    def visit_odd(self, node: OddNode): pass
    @abstractmethod
    def visit_operation(self, node: OperationNode): pass
    @abstractmethod
    def visit_number(self, node: NumberNode): pass
    @abstractmethod
    def visit_variable(self, node: VariableNode): pass



class CompilerContext:
    def __init__(self):
        self.scopes = [{}]
        self.current_scope_level = 0
        self.generated_code = []
        self.indent_level = 0
        self.temp_var_counter = 0
        self.current_procedure = None
        self.procedures = {}

    def enter_scope(self):
        self.scopes.append({})
        self.current_scope_level += 1
        self.indent_level += 1

    def exit_scope(self):
        if self.current_scope_level > 0:
            self.scopes.pop()
            self.current_scope_level -= 1
            self.indent_level -= 1

    def add_variable(self, name: str):
        self.scopes[-1][name] = True

    def variable_exists(self, name: str) -> bool:
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False

    def generate_temp_var(self) -> str:
        temp_var = f"_temp{self.temp_var_counter}"
        self.temp_var_counter += 1
        return temp_var

    def add_code(self, code: str):
        self.generated_code.append("\t" * self.indent_level + code)

    def get_code(self) -> str:
        return "\n".join(self.generated_code)

    def register_procedure(self, name: str, node: ASTNode):
        self.procedures[name] = node


class CCompiler(ASTVisitor):
    def __init__(self):
        self.code = []

    def compile(self, node: BlockNode) -> str:
        self.code = ['#include <stdio.h>\n']
        node.accept(self)
        return "\n".join(self.code)

    def visit_block(self, node: BlockNode):
        for var in node.variables:
            self.code.append(f"int {var};")
        self.code.append("int main() {")
        if node.statement: node.statement.accept(self)
        self.code.append("    return 0;")
        self.code.append("}")

    def visit_assign(self, node: AssignNode):
        expr = node.expression.accept(self)
        self.code.append(f"    {node.var_name} = {expr};")

    def visit_call(self, node: CallNode):
        self.code.append(f"    {node.proc_name}();")

    def visit_compound(self, node: CompoundNode):
        for s in node.statements: s.accept(self)

    def visit_if(self, node: IfNode):
        cond = node.condition.accept(self)
        self.code.append(f"    if ({cond}) {{")
        node.statement.accept(self)
        self.code.append("    }")

    def visit_while(self, node: WhileNode):
        cond = node.condition.accept(self)
        self.code.append(f"    while ({cond}) {{")
        node.statement.accept(self)
        self.code.append("    }")

    def visit_read(self, node: ReadNode):
        self.code.append(f"    scanf(\"%d\", &{node.var_name});")

    def visit_write(self, node: WriteNode):
        expr = node.expression.accept(self)
        self.code.append(f"    printf(\"%d\\n\", {expr});")

    def visit_odd(self, node: OddNode):
        expr = node.expression.accept(self)
        return f"({expr} % 2 == 1)"

    def visit_operation(self, node: OperationNode):
        l = node.left.accept(self)
        r = node.right.accept(self)
        return f"({l} {node.operator} {r})"

    def visit_number(self, node: NumberNode): return str(node.value)

    def visit_variable(self, node: VariableNode): return node.name


class TACCompiler(ASTVisitor):
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def compile(self, node: BlockNode) -> str:
        node.accept(self)
        return "\n".join(self.code)

    def visit_block(self, node: BlockNode):
        if node.statement: node.statement.accept(self)

    def visit_assign(self, node: AssignNode):
        val = node.expression.accept(self)
        self.code.append(f"{node.var_name} = {val}")

    def visit_call(self, node: CallNode):
        self.code.append(f"call {node.proc_name}")

    def visit_compound(self, node: CompoundNode):
        for s in node.statements: s.accept(self)

    def visit_if(self, node: IfNode):
        cond = node.condition.accept(self)
        L_end = self.new_label()
        self.code.append(f"ifz {cond} goto {L_end}")
        node.statement.accept(self)
        self.code.append(f"{L_end}:")

    def visit_while(self, node: WhileNode):
        L_start = self.new_label()
        L_end = self.new_label()
        self.code.append(f"{L_start}:")
        cond = node.condition.accept(self)
        self.code.append(f"ifz {cond} goto {L_end}")
        node.statement.accept(self)
        self.code.append(f"goto {L_start}")
        self.code.append(f"{L_end}:")

    def visit_read(self, node: ReadNode):
        self.code.append(f"read {node.var_name}")

    def visit_write(self, node: WriteNode):
        val = node.expression.accept(self)
        self.code.append(f"print {val}")

    def visit_odd(self, node: OddNode):
        val = node.expression.accept(self)
        t = self.new_temp()
        self.code.append(f"{t} = {val} % 2")
        return t

    def visit_operation(self, node: OperationNode):
        l = node.left.accept(self)
        r = node.right.accept(self)
        t = self.new_temp()
        self.code.append(f"{t} = {l} {node.operator} {r}")
        return t

    def visit_number(self, node: NumberNode):
        t = self.new_temp()
        self.code.append(f"{t} = {node.value}")
        return t

    def visit_variable(self, node: VariableNode): return node.name


class PL0Compiler:
    @staticmethod
    def compile_file(input_filename: str, output_filename: str = None):
        try:
            with open(input_filename, 'r') as f:
                code = f.read()
        except IOError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        base, _ = os.path.splitext(input_filename)
        token_file = base + ".tokens.json"
        ast_file   = base + ".ast.json"
        tac_file   = base + ".tac"
        output_filename = output_filename or (base + ".c")

        # Lexing
        lexer = Lexer(code)
        with open(token_file, "w") as f: json.dump(lexer.tokens, f, indent=2)

        # Parsing
        parser = PackratParser(lexer.tokens)
        ast = parser.parse()
        with open(ast_file, "w") as f: json.dump(ast.to_dict(), f, indent=2)

        # TAC
        tac_comp = TACCompiler()
        tac_code = tac_comp.compile(ast)
        with open(tac_file, "w") as f: f.write(tac_code)

        # C
        c_comp = CCompiler()
        c_code = c_comp.compile(ast)
        with open(output_filename, "w") as f: f.write(c_code)

        print(f"Compiled {input_filename} → {token_file}, {ast_file}, {tac_file}, {output_filename}")


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: compiler.py <input_filename> [output_filename]", file=sys.stderr)
        sys.exit(1)
    input_filename = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) == 3 else None
    PL0Compiler.compile_file(input_filename, output_filename)


if __name__ == "__main__":
    main()


