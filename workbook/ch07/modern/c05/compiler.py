#!/usr/bin/env python3

import sys
import os
import importlib.util
from typing import Tuple, Optional, List, Callable, Any, Dict
from abc import ABC, abstractmethod
from enum import Enum


class MessageLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class CompilerMessage:
    def __init__(self, level: MessageLevel, message: str, position: Optional[int] = None, 
                 source: Optional[str] = None, context: Optional[Dict] = None):
        self.level = level
        self.message = message
        self.position = position
        self.source = source
        self.context = context or {}

    def __str__(self):
        pos_info = f" at position {self.position}" if self.position is not None else ""
        source_info = f" in {self.source}" if self.source else ""
        return f"[{self.level.value}]{source_info}{pos_info}: {self.message}"


class MessageCollector:
    def __init__(self):
        self.messages: List[CompilerMessage] = []
        self.debug_enabled = False

    def add(self, level: MessageLevel, message: str, position: Optional[int] = None, 
            source: Optional[str] = None, context: Optional[Dict] = None):
        msg = CompilerMessage(level, message, position, source, context)
        self.messages.append(msg)
        if self.debug_enabled or level != MessageLevel.DEBUG:
            print(str(msg))

    def debug(self, message: str, position: Optional[int] = None, source: Optional[str] = None, context: Optional[Dict] = None):
        self.add(MessageLevel.DEBUG, message, position, source, context)

    def info(self, message: str, position: Optional[int] = None, source: Optional[str] = None, context: Optional[Dict] = None):
        self.add(MessageLevel.INFO, message, position, source, context)

    def warning(self, message: str, position: Optional[int] = None, source: Optional[str] = None, context: Optional[Dict] = None):
        self.add(MessageLevel.WARNING, message, position, source, context)

    def error(self, message: str, position: Optional[int] = None, source: Optional[str] = None, context: Optional[Dict] = None):
        self.add(MessageLevel.ERROR, message, position, source, context)

    def has_errors(self) -> bool:
        return any(msg.level == MessageLevel.ERROR for msg in self.messages)

    def get_messages(self, level: Optional[MessageLevel] = None) -> List[CompilerMessage]:
        if level is None:
            return self.messages[:]
        return [msg for msg in self.messages if msg.level == level]

    def enable_debug(self, enabled: bool = True):
        self.debug_enabled = enabled

    def clear(self):
        self.messages.clear()


class Lexer:
    def __init__(self, code: str, messages: MessageCollector):
        self.code = code.strip()
        self.tokens = []
        self.pos = 0
        self.messages = messages
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
                self.messages.debug(f"Lexer produced token: 'end.' (kw)", self.pos, "Lexer")
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
                self.messages.error(f"Unexpected character: '{self.code[self.pos]}'", self.pos, "Lexer")
                raise SyntaxError(f"Unexpected character: '{self.code[self.pos]}'")
            self.tokens.append((token, kind))
            self.messages.debug(f"Lexer produced token: '{token}' ({kind})", self.pos, "Lexer")

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
    def __init__(self):
        self.metadata = {}
        self.source_position = None

    @abstractmethod
    def accept(self, visitor):
        pass

    def set_metadata(self, key: str, value: Any):
        self.metadata[key] = value

    def get_metadata(self, key: str, default=None):
        return self.metadata.get(key, default)


class BlockNode(ASTNode):
    def __init__(self, variables: List[str], procedures: List[Tuple[str, ASTNode]], statement: ASTNode):
        super().__init__()
        self.variables = variables
        self.procedures = procedures
        self.statement = statement
    def accept(self, visitor):
        return visitor.visit_block(self)


class AssignNode(ASTNode):
    def __init__(self, var_name: str, expression: ASTNode):
        super().__init__()
        self.var_name = var_name
        self.expression = expression
    def accept(self, visitor):
        return visitor.visit_assign(self)


class CallNode(ASTNode):
    def __init__(self, proc_name: str):
        super().__init__()
        self.proc_name = proc_name
    def accept(self, visitor):
        return visitor.visit_call(self)


class ReadNode(ASTNode):
    def __init__(self, var_name: str):
        super().__init__()
        self.var_name = var_name
    def accept(self, visitor):
        return visitor.visit_read(self)


class WriteNode(ASTNode):
    def __init__(self, expression: ASTNode):
        super().__init__()
        self.expression = expression
    def accept(self, visitor):
        return visitor.visit_write(self)


class CompoundNode(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        super().__init__()
        self.statements = statements
    def accept(self, visitor):
        return visitor.visit_compound(self)


class NestedBlockNode(ASTNode):
    def __init__(self, variables: List[str], statements: List[ASTNode]):
        super().__init__()
        self.variables = variables
        self.statements = statements
    def accept(self, visitor):
        return visitor.visit_nested_block(self)


class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_statement: ASTNode):
        super().__init__()
        self.condition = condition
        self.then_statement = then_statement
    def accept(self, visitor):
        return visitor.visit_if(self)


class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, body: ASTNode):
        super().__init__()
        self.condition = condition
        self.body = body
    def accept(self, visitor):
        return visitor.visit_while(self)


class OperationNode(ASTNode):
    def __init__(self, operator: str, left: ASTNode, right: ASTNode):
        super().__init__()
        self.operator = operator
        self.left = left
        self.right = right
    def accept(self, visitor):
        return visitor.visit_operation(self)


class VariableNode(ASTNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    def accept(self, visitor):
        return visitor.visit_variable(self)


class NumberNode(ASTNode):
    def __init__(self, value: int):
        super().__init__()
        self.value = value
    def accept(self, visitor):
        return visitor.visit_number(self)


class PackratParser:
    def __init__(self, tokens: List[Tuple[str, str]], messages: MessageCollector):
        self.tokens = tokens
        self.cache = {}
        self.messages = messages

    def parse(self):
        result, pos = self.program(0)
        if result is None:
            self.messages.error("Failed to parse program", pos, "Parser")
            raise SyntaxError("Failed to parse program")
        if pos != len(self.tokens):
            self.messages.error("Incomplete parse - tokens remaining", pos, "Parser")
            raise SyntaxError("Incomplete parse")
        return result

    def memoize(self, rule: str, pos: int, func: Callable[[int], Tuple[Any, int]]) -> Tuple[Any, int]:
        key = (rule, pos)
        if key in self.cache:
            self.messages.debug(f"Cache hit for {rule} at pos {pos}", pos, "Parser")
            return self.cache[key]
        result = func(pos)
        self.cache[key] = result
        return result

    def program(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _program(p: int) -> Tuple[Optional[ASTNode], int]:
            self.messages.debug(f"Entering program at pos {p}", p, "Parser")
            block, p = self.block(p)
            if block is None:
                self.messages.error(f"Failed to parse block", p, "Parser")
                return None, p
            if p == len(self.tokens) or (p < len(self.tokens) and self.tokens[p] == ("end.", "kw")):
                if p < len(self.tokens):
                    self.messages.debug(f"Consumed end.", p, "Parser")
                    p += 1
                return block, p
            self.messages.error(f"Expected 'end.' or EOF, got {self.tokens[p] if p < len(self.tokens) else 'EOF'}", p, "Parser")
            return None, p
        return self.memoize("program", pos, _program)

    def block(self, pos: int) -> Tuple[Optional[BlockNode], int]:
        def _block(p: int) -> Tuple[Optional[BlockNode], int]:
            self.messages.debug(f"Entering block", p, "Parser")
            variables = []
            procedures = []
            if p < len(self.tokens) and self.tokens[p] == ("var", "kw"):
                self.messages.debug(f"Found 'var'", p, "Parser")
                p += 1
                if p >= len(self.tokens) or self.tokens[p][1] != "id":
                    self.messages.error(f"Expected identifier after 'var' but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}", p, "Parser")
                    raise SyntaxError(f"Expected identifier after 'var'")
                variables.append(self.tokens[p][0])
                self.messages.debug(f"Processing variable: '{variables[-1]}'", p, "Parser")
                p += 1
                while p < len(self.tokens) and self.tokens[p] == (",", "comma"):
                    self.messages.debug(f"Consumed comma", p, "Parser")
                    p += 1
                    if p >= len(self.tokens) or self.tokens[p][1] != "id" or self.tokens[p][0] in (";", ",", "end.", "end"):
                        self.messages.error(f"Expected identifier after comma but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}", p, "Parser")
                        raise SyntaxError(f"Expected identifier after comma")
                    variables.append(self.tokens[p][0])
                    self.messages.debug(f"Processing variable: '{variables[-1]}'", p, "Parser")
                    p += 1
                if p >= len(self.tokens) or self.tokens[p] != (";", "semi"):
                    self.messages.error(f"Expected semicolon but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}", p, "Parser")
                    raise SyntaxError(f"Expected semicolon")
                self.messages.debug(f"Consumed semicolon", p, "Parser")
                p += 1
            while p < len(self.tokens) and self.tokens[p] == ("procedure", "kw"):
                self.messages.debug(f"Found 'procedure'", p, "Parser")
                p += 1
                if p >= len(self.tokens) or self.tokens[p][1] != "id":
                    self.messages.error(f"Expected identifier after 'procedure' but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}", p, "Parser")
                    raise SyntaxError(f"Expected identifier after 'procedure'")
                proc_name = self.tokens[p][0]
                self.messages.debug(f"Processing procedure: '{proc_name}'", p, "Parser")
                p += 1
                if p >= len(self.tokens) or self.tokens[p] != (";", "semi"):
                    self.messages.error(f"Expected semicolon after procedure name", p, "Parser")
                    raise SyntaxError(f"Expected semicolon after procedure name")
                self.messages.debug(f"Consumed semicolon", p, "Parser")
                p += 1
                proc_body, p = self.block(p)
                if proc_body is None:
                    self.messages.error(f"Failed to parse procedure body", p, "Parser")
                    return None, p
                procedures.append((proc_name, proc_body))
                if p >= len(self.tokens) or self.tokens[p] != (";", "semi"):
                    self.messages.error(f"Expected semicolon after procedure body", p, "Parser")
                    raise SyntaxError(f"Expected semicolon after procedure body")
                self.messages.debug(f"Consumed semicolon after procedure", p, "Parser")
                p += 1
            self.messages.debug(f"Parsing statement", p, "Parser")
            statement, p = self.statement(p)
            if statement is None:
                self.messages.error(f"Failed to parse statement", p, "Parser")
                return None, p
            self.messages.debug(f"Block parsed successfully", p, "Parser")
            return BlockNode(variables, procedures, statement), p
        return self.memoize("block", pos, _block)

    def statement(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _statement(p: int) -> Tuple[Optional[ASTNode], int]:
            self.messages.debug(f"Entering statement", p, "Parser")
            if p >= len(self.tokens):
                self.messages.debug(f"End of tokens reached", p, "Parser")
                return None, p
            token, kind = self.tokens[p]
            if kind == "id":
                var_name = token
                p += 1
                if p >= len(self.tokens) or self.tokens[p] != (":=", "asgn"):
                    self.messages.error(f"Expected ':=' after id", p, "Parser")
                    return None, p
                p += 1
                expr, p = self.expression(p)
                if expr is None:
                    self.messages.error(f"Failed to parse expression", p, "Parser")
                    return None, p
                self.messages.debug(f"Parsed assignment", p, "Parser")
                return AssignNode(var_name, expr), p
            elif token == "call" and kind == "kw":
                p += 1
                if p >= len(self.tokens) or self.tokens[p][1] != "id":
                    self.messages.error(f"Expected id after 'call'", p, "Parser")
                    return None, p
                proc_name = self.tokens[p][0]
                p += 1
                self.messages.debug(f"Parsed call", p, "Parser")
                return CallNode(proc_name), p
            elif token == "?" and kind == "kw":
                p += 1
                if p >= len(self.tokens) or self.tokens[p][1] != "id":
                    self.messages.error(f"Expected id after '?'", p, "Parser")
                    return None, p
                var_name = self.tokens[p][0]
                p += 1
                self.messages.debug(f"Parsed read", p, "Parser")
                return ReadNode(var_name), p
            elif token == "!" and kind == "kw":
                p += 1
                expr, p = self.expression(p)
                if expr is None:
                    self.messages.error(f"Failed to parse expression after '!'", p, "Parser")
                    return None, p
                self.messages.debug(f"Parsed write", p, "Parser")
                return WriteNode(expr), p
            elif token == "begin" and kind == "kw":
                p += 1
                variables = []
                if p < len(self.tokens) and self.tokens[p] == ("var", "kw"):
                    self.messages.debug(f"Found 'var' in nested block", p, "Parser")
                    p += 1
                    if p >= len(self.tokens) or self.tokens[p][1] != "id":
                        self.messages.error(f"Expected identifier after 'var' but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}", p, "Parser")
                        raise SyntaxError(f"Expected identifier after 'var'")
                    variables.append(self.tokens[p][0])
                    self.messages.debug(f"Processing nested variable: '{variables[-1]}'", p, "Parser")
                    p += 1
                    while p < len(self.tokens) and self.tokens[p] == (",", "comma"):
                        self.messages.debug(f"Consumed comma in nested block", p, "Parser")
                        p += 1
                        if p >= len(self.tokens) or self.tokens[p][1] != "id" or self.tokens[p][0] in (";", ",", "end.", "end"):
                            self.messages.error(f"Expected identifier after comma but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}", p, "Parser")
                            raise SyntaxError(f"Expected identifier after comma")
                        variables.append(self.tokens[p][0])
                        self.messages.debug(f"Processing nested variable: '{variables[-1]}'", p, "Parser")
                        p += 1
                    if p >= len(self.tokens) or self.tokens[p] != (";", "semi"):
                        self.messages.error(f"Expected semicolon but got: {self.tokens[p] if p < len(self.tokens) else 'EOF'}", p, "Parser")
                        raise SyntaxError(f"Expected semicolon")
                    self.messages.debug(f"Consumed semicolon in nested block", p, "Parser")
                    p += 1
                
                statements = []
                stmt, p = self.statement(p)
                if stmt is None:
                    self.messages.error(f"Failed to parse first statement in begin", p, "Parser")
                    return None, p
                statements.append(stmt)
                while p < len(self.tokens) and self.tokens[p] == (";", "semi"):
                    self.messages.debug(f"Consumed semicolon in begin", p, "Parser")
                    p += 1
                    stmt, p = self.statement(p)
                    if stmt is None:
                        self.messages.debug(f"Failed to parse statement after semicolon", p, "Parser")
                        break
                    statements.append(stmt)
                if p >= len(self.tokens) or self.tokens[p][0] not in ("end", "end."):
                    self.messages.error(f"Expected 'end' or 'end.', got {self.tokens[p] if p < len(self.tokens) else 'EOF'}", p, "Parser")
                    return None, p
                self.messages.debug(f"Consumed end", p, "Parser")
                p += 1
                
                if variables:
                    self.messages.debug(f"Parsed nested block with variables", p, "Parser")
                    return NestedBlockNode(variables, statements), p
                else:
                    self.messages.debug(f"Parsed compound statement", p, "Parser")
                    return CompoundNode(statements), p
                    
            elif token == "if" and kind == "kw":
                p += 1
                cond, p = self.condition(p)
                if cond is None:
                    self.messages.error(f"Failed to parse condition", p, "Parser")
                    return None, p
                if p >= len(self.tokens) or self.tokens[p] != ("then", "kw"):
                    self.messages.error(f"Expected 'then'", p, "Parser")
                    return None, p
                p += 1
                stmt, p = self.statement(p)
                if stmt is None:
                    self.messages.error(f"Failed to parse statement after then", p, "Parser")
                    return None, p
                self.messages.debug(f"Parsed if statement", p, "Parser")
                return IfNode(cond, stmt), p
            elif token == "while" and kind == "kw":
                p += 1
                cond, p = self.condition(p)
                if cond is None:
                    self.messages.error(f"Failed to parse condition", p, "Parser")
                    return None, p
                if p >= len(self.tokens) or self.tokens[p] != ("do", "kw"):
                    self.messages.error(f"Expected 'do'", p, "Parser")
                    return None, p
                p += 1
                stmt, p = self.statement(p)
                if stmt is None:
                    self.messages.error(f"Failed to parse statement after do", p, "Parser")
                    return None, p
                self.messages.debug(f"Parsed while statement", p, "Parser")
                return WhileNode(cond, stmt), p
            self.messages.debug(f"No valid statement, token: {token}", p, "Parser")
            return None, p
        return self.memoize("statement", pos, _statement)

    def condition(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _condition(p: int) -> Tuple[Optional[ASTNode], int]:
            self.messages.debug(f"Entering condition", p, "Parser")
            left, p = self.expression(p)
            if left is None:
                self.messages.error(f"Failed to parse left expression", p, "Parser")
                return None, p
            if p >= len(self.tokens) or self.tokens[p][0] not in ("=", "<", ">", "<=", ">="):
                self.messages.error(f"Expected comparison operator", p, "Parser")
                return None, p
            op = self.tokens[p][0]
            p += 1
            right, p = self.expression(p)
            if right is None:
                self.messages.error(f"Failed to parse right expression", p, "Parser")
                return None, p
            self.messages.debug(f"Parsed condition", p, "Parser")
            return OperationNode(op, left, right), p
        return self.memoize("condition", pos, _condition)

    def expression(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _expression(p: int) -> Tuple[Optional[ASTNode], int]:
            self.messages.debug(f"Entering expression", p, "Parser")
            left, p = self.term(p)
            if left is None:
                self.messages.error(f"Failed to parse term", p, "Parser")
                return None, p
            while p < len(self.tokens) and self.tokens[p][0] in ("+", "-"):
                op = self.tokens[p][0]
                p += 1
                right, p = self.term(p)
                if right is None:
                    self.messages.error(f"Failed to parse right term", p, "Parser")
                    return None, p
                left = OperationNode(op, left, right)
            self.messages.debug(f"Parsed expression", p, "Parser")
            return left, p
        return self.memoize("expression", pos, _expression)

    def term(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _term(p: int) -> Tuple[Optional[ASTNode], int]:
            self.messages.debug(f"Entering term", p, "Parser")
            left, p = self.factor(p)
            if left is None:
                self.messages.error(f"Failed to parse factor", p, "Parser")
                return None, p
            while p < len(self.tokens) and self.tokens[p][0] in ("*", "/"):
                op = self.tokens[p][0]
                p += 1
                right, p = self.factor(p)
                if right is None:
                    self.messages.error(f"Failed to parse right factor", p, "Parser")
                    return None, p
                left = OperationNode(op, left, right)
            self.messages.debug(f"Parsed term", p, "Parser")
            return left, p
        return self.memoize("term", pos, _term)

    def factor(self, pos: int) -> Tuple[Optional[ASTNode], int]:
        def _factor(p: int) -> Tuple[Optional[ASTNode], int]:
            self.messages.debug(f"Entering factor", p, "Parser")
            if p >= len(self.tokens):
                self.messages.debug(f"End of tokens reached", p, "Parser")
                return None, p
            token, kind = self.tokens[p]
            if kind == "id":
                p += 1
                self.messages.debug(f"Parsed variable", p, "Parser")
                return VariableNode(token), p
            elif kind == "num":
                p += 1
                self.messages.debug(f"Parsed number", p, "Parser")
                return NumberNode(int(token)), p
            elif token == "(" and kind == "op":
                p += 1
                expr, p = self.expression(p)
                if expr is None or p >= len(self.tokens) or self.tokens[p] != (")", "op"):
                    self.messages.error(f"Failed to parse parenthesized expression", p, "Parser")
                    return None, p
                p += 1
                self.messages.debug(f"Parsed parenthesized expression", p, "Parser")
                return expr, p
            self.messages.debug(f"No valid factor, token: {token}", p, "Parser")
            return None, p
        return self.memoize("factor", pos, _factor)


class Visitor(ABC):
    @abstractmethod
    def visit_block(self, node: BlockNode): pass
    @abstractmethod
    def visit_assign(self, node: AssignNode): pass
    @abstractmethod
    def visit_call(self, node: CallNode): pass
    @abstractmethod
    def visit_read(self, node: ReadNode): pass
    @abstractmethod
    def visit_write(self, node: WriteNode): pass
    @abstractmethod
    def visit_compound(self, node: CompoundNode): pass
    @abstractmethod
    def visit_nested_block(self, node: NestedBlockNode): pass
    @abstractmethod
    def visit_if(self, node: IfNode): pass
    @abstractmethod
    def visit_while(self, node: WhileNode): pass
    @abstractmethod
    def visit_operation(self, node: OperationNode): pass
    @abstractmethod
    def visit_variable(self, node: VariableNode): pass
    @abstractmethod
    def visit_number(self, node: NumberNode): pass


class CompilerContext:
    def __init__(self, output_dir: str = None):
        self.scopes = [{}]
        self.current_scope_level = 0
        self.indent_level = 0
        self.temp_var_counter = 0
        self.current_procedure = None
        self.procedures = {}
        self.block_counter = 0
        self.plugin_results = {}
        self.generated_outputs = {}  # Track all generated outputs
        self.output_dir = output_dir or os.getcwd()
        self.source_filename = None
        self.base_name = None
        
        # Ensure output directory exists
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def set_source_info(self, source_filename: str):
        """Set source file information for plugins to use"""
        self.source_filename = source_filename
        self.base_name = os.path.splitext(os.path.basename(source_filename))[0]

    def get_output_path(self, filename: str) -> str:
        """Get full path for an output file"""
        return os.path.join(self.output_dir, filename)

    def register_output_file(self, plugin_name: str, filename: str, description: str = ""):
        """Register a file that was generated by a plugin"""
        if plugin_name not in self.generated_outputs:
            self.generated_outputs[plugin_name] = []
        self.generated_outputs[plugin_name].append({
            'filename': filename,
            'full_path': self.get_output_path(filename),
            'description': description
        })

    def get_generated_files(self, plugin_name: str = None) -> Dict:
        """Get list of generated files, optionally filtered by plugin"""
        if plugin_name:
            return self.generated_outputs.get(plugin_name, [])
        return self.generated_outputs

    def enter_scope(self):
        self.scopes.append({})
        self.current_scope_level += 1

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.current_scope_level -= 1

    def declare_variable(self, name: str, var_type: str = "int"):
        self.scopes[-1][name] = {"type": var_type, "level": self.current_scope_level}

    def lookup_variable(self, name: str):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def declare_procedure(self, name: str, block_node: ASTNode):
        self.procedures[name] = {"block": block_node, "level": self.current_scope_level}

    def lookup_procedure(self, name: str):
        return self.procedures.get(name)

    def get_temp_var(self) -> str:
        self.temp_var_counter += 1
        return f"temp_{self.temp_var_counter}"

    def get_unique_block_id(self) -> str:
        self.block_counter += 1
        return f"block_{self.block_counter}"

    def indent(self) -> str:
        return "    " * self.indent_level

    def increase_indent(self):
        self.indent_level += 1

    def decrease_indent(self):
        if self.indent_level > 0:
            self.indent_level -= 1


class SemanticAnalyzer(Visitor):
    def __init__(self, context: CompilerContext, messages: MessageCollector):
        self.context = context
        self.messages = messages

    def analyze(self, ast: ASTNode):
        """Run semantic analysis on the AST"""
        try:
            ast.accept(self)
            self.messages.info("Semantic analysis completed successfully")
        except Exception as e:
            self.messages.error(f"Semantic analysis failed: {str(e)}")
            raise

    def visit_block(self, node: BlockNode):
        self.context.enter_scope()
        
        # Declare variables
        for var_name in node.variables:
            if self.context.lookup_variable(var_name) and \
               self.context.lookup_variable(var_name)['level'] == self.context.current_scope_level:
                self.messages.error(f"Variable '{var_name}' already declared in current scope")
            else:
                self.context.declare_variable(var_name)
                self.messages.debug(f"Declared variable: {var_name}")

        # Declare procedures
        for proc_name, proc_block in node.procedures:
            if proc_name in self.context.procedures:
                self.messages.error(f"Procedure '{proc_name}' already declared")
            else:
                self.context.declare_procedure(proc_name, proc_block)
                self.messages.debug(f"Declared procedure: {proc_name}")

        # Analyze procedure bodies
        for proc_name, proc_block in node.procedures:
            old_proc = self.context.current_procedure
            self.context.current_procedure = proc_name
            proc_block.accept(self)
            self.context.current_procedure = old_proc

        # Analyze main statement
        node.statement.accept(self)
        self.context.exit_scope()

    def visit_assign(self, node: AssignNode):
        if not self.context.lookup_variable(node.var_name):
            self.messages.error(f"Undefined variable: {node.var_name}")
        node.expression.accept(self)

    def visit_call(self, node: CallNode):
        if not self.context.lookup_procedure(node.proc_name):
            self.messages.error(f"Undefined procedure: {node.proc_name}")

    def visit_read(self, node: ReadNode):
        if not self.context.lookup_variable(node.var_name):
            self.messages.error(f"Undefined variable: {node.var_name}")

    def visit_write(self, node: WriteNode):
        node.expression.accept(self)

    def visit_compound(self, node: CompoundNode):
        for stmt in node.statements:
            stmt.accept(self)

    def visit_nested_block(self, node: NestedBlockNode):
        self.context.enter_scope()
        
        # Declare nested variables
        for var_name in node.variables:
            if self.context.lookup_variable(var_name) and \
               self.context.lookup_variable(var_name)['level'] == self.context.current_scope_level:
                self.messages.error(f"Variable '{var_name}' already declared in current scope")
            else:
                self.context.declare_variable(var_name)
                self.messages.debug(f"Declared nested variable: {var_name}")
        
        # Analyze statements
        for stmt in node.statements:
            stmt.accept(self)
            
        self.context.exit_scope()

    def visit_if(self, node: IfNode):
        node.condition.accept(self)
        node.then_statement.accept(self)

    def visit_while(self, node: WhileNode):
        node.condition.accept(self)
        node.body.accept(self)

    def visit_operation(self, node: OperationNode):
        node.left.accept(self)
        node.right.accept(self)

    def visit_variable(self, node: VariableNode):
        if not self.context.lookup_variable(node.name):
            self.messages.error(f"Undefined variable: {node.name}")

    def visit_number(self, node: NumberNode):
        pass  # Numbers are always valid


class CodeGenerator(Visitor):
    def __init__(self, context: CompilerContext, messages: MessageCollector):
        self.context = context
        self.messages = messages
        self.code = []

    def generate(self, ast: ASTNode) -> str:
        """Generate code from AST"""
        self.code = []
        try:
            ast.accept(self)
            result = '\n'.join(self.code)
            self.messages.info("Code generation completed successfully")
            return result
        except Exception as e:
            self.messages.error(f"Code generation failed: {str(e)}")
            raise

    def emit(self, line: str):
        self.code.append(self.context.indent() + line)

    def visit_block(self, node: BlockNode):
        self.emit("# Block start")
        self.context.increase_indent()
        
        # Initialize variables
        for var_name in node.variables:
            self.emit(f"{var_name} = 0  # Variable declaration")
        
        # Generate procedure definitions
        for proc_name, proc_block in node.procedures:
            self.emit(f"def {proc_name}():")
            self.context.increase_indent()
            proc_block.accept(self)
            self.context.decrease_indent()
            self.emit("")
        
        # Generate main statement
        node.statement.accept(self)
        self.context.decrease_indent()

    def visit_assign(self, node: AssignNode):
        # Generate expression first
        expr_code = self._generate_expression(node.expression)
        self.emit(f"{node.var_name} = {expr_code}")

    def visit_call(self, node: CallNode):
        self.emit(f"{node.proc_name}()")

    def visit_read(self, node: ReadNode):
        self.emit(f"{node.var_name} = int(input('Enter value for {node.var_name}: '))")

    def visit_write(self, node: WriteNode):
        expr_code = self._generate_expression(node.expression)
        self.emit(f"print({expr_code})")

    def visit_compound(self, node: CompoundNode):
        for stmt in node.statements:
            stmt.accept(self)

    def visit_nested_block(self, node: NestedBlockNode):
        self.emit("# Nested block start")
        self.context.increase_indent()
        
        # Initialize nested variables
        for var_name in node.variables:
            self.emit(f"{var_name} = 0  # Nested variable declaration")
        
        # Generate statements
        for stmt in node.statements:
            stmt.accept(self)
            
        self.context.decrease_indent()
        self.emit("# Nested block end")

    def visit_if(self, node: IfNode):
        condition_code = self._generate_expression(node.condition)
        self.emit(f"if {condition_code}:")
        self.context.increase_indent()
        node.then_statement.accept(self)
        self.context.decrease_indent()

    def visit_while(self, node: WhileNode):
        condition_code = self._generate_expression(node.condition)
        self.emit(f"while {condition_code}:")
        self.context.increase_indent()
        node.body.accept(self)
        self.context.decrease_indent()

    def visit_operation(self, node: OperationNode):
        # This should not be called directly; use _generate_expression instead
        pass

    def visit_variable(self, node: VariableNode):
        # This should not be called directly; use _generate_expression instead
        pass

    def visit_number(self, node: NumberNode):
        # This should not be called directly; use _generate_expression instead
        pass

    def _generate_expression(self, node: ASTNode) -> str:
        """Generate expression code as string"""
        if isinstance(node, NumberNode):
            return str(node.value)
        elif isinstance(node, VariableNode):
            return node.name
        elif isinstance(node, OperationNode):
            left = self._generate_expression(node.left)
            right = self._generate_expression(node.right)
            if node.operator == "=":
                return f"({left} == {right})"
            else:
                return f"({left} {node.operator} {right})"
        else:
            raise ValueError(f"Unknown expression node type: {type(node)}")


class Plugin(ABC):
    """Base class for compiler plugins"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self, ast: ASTNode, context: CompilerContext, messages: MessageCollector) -> Any:
        """Execute the plugin and return results"""
        pass
    
    def get_dependencies(self) -> List[str]:
        """Return list of plugin names this plugin depends on"""
        return []


class PythonCodeGenPlugin(Plugin):
    """Plugin to generate Python code"""
    
    def __init__(self):
        super().__init__("python_codegen")
    
    def execute(self, ast: ASTNode, context: CompilerContext, messages: MessageCollector) -> str:
        generator = CodeGenerator(context, messages)
        python_code = generator.generate(ast)
        
        # Generate output filename
        if context.base_name:
            filename = f"{context.base_name}.py"
        else:
            filename = "output.py"
        
        # Write to file
        output_path = context.get_output_path(filename)
        with open(output_path, 'w') as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("# Generated by PL/0 Compiler\n\n")
            f.write(python_code)
        
        context.register_output_file(self.name, filename, "Generated Python code")
        messages.info(f"Python code generated: {output_path}")
        
        return python_code


class ASTVisualizerPlugin(Plugin):
    """Plugin to generate AST visualization"""
    
    def __init__(self):
        super().__init__("ast_visualizer")
    
    def execute(self, ast: ASTNode, context: CompilerContext, messages: MessageCollector) -> str:
        dot_content = self._generate_dot(ast)
        
        # Generate output filename
        if context.base_name:
            filename = f"{context.base_name}_ast.dot"
        else:
            filename = "ast.dot"
        
        # Write to file
        output_path = context.get_output_path(filename)
        with open(output_path, 'w') as f:
            f.write(dot_content)
        
        context.register_output_file(self.name, filename, "AST visualization in DOT format")
        messages.info(f"AST visualization generated: {output_path}")
        
        return dot_content
    
    def _generate_dot(self, ast: ASTNode) -> str:
        """Generate DOT format visualization of AST"""
        lines = ["digraph AST {", "  rankdir=TB;", "  node [shape=box];"]
        self.node_counter = 0
        self._visit_node(ast, lines, None)
        lines.append("}")
        return '\n'.join(lines)
    
    def _visit_node(self, node: ASTNode, lines: List[str], parent_id: str) -> str:
        self.node_counter += 1
        node_id = f"node{self.node_counter}"
        
        # Generate node label
        if isinstance(node, BlockNode):
            label = f"Block\\nvars: {', '.join(node.variables) if node.variables else 'none'}\\nprocs: {len(node.procedures)}"
        elif isinstance(node, AssignNode):
            label = f"Assign\\n{node.var_name} :="
        elif isinstance(node, CallNode):
            label = f"Call\\n{node.proc_name}"
        elif isinstance(node, ReadNode):
            label = f"Read\\n{node.var_name}"
        elif isinstance(node, WriteNode):
            label = "Write"
        elif isinstance(node, CompoundNode):
            label = f"Compound\\n{len(node.statements)} statements"
        elif isinstance(node, NestedBlockNode):
            label = f"NestedBlock\\nvars: {', '.join(node.variables) if node.variables else 'none'}"
        elif isinstance(node, IfNode):
            label = "If"
        elif isinstance(node, WhileNode):
            label = "While"
        elif isinstance(node, OperationNode):
            label = f"Op\\n{node.operator}"
        elif isinstance(node, VariableNode):
            label = f"Var\\n{node.name}"
        elif isinstance(node, NumberNode):
            label = f"Num\\n{node.value}"
        else:
            label = type(node).__name__
        
        lines.append(f'  {node_id} [label="{label}"];')
        
        if parent_id:
            lines.append(f'  {parent_id} -> {node_id};')
        
        # Visit children
        if isinstance(node, BlockNode):
            for proc_name, proc_block in node.procedures:
                proc_id = self._visit_node(proc_block, lines, node_id)
                lines.append(f'  {node_id} -> {proc_id} [label="proc: {proc_name}"];')
            self._visit_node(node.statement, lines, node_id)
        elif isinstance(node, AssignNode):
            self._visit_node(node.expression, lines, node_id)
        elif isinstance(node, WriteNode):
            self._visit_node(node.expression, lines, node_id)
        elif isinstance(node, CompoundNode):
            for stmt in node.statements:
                self._visit_node(stmt, lines, node_id)
        elif isinstance(node, NestedBlockNode):
            for stmt in node.statements:
                self._visit_node(stmt, lines, node_id)
        elif isinstance(node, IfNode):
            self._visit_node(node.condition, lines, node_id)
            self._visit_node(node.then_statement, lines, node_id)
        elif isinstance(node, WhileNode):
            self._visit_node(node.condition, lines, node_id)
            self._visit_node(node.body, lines, node_id)
        elif isinstance(node, OperationNode):
            self._visit_node(node.left, lines, node_id)
            self._visit_node(node.right, lines, node_id)
        
        return node_id


class PluginManager:
    """Manages and executes compiler plugins"""
    
    def __init__(self):
        self.plugins = {}
        self.plugin_order = []
    
    def register_plugin(self, plugin: Plugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        self._update_execution_order()
    
    def _update_execution_order(self):
        """Update plugin execution order based on dependencies"""
        # Simple topological sort for plugin dependencies
        visited = set()
        temp_visited = set()
        self.plugin_order = []
        
        def visit(plugin_name):
            if plugin_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving plugin: {plugin_name}")
            if plugin_name not in visited:
                temp_visited.add(plugin_name)
                plugin = self.plugins[plugin_name]
                for dep in plugin.get_dependencies():
                    if dep not in self.plugins:
                        raise ValueError(f"Plugin dependency not found: {dep}")
                    visit(dep)
                temp_visited.remove(plugin_name)
                visited.add(plugin_name)
                self.plugin_order.append(plugin_name)
        
        for plugin_name in self.plugins:
            if plugin_name not in visited:
                visit(plugin_name)
    
    def execute_plugins(self, ast: ASTNode, context: CompilerContext, messages: MessageCollector):
        """Execute all plugins in dependency order"""
        for plugin_name in self.plugin_order:
            plugin = self.plugins[plugin_name]
            try:
                messages.info(f"Executing plugin: {plugin_name}")
                result = plugin.execute(ast, context, messages)
                context.plugin_results[plugin_name] = result
                messages.info(f"Plugin {plugin_name} completed successfully")
            except Exception as e:
                messages.error(f"Plugin {plugin_name} failed: {str(e)}")
                raise


class PL0Compiler:
    """Main compiler class"""
    
    def __init__(self, output_dir: str = None):
        self.messages = MessageCollector()
        self.context = CompilerContext(output_dir)
        self.plugin_manager = PluginManager()
        
        # Register default plugins
        self._register_default_plugins()
    
    def _register_default_plugins(self):
        """Register default plugins"""
        self.plugin_manager.register_plugin(PythonCodeGenPlugin())
        self.plugin_manager.register_plugin(ASTVisualizerPlugin())
    
    def compile_file(self, filename: str, debug: bool = False) -> bool:
        """Compile a PL/0 source file"""
        try:
            self.messages.enable_debug(debug)
            self.messages.info(f"Compiling file: {filename}")
            self.context.set_source_info(filename)
            
            # Read source file
            with open(filename, 'r') as f:
                source_code = f.read()
            
            return self.compile_source(source_code, debug)
            
        except FileNotFoundError:
            self.messages.error(f"Source file not found: {filename}")
            return False
        except Exception as e:
            self.messages.error(f"Compilation failed: {str(e)}")
            return False
    
    def compile_source(self, source_code: str, debug: bool = False) -> bool:
        """Compile PL/0 source code"""
        try:
            self.messages.enable_debug(debug)
            self.messages.clear()
            
            # Lexical analysis
            self.messages.info("Starting lexical analysis...")
            lexer = Lexer(source_code, self.messages)
            
            # Parsing
            self.messages.info("Starting parsing...")
            parser = PackratParser(lexer.tokens, self.messages)
            ast = parser.parse()
            
            # Semantic analysis
            self.messages.info("Starting semantic analysis...")
            analyzer = SemanticAnalyzer(self.context, self.messages)
            analyzer.analyze(ast)
            
            if self.messages.has_errors():
                self.messages.error("Compilation failed due to errors")
                return False
            
            # Execute plugins
            self.messages.info("Executing plugins...")
            self.plugin_manager.execute_plugins(ast, self.context, self.messages)
            
            # Report generated files
            self._report_generated_files()
            
            self.messages.info("Compilation completed successfully!")
            return True
            
        except Exception as e:
            self.messages.error(f"Compilation failed: {str(e)}")
            return False
    
    def _report_generated_files(self):
        """Report all generated files"""
        files = self.context.get_generated_files()
        if files:
            self.messages.info("Generated files:")
            for plugin_name, file_list in files.items():
                for file_info in file_list:
                    desc = f" - {file_info['description']}" if file_info['description'] else ""
                    self.messages.info(f"  {file_info['filename']} (by {plugin_name}){desc}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PL/0 Compiler with Plugin System')
    parser.add_argument('input_file', help='PL/0 source file to compile')
    parser.add_argument('-o', '--output-dir', help='Output directory for generated files', default='.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--plugin', action='append', help='Load additional plugin from file')
    
    args = parser.parse_args()
    
    # Create compiler
    compiler = PL0Compiler(args.output_dir)
    
    # Load additional plugins if specified
    if args.plugin:
        for plugin_file in args.plugin:
            try:
                spec = importlib.util.spec_from_file_location("custom_plugin", plugin_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for plugin classes in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, Plugin) and 
                        attr != Plugin):
                        plugin_instance = attr()
                        compiler.plugin_manager.register_plugin(plugin_instance)
                        compiler.messages.info(f"Loaded plugin: {plugin_instance.name}")
                        
            except Exception as e:
                compiler.messages.error(f"Failed to load plugin {plugin_file}: {str(e)}")
    
    # Compile the file
    success = compiler.compile_file(args.input_file, args.debug)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
