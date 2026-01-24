#!/usr/bin/env python3
"""
A simple educational programming language compiler/interpreter.
Expression-based, statically typed, immutable-by-default.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from enum import Enum



# LEXER


class TokenType(Enum):
    # Keywords
    LET = "let"
    VAR = "var"
    FUN = "fun"
    CLASS = "class"
    IF = "if"
    THEN = "then"
    ELSE = "else"
    MATCH = "match"
    WHILE = "while"
    DO = "do"
    
    # Literals
    INT = "INT"
    BOOL = "BOOL"
    STRING = "STRING"
    
    # Identifiers and types
    ID = "ID"
    
    # Operators
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    EQ = "="
    EQEQ = "=="
    LT = "<"
    GT = ">"
    ARROW = "=>"
    RARROW = "->"
    
    # Delimiters
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    COMMA = ","
    COLON = ":"
    UNDERSCORE = "_"
    
    # Special
    EOF = "EOF"
    NEWLINE = "NEWLINE"


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
    def error(self, msg: str):
        raise SyntaxError(f"Lexer error at {self.line}:{self.column}: {msg}")
    
    def peek(self, offset=0):
        pos = self.pos + offset
        return self.source[pos] if pos < len(self.source) else None
    
    def advance(self):
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self):
        while self.peek() and self.peek() in ' \t\r\n':
            self.advance()
    
    def skip_comment(self):
        if self.peek() == '/' and self.peek(1) == '/':
            while self.peek() and self.peek() != '\n':
                self.advance()
    
    def read_number(self):
        start = self.pos
        while self.peek() and self.peek().isdigit():
            self.advance()
        return int(self.source[start:self.pos])
    
    def read_identifier(self):
        start = self.pos
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()
        return self.source[start:self.pos]
    
    def read_string(self):
        self.advance()  # skip opening quote
        start = self.pos
        while self.peek() and self.peek() != '"':
            self.advance()
        if not self.peek():
            self.error("Unterminated string")
        value = self.source[start:self.pos]
        self.advance()  # skip closing quote
        return value
    
    def tokenize(self):
        keywords = {
            "let", "var", "fun", "class", "if", "then", "else",
            "match", "while", "do", "true", "false"
        }
        
        while self.pos < len(self.source):
            self.skip_whitespace()
            self.skip_comment()
            
            if self.pos >= len(self.source):
                break
            
            line, col = self.line, self.column
            ch = self.peek()
            
            # Numbers
            if ch.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.INT, value, line, col))
            
            # Identifiers and keywords
            elif ch.isalpha() or ch == '_':
                value = self.read_identifier()
                if value in keywords:
                    if value == "true":
                        self.tokens.append(Token(TokenType.BOOL, True, line, col))
                    elif value == "false":
                        self.tokens.append(Token(TokenType.BOOL, False, line, col))
                    else:
                        self.tokens.append(Token(TokenType(value), value, line, col))
                else:
                    self.tokens.append(Token(TokenType.ID, value, line, col))
            
            # Strings
            elif ch == '"':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, line, col))
            
            # Operators and delimiters
            elif ch == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', line, col))
                self.advance()
            elif ch == '-':
                if self.peek(1) == '>':
                    self.tokens.append(Token(TokenType.RARROW, '->', line, col))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.MINUS, '-', line, col))
                    self.advance()
            elif ch == '*':
                self.tokens.append(Token(TokenType.STAR, '*', line, col))
                self.advance()
            elif ch == '/':
                self.tokens.append(Token(TokenType.SLASH, '/', line, col))
                self.advance()
            elif ch == '=':
                if self.peek(1) == '=':
                    self.tokens.append(Token(TokenType.EQEQ, '==', line, col))
                    self.advance()
                    self.advance()
                elif self.peek(1) == '>':
                    self.tokens.append(Token(TokenType.ARROW, '=>', line, col))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.EQ, '=', line, col))
                    self.advance()
            elif ch == '<':
                self.tokens.append(Token(TokenType.LT, '<', line, col))
                self.advance()
            elif ch == '>':
                self.tokens.append(Token(TokenType.GT, '>', line, col))
                self.advance()
            elif ch == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', line, col))
                self.advance()
            elif ch == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', line, col))
                self.advance()
            elif ch == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', line, col))
                self.advance()
            elif ch == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', line, col))
                self.advance()
            elif ch == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', line, col))
                self.advance()
            elif ch == ':':
                self.tokens.append(Token(TokenType.COLON, ':', line, col))
                self.advance()
            else:
                self.error(f"Unexpected character: {ch}")
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens



# AST NODES


@dataclass
class IntLiteral:
    value: int

@dataclass
class BoolLiteral:
    value: bool

@dataclass
class StringLiteral:
    value: str

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

@dataclass
class If:
    cond: Any
    then_expr: Any
    else_expr: Any

@dataclass
class Let:
    name: str
    type_annotation: Optional[str]
    value: Any
    mutable: bool = False

@dataclass
class Assign:
    name: str
    value: Any

@dataclass
class FunCall:
    func: str
    args: List[Any]

@dataclass
class FunDef:
    name: str
    params: List[tuple]  # [(name, type), ...]
    return_type: Optional[str]
    body: Any

@dataclass
class ClassDef:
    name: str
    params: List[tuple]  # [(name, type), ...]
    methods: List[FunDef]

@dataclass
class Constructor:
    class_name: str
    args: List[Any]

@dataclass
class MethodCall:
    obj: Any
    method: str
    args: List[Any]

@dataclass
class FieldAccess:
    obj: Any
    field: str

@dataclass
class Block:
    exprs: List[Any]

@dataclass
class While:
    cond: Any
    body: Any

@dataclass
class Program:
    declarations: List[Any]



# PARSER


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def error(self, msg: str):
        tok = self.current()
        raise SyntaxError(f"Parse error at {tok.line}:{tok.column}: {msg}")
    
    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]
    
    def peek(self, offset=0):
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else self.tokens[-1]
    
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def expect(self, token_type: TokenType):
        if self.current().type != token_type:
            self.error(f"Expected {token_type}, got {self.current().type}")
        tok = self.current()
        self.advance()
        return tok
    
    def parse_program(self):
        declarations = []
        while self.current().type != TokenType.EOF:
            declarations.append(self.parse_declaration())
        return Program(declarations)
    
    def parse_declaration(self):
        if self.current().type == TokenType.FUN:
            return self.parse_fun_def()
        elif self.current().type == TokenType.CLASS:
            return self.parse_class_def()
        else:
            return self.parse_expr()
    
    def parse_fun_def(self):
        self.expect(TokenType.FUN)
        name = self.expect(TokenType.ID).value
        self.expect(TokenType.LPAREN)
        
        params = []
        while self.current().type != TokenType.RPAREN:
            param_name = self.expect(TokenType.ID).value
            self.expect(TokenType.COLON)
            param_type = self.expect(TokenType.ID).value
            params.append((param_name, param_type))
            if self.current().type == TokenType.COMMA:
                self.advance()
        
        self.expect(TokenType.RPAREN)
        
        return_type = None
        if self.current().type == TokenType.COLON:
            self.advance()
            return_type = self.expect(TokenType.ID).value
        
        self.expect(TokenType.EQ)
        body = self.parse_expr()
        
        return FunDef(name, params, return_type, body)
    
    def parse_class_def(self):
        self.expect(TokenType.CLASS)
        name = self.expect(TokenType.ID).value
        self.expect(TokenType.LPAREN)
        
        params = []
        while self.current().type != TokenType.RPAREN:
            param_name = self.expect(TokenType.ID).value
            self.expect(TokenType.COLON)
            param_type = self.expect(TokenType.ID).value
            params.append((param_name, param_type))
            if self.current().type == TokenType.COMMA:
                self.advance()
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        
        methods = []
        while self.current().type == TokenType.FUN:
            methods.append(self.parse_fun_def())
        
        self.expect(TokenType.RBRACE)
        
        return ClassDef(name, params, methods)
    
    def parse_expr(self):
        if self.current().type == TokenType.LET:
            return self.parse_let()
        elif self.current().type == TokenType.VAR:
            return self.parse_var()
        elif self.current().type == TokenType.IF:
            return self.parse_if()
        elif self.current().type == TokenType.WHILE:
            return self.parse_while()
        else:
            return self.parse_assign()
    
    def parse_let(self):
        self.expect(TokenType.LET)
        name = self.expect(TokenType.ID).value
        
        type_annotation = None
        if self.current().type == TokenType.COLON:
            self.advance()
            type_annotation = self.expect(TokenType.ID).value
        
        self.expect(TokenType.EQ)
        value = self.parse_expr()
        
        return Let(name, type_annotation, value, mutable=False)
    
    def parse_var(self):
        self.expect(TokenType.VAR)
        name = self.expect(TokenType.ID).value
        
        type_annotation = None
        if self.current().type == TokenType.COLON:
            self.advance()
            type_annotation = self.expect(TokenType.ID).value
        
        self.expect(TokenType.EQ)
        value = self.parse_expr()
        
        return Let(name, type_annotation, value, mutable=True)
    
    def parse_if(self):
        self.expect(TokenType.IF)
        cond = self.parse_expr()
        self.expect(TokenType.THEN)
        then_expr = self.parse_expr()
        self.expect(TokenType.ELSE)
        else_expr = self.parse_expr()
        
        return If(cond, then_expr, else_expr)
    
    def parse_while(self):
        self.expect(TokenType.WHILE)
        cond = self.parse_expr()
        self.expect(TokenType.DO)
        body = self.parse_expr()
        
        return While(cond, body)
    
    def parse_assign(self):
        expr = self.parse_logic()
        
        if self.current().type == TokenType.EQ:
            if not isinstance(expr, Var):
                self.error("Can only assign to variables")
            self.advance()
            value = self.parse_expr()
            return Assign(expr.name, value)
        
        return expr
    
    def parse_logic(self):
        left = self.parse_arith()
        
        while self.current().type in [TokenType.EQEQ, TokenType.LT, TokenType.GT]:
            op = self.current().value
            self.advance()
            right = self.parse_arith()
            left = BinOp(op, left, right)
        
        return left
    
    def parse_arith(self):
        left = self.parse_term()
        
        while self.current().type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current().value
            self.advance()
            right = self.parse_term()
            left = BinOp(op, left, right)
        
        return left
    
    def parse_term(self):
        left = self.parse_factor()
        
        while self.current().type in [TokenType.STAR, TokenType.SLASH]:
            op = self.current().value
            self.advance()
            right = self.parse_factor()
            left = BinOp(op, left, right)
        
        return left
    
    def parse_factor(self):
        tok = self.current()
        
        if tok.type == TokenType.INT:
            self.advance()
            return IntLiteral(tok.value)
        
        elif tok.type == TokenType.BOOL:
            self.advance()
            return BoolLiteral(tok.value)
        
        elif tok.type == TokenType.STRING:
            self.advance()
            return StringLiteral(tok.value)
        
        elif tok.type == TokenType.ID:
            name = tok.value
            self.advance()
            
            # Function call or constructor
            if self.current().type == TokenType.LPAREN:
                self.advance()
                args = []
                while self.current().type != TokenType.RPAREN:
                    args.append(self.parse_expr())
                    if self.current().type == TokenType.COMMA:
                        self.advance()
                self.expect(TokenType.RPAREN)
                
                # Check if it's a class name (uppercase)
                if name[0].isupper():
                    return Constructor(name, args)
                else:
                    return FunCall(name, args)
            
            # Check for method call (dot notation)
            elif self.current().type == TokenType.ID and self.peek(-2).type == TokenType.ID:
                # This is obj.method() syntax - handled differently
                return Var(name)
            
            return Var(name)
        
        elif tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TokenType.RPAREN)
            
            # Check for method call after closing paren
            if self.current().type == TokenType.ID:
                method = self.current().value
                self.advance()
                if self.current().type == TokenType.LPAREN:
                    self.advance()
                    args = []
                    while self.current().type != TokenType.RPAREN:
                        args.append(self.parse_expr())
                        if self.current().type == TokenType.COMMA:
                            self.advance()
                    self.expect(TokenType.RPAREN)
                    return MethodCall(expr, method, args)
            
            return expr
        
        else:
            self.error(f"Unexpected token: {tok.type}")



# TYPE CHECKER


class TypeChecker:
    def __init__(self):
        self.env = {}
        self.mutable_vars = set()  # Track which variables are mutable
        self.functions = {}
        self.classes = {}
    
    def error(self, msg: str):
        raise TypeError(f"Type error: {msg}")
    
    def check_program(self, program: Program):
        for decl in program.declarations:
            if isinstance(decl, FunDef):
                self.functions[decl.name] = decl
            elif isinstance(decl, ClassDef):
                self.classes[decl.name] = decl
                # Register methods - they'll be looked up through the class
            else:
                self.check(decl)
    
    def check(self, expr, env=None):
        if env is None:
            env = self.env.copy()
        
        if isinstance(expr, IntLiteral):
            return "Int"
        
        elif isinstance(expr, BoolLiteral):
            return "Bool"
        
        elif isinstance(expr, StringLiteral):
            return "String"
        
        elif isinstance(expr, Var):
            if expr.name not in env:
                self.error(f"Undefined variable: {expr.name}")
            return env[expr.name]
        
        elif isinstance(expr, BinOp):
            left_type = self.check(expr.left, env)
            right_type = self.check(expr.right, env)
            
            if expr.op in ['+', '-', '*', '/']:
                if left_type != "Int" or right_type != "Int":
                    self.error(f"Arithmetic requires Int, got {left_type} and {right_type}")
                return "Int"
            
            elif expr.op in ['==', '<', '>']:
                if left_type != right_type:
                    self.error(f"Comparison requires same types, got {left_type} and {right_type}")
                return "Bool"
        
        elif isinstance(expr, If):
            cond_type = self.check(expr.cond, env)
            if cond_type != "Bool":
                self.error(f"If condition must be Bool, got {cond_type}")
            
            then_type = self.check(expr.then_expr, env)
            else_type = self.check(expr.else_expr, env)
            
            if then_type != else_type:
                self.error(f"If branches must have same type, got {then_type} and {else_type}")
            
            return then_type
        
        elif isinstance(expr, Let):
            value_type = self.check(expr.value, env)
            
            if expr.type_annotation and expr.type_annotation != value_type:
                self.error(f"Type annotation mismatch: expected {expr.type_annotation}, got {value_type}")
            
            new_env = env.copy()
            new_env[expr.name] = value_type
            self.env[expr.name] = value_type
            
            # Track mutable variables
            if expr.mutable:
                self.mutable_vars.add(expr.name)
            
            return "Unit"
        
        elif isinstance(expr, Assign):
            if expr.name not in env:
                self.error(f"Undefined variable: {expr.name}")
            
            # Check if variable is mutable
            if expr.name not in self.mutable_vars:
                self.error(f"Cannot assign to immutable variable: {expr.name}")
            
            value_type = self.check(expr.value, env)
            var_type = env[expr.name]
            
            if value_type != var_type:
                self.error(f"Assignment type mismatch: expected {var_type}, got {value_type}")
            
            return "Unit"
        
        elif isinstance(expr, FunCall):
            # Check if this might be a method call on an object
            # Methods are called like: methodName(object, args...)
            if expr.func not in self.functions:
                # Try to find it as a method in any class
                for class_name, class_def in self.classes.items():
                    for method in class_def.methods:
                        if method.name == expr.func:
                            # Found the method
                            # First arg should be an object of this class
                            if len(expr.args) == 0:
                                self.error(f"Method {expr.func} requires an object as first argument")
                            
                            first_arg_type = self.check(expr.args[0], env)
                            if first_arg_type != class_name:
                                self.error(f"Method {expr.func} expects {class_name} as first argument, got {first_arg_type}")
                            
                            # Check remaining arguments match method parameters
                            if len(expr.args) - 1 != len(method.params):
                                self.error(f"Method {expr.func} expects {len(method.params)} arguments, got {len(expr.args) - 1}")
                            
                            for arg, (param_name, param_type) in zip(expr.args[1:], method.params):
                                arg_type = self.check(arg, env)
                                if arg_type != param_type:
                                    self.error(f"Argument type mismatch: expected {param_type}, got {arg_type}")
                            
                            # Return type is inferred from method body with class fields in scope
                            method_env = env.copy()
                            for (field_name, field_type) in class_def.params:
                                method_env[field_name] = field_type
                            for (param_name, param_type) in method.params:
                                method_env[param_name] = param_type
                            
                            if method.return_type:
                                return method.return_type
                            else:
                                return self.check(method.body, method_env)
                
                self.error(f"Undefined function: {expr.func}")
            
            func_def = self.functions[expr.func]
            
            if len(expr.args) != len(func_def.params):
                self.error(f"Function {expr.func} expects {len(func_def.params)} arguments, got {len(expr.args)}")
            
            for arg, (param_name, param_type) in zip(expr.args, func_def.params):
                arg_type = self.check(arg, env)
                if arg_type != param_type:
                    self.error(f"Argument type mismatch: expected {param_type}, got {arg_type}")
            
            if func_def.return_type:
                return func_def.return_type
            else:
                # Infer return type
                func_env = env.copy()
                for (param_name, param_type) in func_def.params:
                    func_env[param_name] = param_type
                return self.check(func_def.body, func_env)
        
        elif isinstance(expr, Constructor):
            if expr.class_name not in self.classes:
                self.error(f"Undefined class: {expr.class_name}")
            
            return expr.class_name
        
        elif isinstance(expr, While):
            cond_type = self.check(expr.cond, env)
            if cond_type != "Bool":
                self.error(f"While condition must be Bool, got {cond_type}")
            
            self.check(expr.body, env)
            return "Unit"
        
        return "Unit"



# INTERPRETER


@dataclass
class ObjectInstance:
    class_name: str
    fields: Dict[str, Any]

class Interpreter:
    def __init__(self):
        self.env = {}
        self.functions = {}
        self.classes = {}
    
    def error(self, msg: str):
        raise RuntimeError(f"Runtime error: {msg}")
    
    def run_program(self, program: Program):
        result = None
        for decl in program.declarations:
            if isinstance(decl, FunDef):
                self.functions[decl.name] = decl
            elif isinstance(decl, ClassDef):
                self.classes[decl.name] = decl
            else:
                result = self.eval(decl)
        return result
    
    def eval(self, expr, env=None):
        if env is None:
            env = self.env
        
        if isinstance(expr, IntLiteral):
            return expr.value
        
        elif isinstance(expr, BoolLiteral):
            return expr.value
        
        elif isinstance(expr, StringLiteral):
            return expr.value
        
        elif isinstance(expr, Var):
            if expr.name not in env:
                self.error(f"Undefined variable: {expr.name}")
            return env[expr.name]
        
        elif isinstance(expr, BinOp):
            left = self.eval(expr.left, env)
            right = self.eval(expr.right, env)
            
            if expr.op == '+':
                return left + right
            elif expr.op == '-':
                return left - right
            elif expr.op == '*':
                return left * right
            elif expr.op == '/':
                return left // right
            elif expr.op == '==':
                return left == right
            elif expr.op == '<':
                return left < right
            elif expr.op == '>':
                return left > right
        
        elif isinstance(expr, If):
            cond = self.eval(expr.cond, env)
            if cond:
                return self.eval(expr.then_expr, env)
            else:
                return self.eval(expr.else_expr, env)
        
        elif isinstance(expr, Let):
            value = self.eval(expr.value, env)
            env[expr.name] = value
            self.env[expr.name] = value
            return None  # Unit
        
        elif isinstance(expr, Assign):
            value = self.eval(expr.value, env)
            if expr.name not in env:
                self.error(f"Undefined variable: {expr.name}")
            env[expr.name] = value
            if expr.name in self.env:
                self.env[expr.name] = value
            return None  # Unit
        
        elif isinstance(expr, FunCall):
            # First check if it's a regular function
            if expr.func in self.functions:
                func_def = self.functions[expr.func]
                args = [self.eval(arg, env) for arg in expr.args]
                
                # Build function environment with parameters
                func_env = {}
                for (param_name, _), arg_value in zip(func_def.params, args):
                    func_env[param_name] = arg_value
                
                return self.eval(func_def.body, func_env)
            
            # Otherwise, try to find it as a method
            for class_name, class_def in self.classes.items():
                for method in class_def.methods:
                    if method.name == expr.func:
                        # Found the method - first arg should be the object
                        if len(expr.args) == 0:
                            self.error(f"Method {expr.func} requires an object as first argument")
                        
                        obj_arg = self.eval(expr.args[0], env)
                        if not isinstance(obj_arg, ObjectInstance) or obj_arg.class_name != class_name:
                            self.error(f"Method {expr.func} expects {class_name} object as first argument")
                        
                        # Evaluate remaining arguments
                        args = [self.eval(arg, env) for arg in expr.args[1:]]
                        
                        # Build method environment with object fields + parameters
                        method_env = {}
                        # Add object fields
                        for field_name, field_value in obj_arg.fields.items():
                            method_env[field_name] = field_value
                        # Add parameters
                        for (param_name, _), arg_value in zip(method.params, args):
                            method_env[param_name] = arg_value
                        
                        return self.eval(method.body, method_env)
            
            self.error(f"Undefined function: {expr.func}")
        
        elif isinstance(expr, Constructor):
            if expr.class_name not in self.classes:
                self.error(f"Undefined class: {expr.class_name}")
            
            class_def = self.classes[expr.class_name]
            args = [self.eval(arg, env) for arg in expr.args]
            
            fields = {}
            for (param_name, _), arg_value in zip(class_def.params, args):
                fields[param_name] = arg_value
            
            return ObjectInstance(expr.class_name, fields)
        
        elif isinstance(expr, While):
            while self.eval(expr.cond, env):
                self.eval(expr.body, env)
            return None  # Unit
        
        return None



# REPL


def main():
    print("Educational Language Interpreter v0.1")
    print("Type 'exit' to quit\n")
    
    interpreter = Interpreter()
    type_checker = TypeChecker()
    
    # Example programs
    examples = """
Examples to try:

1. Simple arithmetic:
   let x = 10
   let y = x + 5

2. Function:
   fun add(x: Int, y: Int): Int = x + y
   add(3, 4)

3. If expression:
   let x = 10
   if x > 5 then x * 2 else 0

4. Class:
   class Point(x: Int, y: Int) {
       fun move(dx: Int, dy: Int) = Point(x + dx, y + dy)
   }
   Point(10, 20)

5. Mutable variable:
   var counter = 0
   counter = counter + 1
"""
    
    print(examples)
    
    while True:
        try:
            source = input("> ")
            if source.strip() == 'exit':
                break
            
            if not source.strip():
                continue
            
            # Lexer
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            # Parser
            parser = Parser(tokens)
            ast = parser.parse_program()
            
            # Type check
            type_checker.check_program(ast)
            
            # Interpret
            result = interpreter.run_program(ast)
            
            if result is not None:
                print(f"{result}")
            
        except (SyntaxError, TypeError, RuntimeError) as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nBye!")
            break


if __name__ == "__main__":
    main()
